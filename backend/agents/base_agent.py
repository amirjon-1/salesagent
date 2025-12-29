from google import genai
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import time
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db.db import db

load_dotenv()

class BaseAgent:
    #parent class for all agents
    #handles common functionality like logging interactions to the database

    def __init__(self, name: str, role: str, temperature: float = 0.7):
        #agent identity and behavior settings
        self.name = name
        self.role = role
        self.temperature = temperature

        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model_name = "gemini-2.5-flash"


    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        #each agent must implement its own execute method
        raise NotImplementedError("each agent must implement execute()")

    def call_llm(self, prompt: str, lead_id: str = None) -> str:
        #calls the LLM with the given prompt and returns the response text

        full_prompt = f"""You are {self.name}, a specialized AI agent.
        Your role: {self.role}
        {prompt}"""

        start_time = time.time()

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    "temperature": self.temperature,
                    "max_output_tokens": 8000
                }
            )
            
            duration = int((time.time() - start_time) * 1000)

            db.log_agent(
                agent_name=self.name,
                action="call_llm",
                lead_id=lead_id,
                input_data={"prompt": prompt[:200]},
                output_data={"response": response.text[:200]},
                duration_ms=duration,
                success=True
            )

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {self.name} - LLM call ({duration}ms)")
            return response.text
        
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)

            db.log_agent(
                agent_name=self.name,
                action="call_llm",
                lead_id=lead_id,
                input_data={"prompt": prompt[:200]},
                output_data=None,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
            print("error calling LLM:", e)
            raise 
    
    def call_llm_json(self, prompt: str, lead_id: str = None) -> Dict:
        #calls the LLM and expects a JSON response
        json_prompt = f"""{prompt}
        CRITICAL: You MUST return ONLY valid JSON. No markdown code blocks, no explanations, just pure JSON.
        Your response should start with {{ and end with }}."""
        
        response_text = self.call_llm(json_prompt, lead_id=lead_id)

        try:
            cleaned = response_text.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print("error parsing JSON from LLM response:", e)
            db.log_agent(
                agent_name=self.name,
                action="parse_llm_json_fail",
                lead_id=lead_id,
                input_data={"response_text": response_text[:200]},
                output_data={"raw_response": response_text[:500]},
                success=False,
                error_message=f"JSON parse error: {str(e)}"
            )

            return {
                "error": "json_parse_error",
                "raw_response": response_text,
                "agent": self.name,
                "parse_error": str(e)
            }



