from .base_agent import BaseAgent
from .researchagent import ResearchAgent
from .signalagent import SignalAgent
from .writeragent import WriterAgent    
from typing import Dict, Any
from datetime import datetime

class CoordinatorAgent(BaseAgent):
    #agent that coordinates the workflow between research, signal, and writer agents

    def __init__(self):
        super().__init__(
            name="CoordinatorAgent", 
            role="Workflow orchestrator who manages the entire sales automation pipeline", 
            temperature=0.3
        )

        self.research_agent = ResearchAgent()
        self.signal_agent = SignalAgent()
        self.writer_agent = WriterAgent()

    def execute(self, lead_data: Dict[str, Any], db_instance) -> Dict[str, Any]:
        #orchestrates the workflow for a given lead

        lead_id = lead_data['id']
        company_name = lead_data['company_name']
        
        print(f"CoordinatorAgent: Starting full analysis for {company_name}")

        results = {
            "status": "in_progress",
            "steps_completed": [],
            "research": None,
            "signals": [],
            "outreach": None,
            "errors": []
        }
        saved_signals = []

        try:
            print("CoordinatorAgent: Running ResearchAgent...")
            db_instance.update_lead_status(lead_id, "researching")

            profile = self.research_agent.execute(lead_data)
            saved_profile = db_instance.save_lead_profile(lead_id, profile)

            results["research"] = saved_profile
            results["steps_completed"].append("research")
            print("CoordinatorAgent: ResearchAgent completed.")
        except Exception as e:
            error_msg = f"ResearchAgent error: {e}"
            print(f"CoordinatorAgent: {error_msg}")
            results["errors"].append(error_msg)
            db_instance.update_lead_status(lead_id, "new")
            results["status"] = "partial_failure"
            return results
        

        try: 
            print("CoordinatorAgent: Running SignalAgent...")

            signals = self.signal_agent.execute(lead_data)


            for signal in signals:
                saved_signal = db_instance.create_signal(
                    lead_id=lead_id,
                    signal_type=signal['signal_type'],
                    signal_data=signal['signal_data'],
                    urgency_score=signal.get('urgency_score'))
                saved_signals.append(saved_signal)

            results["signals"] = saved_signals
            results["steps_completed"].append("signals")
            print("CoordinatorAgent: SignalAgent completed.")
        except Exception as e:
            print(f"⚠️  Signal detection failed: {e}")
            results["errors"].append(f"Signal error: {str(e)}")

        try:
            print("CoordinatorAgent: Running WriterAgent...")
            
            profile_query = "SELECT * FROM lead_profiles WHERE lead_id = %s ORDER BY created_at DESC LIMIT 1"
            profiles = db_instance.execute_query(profile_query, (lead_id,))
            profile_data = profiles[0] if profiles else profile

            outreach = self.writer_agent.execute(
                lead_data,
                profile_data,
                saved_signals if saved_signals else None
            )

            saved_outreach = db_instance.save_outreach(
                lead_id,
                subject=outreach['subject'],
                body=outreach['body'],
                message_type=outreach['message_type']
            )

            results["outreach"] = saved_outreach
            results["outreach"]["personalization_score"] = outreach.get("personalization_score", 0)
            results["steps_completed"].append("outreach")
            print("CoordinatorAgent: WriterAgent completed.")
        
        except Exception as e:
            print(f"❌ Outreach generation failed: {e}\n")
            results["errors"].append(f"Outreach error: {str(e)}")
            results["status"] = "partial_failure"
            db_instance.update_lead_status(lead_id, "ready")
            return results
        
        db_instance.update_lead_status(lead_id, "ready")

        results["status"] = "success"
        print(f"✅ CoordinatorAgent: Full analysis complete for {company_name}")

        return results