from agents.coordinatoragent import CoordinatorAgent
from db.db import db

db.connect()

# Get a new lead (status = 'new')
leads = db.execute_query("SELECT * FROM leads LIMIT 1")

if leads:
    lead = leads[0]
    
    print(f"\n🧪 Testing Coordinator Agent")
    print(f"Lead: {lead['contact_name']} at {lead['company_name']}\n")
    
    coordinator = CoordinatorAgent()
    results = coordinator.execute(lead, db)
    
    print(f"\n📊 RESULTS:")
    print(f"Status: {results['status']}")
    print(f"Steps completed: {', '.join(results['steps_completed'])}")
    print(f"Signals found: {len(results['signals'])}")
    
    if results['outreach']:
        print(f"Personalization score: {results['outreach'].get('personalization_score')}/10")
    
    if results['errors']:
        print(f"Errors: {results['errors']}")
    
else:
    print("No new leads found. Create a lead first!")

db.disconnect()