import React, { useState, useEffect } from 'react';
import EnergyForm from './EnergyForm';
import TransitForm from './TransitForm';
import WasteForm from './WasteForm';
import Analytics from './Analytics';
import Leaderboard from './Leaderboard';
import ReceiptUploader from './ReceiptUploader';

export type InsightState = 'idle' | 'loading' | 'success';

const Dashboard: React.FC = () => {
  const [insightState, setInsightState] = useState<InsightState>('idle');
  const [insightText, setInsightText] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'track' | 'analytics' | 'leaderboard'>('track');
  const [parsedEnergy, setParsedEnergy] = useState<number | undefined>(undefined);
  const [parsedTransit, setParsedTransit] = useState<number | undefined>(undefined);
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    let storedId = localStorage.getItem('anonymous_device_id');
    if (!storedId) {
      storedId = 'student_' + Math.random().toString(36).substring(7);
      localStorage.setItem('anonymous_device_id', storedId);
    }
    setUserId(storedId);
  }, []);

  const handleTrackStart = () => {
    setInsightState('loading');
    setInsightText(null);
  };

  const handleTrackSuccess = (text: string) => {
    setInsightState('success');
    setInsightText(text);
  };

  const handleTrackError = () => {
    setInsightState('idle');
    setInsightText("An error occurred while generating insights. Please try again.");
  };

  const handleParsed = (category: string, value: number) => {
    if (category === 'energy') setParsedEnergy(value);
    if (category === 'transit') setParsedTransit(value);
  };

  return (
    <>
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <main id="main-content">
      <header className="hero-section">
        <h1 className="emerald-gradient-text">Smart Campus Sustainability Engine</h1>
        <p className="hero-subtitle">Real-time CO₂e tracking & AI-driven reduction strategies.</p>
        
        <nav role="tablist" aria-label="Dashboard navigation" style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '1rem' }}>
          <button 
            role="tab" aria-selected={activeTab === 'track'}
            style={{ width: 'auto', background: activeTab === 'track' ? 'var(--accent)' : 'rgba(255,255,255,0.1)' }}
            onClick={() => setActiveTab('track')}
          >Track Footprint</button>
          <button 
            role="tab" aria-selected={activeTab === 'analytics'}
            style={{ width: 'auto', background: activeTab === 'analytics' ? 'var(--accent)' : 'rgba(255,255,255,0.1)' }}
            onClick={() => setActiveTab('analytics')}
          >Data Analytics</button>
          <button 
            role="tab" aria-selected={activeTab === 'leaderboard'}
            style={{ width: 'auto', background: activeTab === 'leaderboard' ? 'var(--accent)' : 'rgba(255,255,255,0.1)' }}
            onClick={() => setActiveTab('leaderboard')}
          >Leaderboard</button>
        </nav>
      </header>

      {activeTab === 'track' && (
        <>
          <ReceiptUploader onParsed={handleParsed} />
          <div className="dashboard-grid">
            <EnergyForm 
              userId={userId}
              onTrackStart={handleTrackStart} 
              onTrackSuccess={handleTrackSuccess} 
              onTrackError={handleTrackError}
              initialKwh={parsedEnergy}
            />
            <TransitForm 
              userId={userId}
              onTrackStart={handleTrackStart} 
              onTrackSuccess={handleTrackSuccess} 
              onTrackError={handleTrackError} 
              initialDistance={parsedTransit}
            />
            <WasteForm 
              userId={userId}
              onTrackStart={handleTrackStart} 
              onTrackSuccess={handleTrackSuccess} 
              onTrackError={handleTrackError} 
            />
          </div>

          <section className="global-insight-panel" aria-live="polite">
            <h2>AI Eco-Concierge Insights</h2>
            {insightState === 'idle' && (
              <p className="insight-muted">Submit a metric to receive personalized reduction strategies.</p>
            )}
            
            {insightState === 'loading' && (
              <div className="insight-loading">
                <div className="skeleton skeleton-text"></div>
                <div className="skeleton skeleton-text short"></div>
              </div>
            )}

            {insightState === 'success' && insightText && (
              <div className="insight-success">
                <strong>Eco-Concierge:</strong> {insightText}
              </div>
            )}
          </section>
        </>
      )}

      {activeTab === 'analytics' && <Analytics userId={userId} />}
      {activeTab === 'leaderboard' && <Leaderboard />}

    </main>
    </>
  );
};

export default Dashboard;
