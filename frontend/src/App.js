import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [researching, setResearching] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  
  const [newLead, setNewLead] = useState({
    company_name: '',
    contact_name: '',
    contact_email: '',
    contact_linkedin: '',
    title: '',
    industry: '',
    company_size: ''
  });

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await fetch(`${API_URL}/leads`);
      const data = await response.json();
      setLeads(data);
    } catch (error) {
      console.error('Failed to fetch leads:', error);
    }
  };

  const fetchLeadDetails = async (leadId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/leads/${leadId}`);
      const data = await response.json();
      setSelectedLead(data);
    } catch (error) {
      console.error('Failed to fetch lead details:', error);
    }
    setLoading(false);
  };

  const handleCreateLead = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await fetch(`${API_URL}/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLead)
      });
      
      await fetchLeads();
      
      setNewLead({
        company_name: '',
        contact_name: '',
        contact_email: '',
        contact_linkedin: '',
        title: '',
        industry: '',
        company_size: ''
      });
      
      setShowAddModal(false);
    } catch (error) {
      console.error('Failed to create lead:', error);
    }
    
    setLoading(false);
  };

  const handleResearch = async (leadId) => {
    setResearching(true);
    
    try {
      await fetch(`${API_URL}/leads/${leadId}/research`, {
        method: 'POST'
      });
      
      await fetchLeads();
      await fetchLeadDetails(leadId);
    } catch (error) {
      console.error('Research failed:', error);
    }
    
    setResearching(false);
  };

  const getStatusColor = (status) => {
    const colors = {
      new: '#0073e6',
      researching: '#f5a623',
      ready: '#7ed321',
      contacted: '#9013fe'
    };
    return colors[status] || '#b0b0b0';
  };

  const filteredLeads = statusFilter === 'all' 
    ? leads 
    : leads.filter(l => l.status === statusFilter);

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-content">
          <div className="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path d="M16 1L30 9V23L16 31L2 23V9L16 1Z" fill="#FF385C"/>
              <path d="M16 8L23 12V20L16 24L9 20V12L16 8Z" fill="white"/>
            </svg>
            <span className="logo-text">SalesAgent</span>
          </div>
          <div className="nav-right">
            <button className="nav-button">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0a6 6 0 00-6 6v2.586l-.707.707A1 1 0 002 11h12a1 1 0 00.707-1.707L14 8.586V6a6 6 0 00-6-6z"/>
              </svg>
            </button>
            <div className="nav-avatar">A</div>
          </div>
        </div>
      </nav>

      <div className="main-content">
        <aside className="sidebar">
          <div className="sidebar-section">
            <div className="sidebar-header">
              <h2>Leads</h2>
              <button className="btn-add" onClick={() => setShowAddModal(true)}>
                +
              </button>
            </div>
            
            <div className="stats-row">
              <div className="stat-card">
                <div className="stat-value">{leads.length}</div>
                <div className="stat-label">Total leads</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{leads.filter(l => l.status === 'ready').length}</div>
                <div className="stat-label">Ready</div>
              </div>
            </div>

            <div className="filter-section">
              <div className="filter-label">Filter by status</div>
              <div className="filter-pills">
                <button 
                  className={`filter-pill ${statusFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setStatusFilter('all')}
                >
                  All
                </button>
                <button 
                  className={`filter-pill ${statusFilter === 'new' ? 'active' : ''}`}
                  onClick={() => setStatusFilter('new')}
                >
                  New
                </button>
                <button 
                  className={`filter-pill ${statusFilter === 'ready' ? 'active' : ''}`}
                  onClick={() => setStatusFilter('ready')}
                >
                  Ready
                </button>
              </div>
            </div>
          </div>

          <div className="leads-list">
            {filteredLeads.length === 0 ? (
              <div className="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <h3>No leads found</h3>
                <p>Add a lead to get started</p>
              </div>
            ) : (
              filteredLeads.map(lead => (
                <div
                  key={lead.id}
                  className={`lead-card ${selectedLead?.lead?.id === lead.id ? 'active' : ''}`}
                  onClick={() => fetchLeadDetails(lead.id)}
                >
                  <div className="lead-card-header">
                    <div className="lead-card-company">{lead.company_name}</div>
                    <div 
                      className="status-dot"
                      style={{ backgroundColor: getStatusColor(lead.status) }}
                    />
                  </div>
                  <div className="lead-card-contact">{lead.contact_name}</div>
                  <div className="lead-card-meta">{lead.title || 'No title'}</div>
                </div>
              ))
            )}
          </div>
        </aside>

        <main className="content-area">
          {loading && !selectedLead ? (
            <div className="loading-state">
              <div className="spinner"/>
              <p>Loading lead details...</p>
            </div>
          ) : selectedLead ? (
            <div>
              <div className="content-header">
                <h1 className="content-title">{selectedLead.lead.company_name}</h1>
                <div className="content-meta">
                  <div className="meta-item">
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z"/>
                      <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z"/>
                    </svg>
                    {selectedLead.lead.industry || 'Unknown industry'}
                  </div>
                  <div className="meta-item">
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
                    </svg>
                    {selectedLead.lead.company_size || selectedLead.profile?.company_size || 'Unknown size'}
                  </div>
                  {selectedLead.profile?.funding_stage && (
                    <div className="meta-item">
                      <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z"/>
                      </svg>
                      {selectedLead.profile.funding_stage}
                    </div>
                  )}
                  <div 
                    className="status-badge"
                    style={{ 
                      backgroundColor: `${getStatusColor(selectedLead.lead.status)}15`,
                      color: getStatusColor(selectedLead.lead.status)
                    }}
                  >
                    {selectedLead.lead.status}
                  </div>
                  {selectedLead.lead.status === 'new' && (
                    <button
                      className="btn-primary"
                      onClick={() => handleResearch(selectedLead.lead.id)}
                      disabled={researching}
                    >
                      {researching ? (
                        <>
                          <div className="btn-spinner"/>
                          Researching...
                        </>
                      ) : (
                        <>
                          <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M9 9a2 2 0 114 0 2 2 0 01-4 0z"/>
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a4 4 0 00-3.446 6.032l-2.261 2.26a1 1 0 101.414 1.415l2.261-2.261A4 4 0 1011 5z"/>
                          </svg>
                          Start research
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>

              <div className="content-grid">
                <div className="content-section">
                  <h3 className="section-title">Contact</h3>
                  <div className="contact-display">
                    <div className="contact-avatar-large">
                      {selectedLead.lead.contact_name.charAt(0)}
                    </div>
                    <div>
                      <div className="contact-name">{selectedLead.lead.contact_name}</div>
                      <div className="contact-title">{selectedLead.lead.title || 'No title'}</div>
                    </div>
                  </div>
                  
                  <div className="contact-details">
                    {selectedLead.lead.contact_email && (
                      <div className="contact-detail">
                        <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                        </svg>
                        {selectedLead.lead.contact_email}
                      </div>
                    )}
                    {selectedLead.lead.contact_linkedin && (
                      <div className="contact-detail">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                        <a href={selectedLead.lead.contact_linkedin} target="_blank" rel="noopener noreferrer">
                          View profile
                        </a>
                      </div>
                    )}
                  </div>

                  {selectedLead.profile?.contact_background && (
                    <div style={{marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #ebebeb'}}>
                      <div style={{fontSize: '12px', fontWeight: '600', color: '#717171', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.8px'}}>
                        Background
                      </div>
                      <p style={{fontSize: '14px', color: '#222222', lineHeight: '1.5'}}>
                        {selectedLead.profile.contact_background}
                      </p>
                    </div>
                  )}

                  {selectedLead.profile?.communication_style && (
                    <div style={{marginTop: '12px'}}>
                      <div style={{fontSize: '12px', fontWeight: '600', color: '#717171', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.8px'}}>
                        Communication style
                      </div>
                      <span style={{padding: '4px 12px', background: '#f7f7f7', borderRadius: '6px', fontSize: '13px', color: '#222222', textTransform: 'capitalize'}}>
                        {selectedLead.profile.communication_style}
                      </span>
                    </div>
                  )}

                  {selectedLead.profile?.contact_cares_about && selectedLead.profile.contact_cares_about.length > 0 && (
                    <div style={{marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #ebebeb'}}>
                      <div style={{fontSize: '12px', fontWeight: '600', color: '#717171', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.8px'}}>
                        Priorities
                      </div>
                      <ul style={{margin: '0', paddingLeft: '20px'}}>
                        {selectedLead.profile.contact_cares_about.map((item, idx) => (
                          <li key={idx} style={{fontSize: '14px', color: '#222222', lineHeight: '1.6', marginBottom: '4px'}}>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {selectedLead.profile && (
                  <>
                    <div className="content-section">
                      <h3 className="section-title">About</h3>
                      <p className="description-text">
                        {selectedLead.profile.company_description}
                      </p>
                    </div>

                    {selectedLead.profile.recent_news && selectedLead.profile.recent_news.length > 0 && (
                      <div className="content-section">
                        <h3 className="section-title">Recent news</h3>
                        <ul style={{margin: '0', paddingLeft: '20px'}}>
                          {selectedLead.profile.recent_news.map((news, idx) => (
                            <li key={idx} style={{fontSize: '14px', color: '#222222', lineHeight: '1.6', marginBottom: '8px'}}>
                              {news}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {selectedLead.profile.competitors && selectedLead.profile.competitors.length > 0 && (
                      <div className="content-section">
                        <h3 className="section-title">Competitors</h3>
                        <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
                          {selectedLead.profile.competitors.map((competitor, idx) => (
                            <span key={idx} className="tech-tag">{competitor}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedLead.profile.likely_challenges && selectedLead.profile.likely_challenges.length > 0 && (
                      <div className="content-section">
                        <h3 className="section-title">Likely challenges</h3>
                        <ul style={{margin: '0', paddingLeft: '20px'}}>
                          {selectedLead.profile.likely_challenges.map((challenge, idx) => (
                            <li key={idx} style={{fontSize: '14px', color: '#222222', lineHeight: '1.6', marginBottom: '8px'}}>
                              {challenge}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {selectedLead.profile.pain_points && selectedLead.profile.pain_points.length > 0 && (
                      <div className="content-section">
                        <h3 className="section-title">Pain points ({selectedLead.profile.pain_points.length})</h3>
                        <div className="pain-points-list">
                          {selectedLead.profile.pain_points.map((pp, idx) => (
                            <div key={idx} className="pain-point-card">
                              <div className="pain-point-header">
                                <h4 className="pain-point-title">{pp.pain_point}</h4>
                                <div className="urgency-badge">{pp.urgency}/10</div>
                              </div>
                              <p className="pain-point-text">{pp.reasoning}</p>
                              <div className="pain-point-solution">
                                <strong>Solution:</strong> {pp.our_solution}
                              </div>
                              <div className="pain-point-pitch">
                                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                  <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"/>
                                </svg>
                                {pp.talking_point}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedLead.profile.tech_stack && (
                      <div className="content-section">
                        <h3 className="section-title">Tech stack</h3>
                        <div className="tech-stack">
                          {Object.entries(selectedLead.profile.tech_stack).map(([category, items]) => (
                            <div key={category} className="tech-category">
                              <div className="tech-category-label">{category}</div>
                              <div className="tech-tags">
                                {items.map((item, idx) => (
                                  <span key={idx} className="tech-tag">{item}</span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <h3>Select a lead</h3>
              <p>Choose a lead from the sidebar to view details</p>
            </div>
          )}
        </main>
      </div>

      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <button className="btn-close" onClick={() => setShowAddModal(false)}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L8 6.586l2.293-2.293a1 1 0 111.414 1.414L9.414 8l2.293 2.293a1 1 0 01-1.414 1.414L8 9.414l-2.293 2.293a1 1 0 01-1.414-1.414L6.586 8 4.293 5.707a1 1 0 010-1.414z"/>
                </svg>
              </button>
              <h2>Add a new lead</h2>
            </div>
            <form onSubmit={handleCreateLead} className="modal-form">
              <div className="form-group">
                <label>Company name</label>
                <input
                  type="text"
                  value={newLead.company_name}
                  onChange={(e) => setNewLead({...newLead, company_name: e.target.value})}
                  required
                  placeholder="Acme Corp"
                />
              </div>

              <div className="form-group">
                <label>Contact name</label>
                <input
                  type="text"
                  value={newLead.contact_name}
                  onChange={(e) => setNewLead({...newLead, contact_name: e.target.value})}
                  required
                  placeholder="Jane Smith"
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={newLead.contact_email}
                  onChange={(e) => setNewLead({...newLead, contact_email: e.target.value})}
                  placeholder="jane@acme.com"
                />
              </div>

              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={newLead.title}
                  onChange={(e) => setNewLead({...newLead, title: e.target.value})}
                  placeholder="CEO"
                />
              </div>

              <div className="form-group">
                <label>LinkedIn URL</label>
                <input
                  type="url"
                  value={newLead.contact_linkedin}
                  onChange={(e) => setNewLead({...newLead, contact_linkedin: e.target.value})}
                  placeholder="https://linkedin.com/in/janesmith"
                />
              </div>

              <div className="form-group">
                <label>Industry</label>
                <input
                  type="text"
                  value={newLead.industry}
                  onChange={(e) => setNewLead({...newLead, industry: e.target.value})}
                  placeholder="SaaS"
                />
              </div>

              <div className="form-group">
                <label>Company size</label>
                <select
                  value={newLead.company_size}
                  onChange={(e) => setNewLead({...newLead, company_size: e.target.value})}
                >
                  <option value="">Select a size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="10-50">10-50 employees</option>
                  <option value="50-200">50-200 employees</option>
                  <option value="200-1000">200-1000 employees</option>
                  <option value="1000+">1000+ employees</option>
                </select>
              </div>

              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Adding lead...' : 'Add lead'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;