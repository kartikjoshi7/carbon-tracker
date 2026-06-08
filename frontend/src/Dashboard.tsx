import React, { useState } from 'react';
import EnergyForm from './EnergyForm';
import TransitForm from './TransitForm';
import WasteForm from './WasteForm';

export type InsightState = 'idle' | 'loading' | 'success';

const Dashboard: React.FC = () => {
  const [insightState, setInsightState] = useState<InsightState>('idle');
  const [insightText, setInsightText] = useState<string | null>(null);

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

  return (
    <main>
      <header className="hero-section">
        <h1 className="emerald-gradient-text">Smart Campus Sustainability Engine</h1>
        <p className="hero-subtitle">Real-time CO₂e tracking & AI-driven reduction strategies.</p>
      </header>

      <div className="dashboard-grid">
        <EnergyForm 
          onTrackStart={handleTrackStart} 
          onTrackSuccess={handleTrackSuccess} 
          onTrackError={handleTrackError} 
        />
        <TransitForm 
          onTrackStart={handleTrackStart} 
          onTrackSuccess={handleTrackSuccess} 
          onTrackError={handleTrackError} 
        />
        <WasteForm 
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
    </main>
  );
};

export default Dashboard;
