"""
Test script for Research Agent
Creates a test lead and runs research on it
"""

from agents.researchagent import ResearchAgent
from db.db import db
import json

def test_research_agent():
    """
    Test the research agent with a real lead
    """
    print("=" * 60)
    print("TESTING RESEARCH AGENT")
    print("=" * 60)
    
    # Connect to database
    db.connect()
    
    # Create a test lead
    print("\n📝 Creating test lead...")
    lead = db.create_lead(
        company_name="Stripe",
        contact_name="Patrick Collison",
        contact_email="patrick@stripe.com",
        title="CEO",
        industry="FinTech",
        company_size="1000+",
        status="new"
    )
    
    print(f"✅ Created lead: {lead['id']}")
    print(f"   Company: {lead['company_name']}")
    print(f"   Contact: {lead['contact_name']}")
    
    # Initialize research agent
    agent = ResearchAgent()
    
    # Run research
    profile = agent.execute(lead)
    
    # Save profile to database
    print("\n💾 Saving profile to database...")
    saved_profile = db.save_lead_profile(lead['id'], profile)
    
    print(f"✅ Profile saved with ID: {saved_profile['id']}")
    
    # Update lead status
    db.update_lead_status(lead['id'], 'researching')
    
    # Print results
    print("\n" + "=" * 60)
    print("RESEARCH RESULTS")
    print("=" * 60)
    print(json.dumps(profile, indent=2))
    
    # Disconnect
    db.disconnect()
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_research_agent()