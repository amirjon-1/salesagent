from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime

class ResearchAgent(BaseAgent):
    #agent specialized in conducting research tasks

    def __init__(self):
        super().__init__(name="ResearchAgent", role="Deep research specialist who builds comprehensive lead profiles", temperature=0.3)
    
    def execute(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        #executes research on a lead and returns the profile data

        print(f"ResearchAgent: Starting research for lead {lead_data['company_name']}")

        lead_id = lead_data.get('id')

        print("ResearchAgent: Researching company info...")
        company_info = self._research_company(
            lead_data['company_name'],
            lead_data.get('industry'),
            lead_id
        )

        print("ResearchAgent: Researching contact...")

        person_info = self._research_person(
            lead_data['contact_name'],
            lead_data.get('title'),
            lead_data.get('contact_linkedin'),
            lead_id
        )

        print("Identifying pain points...")

        pain_points = self._idenitfy_pain_points(
            company_info,
            person_info,
            lead_id
        )   

        profile = {
            # company
            "company_description": company_info.get("description", ""),
            "company_size": company_info.get("size"),
            "funding_stage": company_info.get("funding"),
            "tech_stack": company_info.get("tech_stack", {}),
            "recent_news": company_info.get("recent_news", []),
            "competitors": company_info.get("competitors", []),
            "likely_challenges": company_info.get("likely_challenges", []),
            "contact_background": person_info.get("background", ""),
            "contact_cares_about": person_info.get("cares_about", []),
            "communication_style": person_info.get("communication_style", "professional"),
            "pain_points": pain_points,
            "research_completed_at": datetime.now().isoformat()
        }


        print(f"ResearchAgent: Completed research for lead {lead_data['company_name']}")

        return profile
    
    def _research_company(self, company_name: str, industry: str = None, lead_id: str = None) -> Dict:
        #researches company information using LLM and other API's
        prompt = f"""
        You are a B2B sales research analyst. Research this company and provide structured information.
        Company: {company_name}
        Industry: {industry or "Unknown"}

        Provide the following in JSON format:
        {{
        "description": "2-3 sentence overview of what they do",
        "size": "estimate company size (10-50, 50-200, 200-1000, 1000+)",
        "funding": "estimated funding stage (bootstrapped, seed, series A/B/C, public)",
        "recent_news": [
            "news item 1",
            "news item 2",
            "news item 3"
        ],
        "tech_stack": {{
            "languages": ["Python", "JavaScript"],
            "frameworks": ["React", "Django"],
            "tools": ["AWS", "Docker"]
        }},
        "competitors": ["Competitor 1", "Competitor 2"],
        "likely_challenges": ["Challenge 1", "Challenge 2"]
        }}

        Base this on your training data knowledge of this company. If you don't know specifics, make reasonable inferences based on industry and company name."""

        return self.call_llm_json(prompt, lead_id=lead_id)

    def _research_person(self, name: str, title: str = None, linkedin_url: str = None, lead_id: str = None) -> Dict:
        #researches person information using LLM and other API's
        
        prompt= f"""
        You are researching a B2B sales contact. Provide insights based on their role.

        Name: {name}
        Title: {title or "Unknown"}
        LinkedIn: {linkedin_url or "Not provided"}

        Provide JSON:
        {{
        "role": "what they do in 1 sentence",
        "background": "likely career path and experience",
        "cares_about": [
            "what matters to them in their role",
            "their likely priorities",
            "what keeps them up at night"
        ],
        "communication_style": "professional/casual/technical/executive",
        "best_approach": "how to reach out to this person effectively"
        }}
        Make reasonable inferences based on the title and role."""

        return self.call_llm_json(prompt, lead_id=lead_id)
    
    def _idenitfy_pain_points(self, company_info: Dict, person_info: Dict, lead_id: str = None) -> List:
        #identifies pain points based on company and person info

        prompt = f"""
        You are a sales strategist. Based on this research, identify specific pain points that a sales automation / AI sales agent platform could solve.
        COMPANY INFO:
        {json.dumps(company_info, indent=2)}

        CONTACT INFO:
        {json.dumps(person_info, indent=2)}

        Identify 3-5 specific pain points and return as JSON array:
        [
        {{
            "pain_point": "specific problem they have",
            "reasoning": "why we think they have this problem",
            "urgency": 7,  // 1-10 scale
            "our_solution": "how our product solves this",
            "talking_point": "one-sentence pitch to mention this"
        }}
        ]

        Be specific and connect to their actual situation, not generic problems."""

        result = self.call_llm_json(prompt, lead_id=lead_id)

        if isinstance(result, dict) and result.get("error"):
            return []

        return result if isinstance(result, list) else []
