import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [researching, setResearching] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  
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
      const response = await fetch(`${API_URL}/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLead)
      });
      
      await response.json();
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
      new: '#3b82f6',
      researching: '#f59e0b',
      ready: '#10b981',
      contacted: '#8b5cf6'
    };
    return colors[status] || '#6b7280';
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-content">
          <div className="nav-left">
            <div className="logo">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="url(#gradient)"/>
                <path d="M16 8L24 16L16 24L8 16L16 8Z" fill="white"/>
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                    <stop stopColor="#3b82f6"/>
                    <stop offset="1" stopColor="#8b5cf6"/>
                  </linearGradient>
                </defs>
              </svg>
              <span className="logo-text">SalesAgent</span>
            </div>
          </div>
          <div className="nav-right">
            <button className="nav-button">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z"/>
                <path d="M10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
              </svg>
            </button>
            <div className="nav-avatar">
              <span>A</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="main-content">
        <aside className="sidebar">
          <div className="sidebar-header">
            <h2>Leads</h2>
            <button 
              className="btn-icon"
              onClick={() => setShowAddModal(true)}
              title="Add new lead"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"/>
              </svg>
            </button>
          </div>

          <div className="sidebar-stats">
            <div className="stat-card">
              <div className="stat-value">{leads.length}</div>
              <div className="stat-label">Total Leads</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{leads.filter(l => l.status === 'ready').length}</div>
              <div className="stat-label">Ready</div>
            </div>
          </div>

          <div className="leads-list">
            {leads.length === 0 ? (
              <div className="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>No leads yet</p>
                <button 
                  className="btn-primary"
                  onClick={() => setShowAddModal(true)}
                >
                  Add your first lead
                </button>
              </div>
            ) : (
              leads.map(lead => (
                <div
                  key={lead.id}
                  className={`lead-item ${selectedLead?.lead?.id === lead.id ? 'active' : ''}`}
                  onClick={() => fetchLeadDetails(lead.id)}
                >
                  <div className="lead-item-header">
                    <div className="lead-item-title">{lead.company_name}</div>
                    <div 
                      className="lead-status-dot"
                      style={{ backgroundColor: getStatusColor(lead.status) }}
                    />
                  </div>
                  <div className="lead-item-subtitle">{lead.contact_name}</div>
                  <div className="lead-item-meta">{lead.title || 'No title'}</div>
                </div>
              ))
            )}
          </div>
        </aside>

        <main className="content-area">
          {loading && !selectedLead ? (
            <div className="loading-state">
              <div className="spinner"/>
              <p>Loading...</p>
            </div>
          ) : selectedLead ? (
            <div className="lead-detail">
              <div className="detail-header">
                <div>
                  <h1>{selectedLead.lead.company_name}</h1>
                  <div className="detail-meta">
                    <span>{selectedLead.lead.industry || 'No industry'}</span>
                    <span>•</span>
                    <span>{selectedLead.lead.company_size || 'Unknown size'}</span>
                    <span>•</span>
                    <span 
                      className="status-badge"
                      style={{ 
                        backgroundColor: `${getStatusColor(selectedLead.lead.status)}15`,
                        color: getStatusColor(selectedLead.lead.status)
                      }}
                    >
                      {selectedLead.lead.status}
                    </span>
                  </div>
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
                        Start Research
                      </>
                    )}
                  </button>
                )}
              </div>

              <div className="detail-grid">
                <div className="detail-card">
                  <div className="card-label">Contact</div>
                  <div className="card-content">
                    <div className="contact-info">
                      <div className="contact-avatar">
                        {selectedLead.lead.contact_name.charAt(0)}
                      </div>
                      <div>
                        <div className="contact-name">{selectedLead.lead.contact_name}</div>
                        <div className="contact-title">{selectedLead.lead.title}</div>
                      </div>
                    </div>
                    {selectedLead.lead.contact_email && (
                      <div className="contact-detail">
                        <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                        </svg>
                        <span>{selectedLead.lead.contact_email}</span>
                      </div>
                    )}
                    {selectedLead.lead.contact_linkedin && (
                      <div className="contact-detail">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                        </svg>
                        <a href={selectedLead.lead.contact_linkedin} target="_blank" rel="noopener noreferrer">
                          LinkedIn Profile
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                {selectedLead.profile && (
                  <>
                    <div className="detail-card full-width">
                      <div className="card-label">Company Overview</div>
                      <div className="card-content">
                        <p className="company-description">
                          {selectedLead.profile.company_description}
                        </p>
                      </div>
                    </div>

                    {selectedLead.profile.pain_points && selectedLead.profile.pain_points.length > 0 && (
                      <div className="detail-card full-width">
                        <div className="card-label">
                          Pain Points ({selectedLead.profile.pain_points.length})
                        </div>
                        <div className="card-content">
                          <div className="pain-points-grid">
                            {selectedLead.profile.pain_points.map((pp, idx) => (
                              <div key={idx} className="pain-point-card">
                                <div className="pain-point-header">
                                  <h3>{pp.pain_point}</h3>
                                  <div className="urgency-badge">
                                    {pp.urgency}/10
                                  </div>
                                </div>
                                <p className="pain-point-reasoning">{pp.reasoning}</p>
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
                      </div>
                    )}

                    {selectedLead.profile.tech_stack && (
                      <div className="detail-card">
                        <div className="card-label">Tech Stack</div>
                        <div className="card-content">
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
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="empty-content">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <h2>Select a lead</h2>
              <p>Choose a lead from the sidebar to view details</p>
            </div>
          )}
        </main>
      </div>

      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New Lead</h2>
              <button 
                className="btn-icon"
                onClick={() => setShowAddModal(false)}
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"/>
                </svg>
              </button>
            </div>
            <form onSubmit={handleCreateLead} className="modal-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Company Name *</label>
                  <input
                    type="text"
                    value={newLead.company_name}
                    onChange={(e) => setNewLead({...newLead, company_name: e.target.value})}
                    required
                    placeholder="Acme Corp"
                  />
                </div>
                <div className="form-group">
                  <label>Contact Name *</label>
                  <input
                    type="text"
                    value={newLead.contact_name}
                    onChange={(e) => setNewLead({...newLead, contact_name: e.target.value})}
                    required
                    placeholder="John Doe"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={newLead.contact_email}
                    onChange={(e) => setNewLead({...newLead, contact_email: e.target.value})}
                    placeholder="john@acme.com"
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
              </div>

              <div className="form-group">
                <label>LinkedIn URL</label>
                <input
                  type="url"
                  value={newLead.contact_linkedin}
                  onChange={(e) => setNewLead({...newLead, contact_linkedin: e.target.value})}
                  placeholder="https://linkedin.com/in/johndoe"
                />
              </div>

              <div className="form-row">
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
                  <label>Company Size</label>
                  <select
                    value={newLead.company_size}
                    onChange={(e) => setNewLead({...newLead, company_size: e.target.value})}
                  >
                    <option value="">Select size</option>
                    <option value="1-10">1-10</option>
                    <option value="10-50">10-50</option>
                    <option value="50-200">50-200</option>
                    <option value="200-1000">200-1000</option>
                    <option value="1000+">1000+</option>
                  </select>
                </div>
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
                  {loading ? 'Creating...' : 'Create Lead'}
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