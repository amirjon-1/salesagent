from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime

class SignalAgent(BaseAgent):
    #agent specialized in generating sales signals

    def __init__(self):
        super().__init__(name="SignalAgent", role="Sales signal detector who identifies buying opportunities from funding, hiring, and news events", temperature=0.4)
    
    def execute(self, lead_data: Dict[str, Any]) -> List[Dict]:
        
        print(f"SignalAgent: Generating signals for lead {lead_data['company_name']}")
        lead_id = lead_data.get('id')
        company_name = lead_data['company_name']
        industry = lead_data.get('industry')

        signals = []

        print("SignalAgent: Detecting funding signals...")
        funding_signals = self._detect_funding_signals(
            company_name,
            lead_id
        )
        signals.extend(funding_signals)

        print("SignalAgent: Detecting hiring signals...")
        hiring_signals = self._detect_hiring_signals(
            company_name,
            industry,
            lead_id
        )
        signals.extend(hiring_signals)

        print("SignalAgent: Detecting news signals...")
        news_signals = self._detect_news_signals(
            company_name,
            lead_id
        )
        signals.extend(news_signals)

        print(f"SignalAgent: Generated {len(signals)} signals for lead {company_name}")

        return signals
    
    def _detect_funding_signals(self, company_name: str, lead_id: str = None) -> Dict:
        #detects funding related signals for a company

        prompt = f"""
            Has this company raised funding recently? Look for Series rounds, seed funding, IPOs, or acquisitions.

            Return JSON:
            {{
                "has_recent_funding": true/false,
                "funding_round": "Series A" or "Seed" or "Series B" or null,
                "amount": "10M USD" or null,
                "date": "Q4 2024" or "November 2024" or null,
                "lead_investor": "Sequoia Capital" or null,
                "total_raised": "50M USD" or null
            }}

            Base this on your training data. If you don't know, set has_recent_funding to false.
        """

        result = self.call_llm_json(prompt, lead_id=lead_id)

        if result.get("error") or not result.get("has_recent_funding"):
            return []
        
        urgency = self._calculate_urgency("funding", result)

        return [{
            "signal_type": "funding",
            "signal_data": result,
            "urgency_score": urgency,
            "detected_at": datetime.now().isoformat()
        }]


    def _detect_hiring_signals(self, company_name: str, industry: str, lead_id: str = None) -> Dict:
        #detects hiring related signals for a company

        prompt = f"""
            Research hiring activity for {company_name} (Industry: {industry or 'Unknown'}).

            Are they actively hiring? How many roles? Which departments?

            Return JSON:
            {{
                "is_hiring": true/false,
                "total_openings": 15,
                "sales_roles": 5,
                "engineering_roles": 8,
                "key_roles": ["VP Sales", "SDRs", "Account Executives"],
                "expansion_signal": true/false
            }}

            Set is_hiring to false if you don't have information.
        """

        result = self.call_llm_json(prompt, lead_id=lead_id)

        if result.get("error") or not result.get("is_hiring"):
            return []

        urgency = self._calculate_urgency("hiring", result)

        return [{
            "signal_type": "hiring",
            "signal_data": result,
            "urgency_score": urgency,
            "detected_at": datetime.now().isoformat()
        }]

    def _detect_news_signals(self, company_name: str, lead_id: str = None) -> Dict:
        #detects news related signals for a company

        prompt = f"""
            Research recent news and events for {company_name}.

            Look for: product launches, partnerships, awards, leadership changes, expansions.

            Return JSON array of news items (up to 3 most recent):
            [
            {{
                "event_type": "product_launch" or "partnership" or "leadership_change" or "expansion" or "award",
                "description": "Launched new AI product",
                "date": "December 2024" or null,
                "relevance": "high" or "medium" or "low"
            }}
            ]

            Return empty array [] if no significant news.
        """
        result = self.call_llm_json(prompt, lead_id=lead_id)

        if result.get("error") or not isinstance(result, list) or len(result) == 0:
            return []
        
        signals = []

        for news_item in result:
            urgency = self._calculate_urgency("news", news_item)

            signals.append({
                "signal_type": "news",
                "signal_data": news_item,
                "urgency_score": urgency,
                "detected_at": datetime.now().isoformat()
            })

        return signals


    def _calculate_urgency(self, signal_type: str, signal_data: Dict) -> int:
        #calculates an urgency score for a signal based on its type and data

        if signal_type == "funding":
            round_type = signal_data.get("funding_round", "").lower()

            if "series c" in round_type or "series d" in round_type:
                return 9 
            elif "series b" in round_type:
                return 8
            elif "series a" in round_type:
                return 7
            elif "seed" in round_type:
                return 6
            else:
                return 5

        if signal_type == "hiring":
            total_openings = signal_data.get("total_openings", 0)
            sales_roles = signal_data.get("sales_roles", 0)

            if sales_roles >= 5:
                return 9
            elif total_openings >= 20:
                return 8
            elif total_openings >= 10:
                return 7
            elif total_openings >= 5:
                return 6
            else:
                return 5

        if signal_type == "news":
            event_type = signal_data.get("event_type", "")
            relevance = signal_data.get("relevance", "medium")

            if event_type == "product_launch" and relevance == "high":
                return 7
            elif event_type == "leadership_change":
                return 6
            elif event_type == "partnership":
                return 6
            elif event_type == "expansion":
                return 7
            elif event_type == "award":
                return 4
            else:
                return 5

        return 5