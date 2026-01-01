# SalesAgent AI - Autonomous Multi-Agent Sales Research System

An intelligent sales automation platform that uses multiple AI agents to research leads, detect buying signals, and generate personalized outreach at scale.


## Problem

Sales teams waste 3-4 hours per lead on manual research, miss 80% of buying signals, and struggle to personalize outreach at scale. This results in low response rates and lost revenue.

## Solution

SalesAgent AI deploys a coordinated team of AI agents that autonomously:
- Research companies and contacts in minutes
- Monitor buying signals 24/7
- Identify pain points and craft solutions
- Generate personalized outreach messages

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                    FastAPI REST
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Multi-Agent System                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Research   │  │    Signal    │  │    Writer    │       │
│  │    Agent     │  │    Agent     │  │    Agent     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                   ┌───────▼────────┐                        │
│                   │   Coordinator  │                        │
│                   │     Agent      │                        │
│                   └────────────────┘                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                  ┌───────▼────────┐
                  │   PostgreSQL   │
                  └────────────────┘
```

## AI Agents

### Research Agent
- Analyzes company information and market position
- Profiles decision makers and their priorities
- Identifies 2-4 specific pain points with urgency scores
- Determines tech stack and competitors

**Technologies:** Gemini 2.5 Flash, structured JSON outputs

### Signal Agent
- Monitors funding announcements, job postings, and news
- Detects buying signals in real-time
- Assigns urgency scores (1-10) to opportunities

### Writer Agent
- Generates personalized email templates
- References specific pain points and recent events
- Adapts tone based on recipient communication style

### Coordinator Agent *(Coming Soon)*
- Orchestrates workflow between agents
- Resolves conflicts and prioritizes tasks
- Reports status to human sales reps

## Tech Stack

**Backend:**
- Python
- FastAPI (REST API)
- PostgreSQL
- Google Gemini 2.5 Flash LLM
- Psycopg2, the database driver

**Frontend:**
- React
- Basic CSS 

- Local development: PostgreSQL
- Production: AWS RDS + EC2

### Prerequisites
- Python 
- Node.js
- PostgreSQL 14+
- Gemeni API key

### Backend Setup
```bash
# Clone repo
git clone https://github.com/amirjon-1/salesagent.git
cd salesagent

# Set up python virtual env
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
touch .env
#below info
#GOOGLE_API_KEY=your_api_key_here
#DATABASE_URL=postgresql://localhost:5432/sales_agents

# Set up database
createdb sales_agents
psql sales_agents < database/schema.sql

# Run backend
python api.py
```

Backend runs at `http://localhost:8000`

### Frontend Setup
```bash
# In new terminal
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`

## Database Schema
```sql
leads             -- Basic lead information
├── lead_profiles -- Research results
├── signals       -- Detected buying triggers
├── outreach      -- Generated messages
└── agent_activity -- Audit log
```

## 🙏 Acknowledgments

- Built with [Google Gemini](https://ai.google.dev/)
- AI Agents by Kaggle [Kaggle](https://www.kaggle.com/learn-guide/5-day-agents)


## Future Enhancements

- [ ] Complete Timing Agent (optimal outreach timing)
- [ ] Real-time news monitoring via NewsAPI
- [ ] LinkedIn integration via Proxycurl
- [ ] Deploy to Railway and Vercel (AWS in future)
- [ ] Add authentication and user management
- [ ] Implement agent-to-agent communication
- [ ] A/B testing for outreach templates
- [ ] Analytics dashboard with conversion metrics

---

Built with ❤️ and AI agents