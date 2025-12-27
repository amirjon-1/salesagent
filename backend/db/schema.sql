CREATE TABLE IF NOT EXISTS leads(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_linkedin VARCHAR(500),
    title VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new', -- new, researching, ready, contacted, responded
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lead_profiles(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    company_description TEXT,
    tech_stack JSONB,
    recent_news JSONB,
    pain_points JSONB,
    research_completed_at TIMESTAMP, 
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signals(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    signal_type VARCHAR(100), -- e.g., funding, hiring, product_launch
    signal_data JSONB NOT NULL,
    urgency_score INTEGER CHECK (urgency_score BETWEEN 1 AND 10),
    detected_at TIMESTAMP DEFAULT NOW(), 
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outreach(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    message_type VARCHAR(50), -- e.g., email, linkedin_message
    subject VARCHAR(500),
    body TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'draft', -- draft, sent, responded
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_activity(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(255) NOT NULL,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    input_data JSONB, 
    output_data JSONB,
    duration_ms INTEGER,  
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company_name);
CREATE INDEX IF NOT EXISTS idx_signals_lead ON signals(lead_id);  
CREATE INDEX IF NOT EXISTS idx_signals_urgency ON signals(urgency_score DESC);
CREATE INDEX IF NOT EXISTS idx_outreach_lead ON outreach(lead_id);
CREATE INDEX IF NOT EXISTS idx_agent_activity_time ON agent_activity(created_at DESC);
