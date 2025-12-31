from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from db.db import db
from agents.researchagent import ResearchAgent
from agents.signalagent import SignalAgent
from agents.writeragent import WriterAgent
from agents.coordinatoragent import CoordinatorAgent

app = FastAPI(
    title="Sales Agents API",
    description="AI agents that automate sales research and outreach",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.connect()
    print("Server started and database connected.")

@app.on_event("shutdown")
def shutdown():
    db.disconnect()
    print("Server shutting down and database disconnected.")

#request
class CreateLeadRequest(BaseModel):
    company_name: str
    contact_name: str
    contact_email: Optional[str] = None
    contact_linkedin: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None

#response format
class LeadResponse(BaseModel):
    id: str
    company_name: str
    contact_name: str
    contact_email: Optional[str]
    contact_linkedin: Optional[str]
    title: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    status: str
    created_at: str
    updated_at: str


@app.get("/")
def root():
    #health check
    return {
        "status": "healthy",
        "message": "Sales Agent System API is running",
        "version": "1.0.0"
    }

@app.post("/leads", response_model=LeadResponse)
def create_lead(lead: CreateLeadRequest):
    #endpoint to create a new lead
    try:
        created = db.create_lead(
            company_name=lead.company_name,
            contact_name=lead.contact_name,
            contact_email=lead.contact_email,
            contact_linkedin=lead.contact_linkedin,
            title=lead.title,
            industry=lead.industry,
            company_size=lead.company_size
        )
        return {
            "id": str(created["id"]),
            "company_name": created["company_name"],
            "contact_name": created["contact_name"],
            "contact_email": created.get("contact_email"),
            "contact_linkedin": created.get("contact_linkedin"),
            "title": created.get("title"),
            "industry": created.get("industry"),
            "company_size": created.get("company_size"),
            "status": created["status"],
            "created_at": str(created["created_at"]),
            "updated_at": str(created["updated_at"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")

@app.get("/leads", response_model=List[LeadResponse])
def get_all_leads():
    #gets all leads
    try:
        query = "SELECT * FROM leads ORDER BY created_at DESC"
        leads = db.execute_query(query, ())
        return [{
            "id": str(lead["id"]),
            "company_name": lead["company_name"],
            "contact_name": lead["contact_name"],
            "contact_email": lead.get("contact_email"),
            "contact_linkedin": lead.get("contact_linkedin"),
            "title": lead.get("title"),
            "industry": lead.get("industry"),
            "company_size": lead.get("company_size"),
            "status": lead["status"],
            "created_at": str(lead["created_at"]),
            "updated_at": str(lead["updated_at"])
        } for lead in leads]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve leads: {str(e)}")
    

@app.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    #gets a lead by ID
    try:
        lead = db.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        profile_query = "SELECT * FROM lead_profiles WHERE lead_id = %s"
        profiles = db.execute_query(profile_query, (lead_id,))
        profile = profiles[0] if profiles else None
        return {
            "lead": {
                "id": str(lead["id"]),
                "company_name": lead["company_name"],
                "contact_name": lead["contact_name"],
                "contact_email": lead.get("contact_email"),
                "contact_linkedin": lead.get("contact_linkedin"),
                "title": lead.get("title"),
                "industry": lead.get("industry"),
                "company_size": lead.get("company_size"),
                "status": lead["status"],
                "created_at": str(lead["created_at"]),
                "updated_at": str(lead["updated_at"])
            },
            "profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve lead: {str(e)}")
    
@app.post("/leads/{lead_id}/research")
def research_lead(lead_id: str):
    #endpoint to run research agent on a lead
    try:
        lead = db.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        db.update_lead_status(lead_id, "researching")

        agent = ResearchAgent()
        profile = agent.execute(lead)

        saved = db.save_lead_profile(lead_id, profile)

        db.update_lead_status(lead_id, "ready")

        return {
            "status": "success",
            "message": "Research completed",
            "lead_id": lead_id,
            "profile": saved
        }
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.update_lead_status(lead_id, "new")
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")
    
@app.get("/leads/{lead_id}/activity")
def get_lead_activity(lead_id: str):
    #gets activity logs for a lead
    try:
        query = "SELECT * FROM agent_activity WHERE lead_id = %s ORDER BY created_at DESC"
        
        logs = db.execute_query(query, (lead_id,))
        return {
            "lead_id": lead_id,
            "activities": logs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve activity logs: {str(e)}")
    
@app.get("/activity")
def get_all_activity():
    #gets all activity logs
    try:
        query = "SELECT * FROM agent_activity ORDER BY created_at DESC LIMIT 50"
        
        logs = db.execute_query(query, ())
        return {
            "activities": logs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve activity logs: {str(e)}")
    

@app.post("/leads/{lead_id}/detect-signals")
def detect_signals(lead_id: str):
    #endpoint to run signal detection agent on a lead
    try:
        lead = db.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        agent = SignalAgent()
        signals = agent.execute(lead)

        saved_signals = []
        for signal in signals:
            saved = db.create_signal(
                lead_id=lead_id,
                signal_type=signal["signal_type"],
                signal_data=signal["signal_data"],
                urgency_score=signal["urgency_score"]
            )
            saved_signals.append(saved)

        return {
            "status": "success",
            "lead_id": lead_id,
            "signals_detected": len(saved_signals),
            "detected_signals": saved_signals
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signal detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/leads/{lead_id}/generate-outreach")
def generate_outreach(lead_id: str):
    
    #endpoint to run writer agent on a lead
    try:
        lead = db.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        profile_query = "SELECT * FROM lead_profiles WHERE lead_id = %s ORDER BY created_at DESC LIMIT 1"
        profiles = db.execute_query(profile_query, (lead_id,))

        if not profiles:
            raise HTTPException(status_code=400, detail="No research profile found. Run research first.")
        
        profile = profiles[0]

        signals_query = "SELECT * FROM signals WHERE lead_id = %s ORDER BY urgency_score DESC"
        signals = db.execute_query(signals_query, (lead_id,))

        print("Generating outreach using WriterAgent...")

        agent = WriterAgent()
        outreach = agent.execute(
            lead_data=lead,
            profile_data=profile,
            signals=signals if signals else None
        )
        saved = db.save_outreach(
            lead_id=lead_id,
            subject=outreach['subject'],
            body=outreach['body'],
            message_type=outreach['message_type']
        )

        return {
            "status": "success",
            "lead_id": lead_id,
            "outreach": saved,
            "personalization_score": outreach['personalization_score']
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Outreach generation failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/leads/{lead_id}/outreach")
def get_outreach(lead_id: str):
    #gets outreach messages for a lead
    try:
        query = "SELECT * FROM outreach WHERE lead_id = %s ORDER BY created_at DESC"
        
        messages = db.execute_query(query, (lead_id,))

        return {
            "lead_id": lead_id,
            "outreach_count": len(messages),
            "messages": messages
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve outreach messages: {str(e)}")

@app.post("/leads/{lead_id}/full-analysis")
def run_full_analysis(lead_id: str):
    #endpoint to run full analysis (research, signal detection, outreach) on a lead
    try:
        lead = db.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        agent = CoordinatorAgent()
        results = agent.execute(lead, db)

        personalization_score = 0
        if results.get("outreach"):
            personalization_score = results["outreach"].get("personalization_score", 0)

        return {
            "status": results["status"],
            "lead_id": lead_id,
            "steps_completed": results["steps_completed"],
            "research_completed": "research" in results["steps_completed"],
            "signals_detected": len(results.get("signals", [])),
            "outreach_generated": "outreach" in results["steps_completed"],
            "personalization_score": personalization_score,
            "errors": results.get("errors", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Full analysis failed: {e}")
        print(f"❌ Full analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

