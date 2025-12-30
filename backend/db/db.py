import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class Database:
    #connection pool, database operations

    def __init__(self):
        #retrieve connection string from environment variable
        self.connection_string = os.getenv("DATABASE_URL", "postgresql://localhost:5432/sales_agents")
        self.conn = None

    def connect(self):
        #connects to database, but gets return values as a dict 
        try: 
            self.conn = psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)
            print("Database connection established.")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        #closes connection
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        #SELECT queries, return results as a list of dicts.
        if not self.conn:
            self.connect()

        try: 
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    def execute_mutation(self, query: str, params: tuple = None) -> Optional[Dict]:
        #INSERT/UPDATE/DELETE queries, return single result as a dict if applicable.
        if not self.conn:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)

            result = cursor.fetchone() if cursor.description else None

            self.conn.commit()
            cursor.close()
            return result
        except Exception as e:
            self.conn.rollback()
            print("mutation error:", e)
            raise   

    def create_lead(self, company_name: str, contact_name: str, contact_email: str = None, **kwargs) -> Dict:
        #creates a new lead in the database

        query = """
            INSERT INTO leads (company_name, contact_name, contact_email, title, contact_linkedin, industry, company_size, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """
        params = (
            company_name,
            contact_name,
            contact_email,
            kwargs.get("title"),
            kwargs.get("contact_linkedin"),
            kwargs.get("industry"),
            kwargs.get("company_size"),
            kwargs.get("status", "new") #default status is 'new'
        )

        return self.execute_mutation(query, params)
    
    def get_lead(self, lead_id: str) -> Optional[Dict]:
        #retrieves a lead by its ID

        query = "SELECT * FROM leads WHERE id = %s"
        params = (lead_id,)

        results = self.execute_query(query, params)
        return results[0] if results else None

    def get_leads_status(self, status: str) -> List[Dict]:
        #retrieves leads by their status

        query = "SELECT * FROM leads WHERE status = %s ORDER BY created_at DESC"
        params = (status,)

        return self.execute_query(query, params)
    
    def update_lead_status(self, lead_id: str, new_status: str) -> Dict:
        #updates the status of a lead

        query = "UPDATE leads SET status = %s, updated_at = NOW() WHERE id = %s RETURNING *"
        params = (new_status, lead_id)

        return self.execute_mutation(query, params)
    
    def save_lead_profile(self, lead_id: str, profile_data: Dict) -> Dict:
        #Save research profile for a lead

        query = """
            INSERT INTO lead_profiles (
                lead_id, company_description, tech_stack, recent_news, pain_points,
                competitors, funding_stage, likely_challenges,
                contact_background, communication_style, contact_cares_about,
                research_completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING *
        """

        params = (
            lead_id,
            profile_data.get("company_description"),
            json.dumps(profile_data.get("tech_stack", {})),
            json.dumps(profile_data.get("recent_news", [])),
            json.dumps(profile_data.get("pain_points", [])),
            json.dumps(profile_data.get('competitors', [])),
            profile_data.get('funding_stage'),  
            json.dumps(profile_data.get('likely_challenges', [])),  
            profile_data.get('contact_background'),  
            profile_data.get('communication_style'),  
            json.dumps(profile_data.get('contact_cares_about', [])) 
        )

        return self.execute_mutation(query, params)
    

    def create_signal(self, lead_id: str, signal_type: str, signal_data: Dict, urgency_score: int) -> Dict:
        #creates a new signal for a lead

        query = """
            INSERT INTO signals (lead_id, signal_type, signal_data, urgency_score)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """

        params = (
            lead_id,
            signal_type,
            json.dumps(signal_data),
            urgency_score
        )

        return self.execute_mutation(query, params)
    
    def save_outreach(self, lead_id: str, subject: str, body: str, message_type: str = 'email') -> Dict:
        #saves an outreach message for a lead

        query = """
            INSERT INTO outreach (lead_id, subject, body, message_type, status)
            VALUES (%s, %s, %s, %s, 'draft')
            RETURNING *
        """

        params = (
            lead_id,
            subject,
            body,
            message_type
        )

        return self.execute_mutation(query, params)

    def log_agent(self, agent_name: str, action: str, lead_id: str = None, input_data: Dict = None, output_data: Dict = None, duration_ms: int = None, success: bool = True, error_message: str = None):
        #logs an agent action

        query = """
            INSERT INTO agent_activity (
                agent_name, action, lead_id, input_data, output_data, 
                duration_ms, success, error_message
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            agent_name,
            action,
            lead_id,
            json.dumps(input_data) if input_data else None,
            json.dumps(output_data) if output_data else None,
            duration_ms,
            success,
            error_message
        )

        self.execute_mutation(query, params)

db = Database()