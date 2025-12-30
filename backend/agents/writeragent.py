from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

class WriterAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="WriterAgent", role="Expert sales copywriter who crafts personalized, compelling outreach that converts", temperature=0.7)
    

    def execute(self, lead_data: Dict, profile_data: Dict, signals: List[Dict] = None) -> Dict:
        #executes the writing task to generate outreach messages

        print(f"WriterAgent: Generating outreach for lead {lead_data['company_name']}")

        lead_id = lead_data.get('id')
        contact_name = lead_data['contact_name']
        company_name = lead_data['company_name']
        title = lead_data.get('title', 'there')

        communication_style  = profile_data.get('communication_style', 'professional')
        pain_points = profile_data.get('pain_points', [])
        first_pain_point = self._select_primary_pain_point(pain_points, signals) if pain_points else None

        signalContext = self._build_signal_context(signals) if signals else None

        print("WriterAgent: Crafting subject line...")
        subject = self._generate_subject_line(
            company_name,
            signalContext,
            first_pain_point,
        )

        print("WriterAgent: Crafting email body...")
        body = self._generate_email_body(
            contact_name,
            company_name,
            title,
            communication_style,
            signalContext,
            first_pain_point,
            profile_data
        )

        personalization_score = self._calculate_personalization_score(
            has_signals = bool(signals), 
            has_pain_points = bool(pain_points),
            has_profile = bool(profile_data)
        )

        print(f"WriterAgent: Generated outreach for lead {lead_data['company_name']} with personalization score {personalization_score}/10")

        return {
            "subject": subject,
            "body": body,
            "message_type": "email",
            "personalization_score": personalization_score,
            "created_at": datetime.now().isoformat()
        }

    def _build_signal_context(self, signals: List[Dict]) -> str:
        #builds a textual context from the signals for use in prompts

        if not signals:
            return None
        
        sorted_signals = sorted(signals, key=lambda s: s.get('urgency_score', 0), reverse=True)

        context_lines = []
        for signal in sorted_signals[:2]: # top 2 signals based on urgency
            signal_type = signal.get('signal_type', 'unknown')
            signal_data = signal.get('signal_data', {})

            if signal_type == 'funding':
                round = signal_data.get('funding_round', 'unknown round')
                amount = signal_data.get('amount', 'an undisclosed amount')

                if amount:
                    context_lines.append(f"The company recently raised {amount} in {round}.")
                else:
                    context_lines.append(f"The company recently raised funding in {round}.")
            elif signal_type == 'hiring':
                total = signal_data.get('total_openings', 0)
                if total > 0:
                    context_lines.append(f"The company is actively hiring with {total} open positions.")
            elif signal_type == 'news':
                event_type = signal_data.get('event_type', 'an event')
                description = signal_data.get('description', '')
                if event_type == 'product_launch':
                    context_lines.append(f"The company recently launched a new product. {description}")
                elif description:
                    context_lines.append(f"Recent news: {description}")

        
        if context_lines:
            return " and ".join(context_lines)
        
        return None
    
    def _select_primary_pain_point(self, pain_points: List[Dict], signals: List[Dict] = None) -> Optional[Dict]:
        #selects the most relevant pain point based on signals

        if not pain_points:
            return None
        
        if signals:
            for signal in signals:
                if signal["signal_type"] == "hiring":
                    for pp in pain_points:
                        if any(word in pp.get('pain_point', '').lower() for word in ['scale', 'scaling', 'team', 'growth', 'hiring']):
                            return pp
        
        sorteds = sorted(pain_points, key=lambda p: p.get('urgency', 0), reverse=True)
        return sorteds[0] if sorteds else None
    

    def _generate_subject_line(self, company_name: str, signal_context: str, top_pain_point: Dict = None) -> str:
        #generates a subject line for the outreach email

        prompt = f"Craft a compelling email subject line to get the attention of a decision maker at {company_name}."

        if signal_context:
            prompt += f" Mention their recent activities: {signal_context}."

        if top_pain_point:
            prompt += f" Address their pain point: {top_pain_point['pain_point']}."

        prompt += " Keep it concise and engaging."

        prompt += """
            Good subject line examples:
            - "Quick question about your Series B plans"
            - "Scaling to 100 reps? Here's what worked for us"
            - "Re: Your SDR hiring spree"

            Requirements:
            - Under 60 characters
            - Reference something specific, not generic
            - Create curiosity without clickbait
            - Professional but conversational
            - NO: "I hope this finds you well", "Touching base", "Following up"

            Return ONLY the subject line text, no quotes, no explanation."""


        subject = self.call_llm(prompt)
        return subject.strip().strip('"').strip("'")

    def _generate_email_body(self, contact_name: str, company_name: str, title: str, communication_style: str, signal_context: str, top_pain_point: Dict = None, profile_data: Dict = None) -> str:
        #generates the body of the outreach email

        if signal_context:
            opening = f"I noticed that {signal_context}."
        else:
            opening = f"I wanted to reach out regarding {company_name} growth."

        if top_pain_point:
            pain_desc = top_pain_point.get('pain_point', 'sales efficiency challenges')
            our_solution = top_pain_point.get('our_solution', 'streamlining sales outreach with AI')
            talking_point = top_pain_point.get('talking_point', 'help sales teams work smarter')
        else:
            pain_desc = "scaling sales operations"
            our_solution = "AI agents that handle research and outreach"
            talking_point = "help sales teams focus on closing deals"

        map = {
            'professional': "professional and respectful",
            'casual': "friendly and conversational",
            'technical': "technical and data-driven",
            'executive': "concise and high-level"
        }

        tone = map.get(communication_style, "professional and respectful")
        
        prompt = f"""
            Write a personalized B2B sales email.

            TO: {contact_name}, {title} at {company_name}
            TONE: {tone}

            OPENING HOOK: {opening}
            PAIN POINT: {pain_desc}
            OUR SOLUTION: {our_solution}
            KEY BENEFIT: {talking_point}

            EMAIL STRUCTURE:
            1. Personal opening that references the hook (1-2 sentences)
            2. Show understanding of their challenge (1 sentence)
            3. Brief mention of how we've helped similar companies (1 sentence)
            4. Low-pressure CTA: ask for 15-min call next week (1 sentence)

            CRITICAL RULES:
            - Total length: 80-100 words maximum
            - Conversational, not corporate
            - NO cliches: "hope this email finds you well", "touching base", "circling back"
            - NO aggressive sales language
            - Focus on THEIR challenge, not our product features
            - End with specific meeting request (15-min call next week)

            Return ONLY the email body, no subject line, no signature."""

        body = self.call_llm(prompt)
        body = body.strip()
        signature = f"""
            Best regards,
            [Your Name]
        """

        return body + "\n\n" + signature
    

        
    def _calculate_personalization_score(self, has_signals: bool, has_pain_points: bool, has_profile: bool) -> int:
        #calculates a personalization score out of 10 based on available data

        score = 5

        if has_signals:
            score += 2
        if has_pain_points:
            score += 2
        if has_profile:
            score += 1

        return min(score, 10)


