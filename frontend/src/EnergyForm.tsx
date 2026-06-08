import React, { useState } from 'react';

const EnergyForm: React.FC = () => {
  const [roommates, setRoommates] = useState<number>(1);
  const [acHours, setAcHours] = useState<number>(0);
  const [sharedKwh, setSharedKwh] = useState<number>(0);
  const [co2, setCo2] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [insight, setInsight] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setInsight(null);
    try {
      const res = await fetch('http://localhost:8000/api/v1/footprint/energy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          roommate_count: roommates,
          ac_hours_logged: acHours,
          shared_appliance_kwh: sharedKwh
        })
      });
      const data = await res.json();
      setCo2(data.calculated_co2);
      
      // Simulate polling/waiting for AI insight
      setTimeout(() => {
        setInsight("Talk to your roommates to optimize the split AC usage. Saving " + data.calculated_co2 + "kg CO2e lowers the Dabhoi PG electricity bill for everyone.");
        setLoading(false);
      }, 2000);

    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <section className="glass-panel">
      <h2>Energy Tracking</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Roommates Count</label>
          <input type="number" min="1" value={roommates} onChange={e => setRoommates(Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label>AC Hours Logged</label>
          <input type="number" min="0" max="24" step="0.1" value={acHours} onChange={e => setAcHours(Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label>Shared Appliance (kWh)</label>
          <input type="number" min="0" step="0.1" value={sharedKwh} onChange={e => setSharedKwh(Number(e.target.value))} required />
        </div>
        <button type="submit" disabled={loading}>Track Energy</button>
      </form>
      
      <div aria-live="polite">
        {co2 !== null && <div className="score-display">Calculated CO₂e: {co2} kg</div>}
        {loading && co2 !== null && (
          <div className="insight-card">
            <div className="skeleton skeleton-text"></div>
            <div className="skeleton skeleton-text short"></div>
          </div>
        )}
        {!loading && insight && (
          <div className="insight-card">
            <strong>Eco-Concierge:</strong> {insight}
          </div>
        )}
      </div>
    </section>
  );
};

export default EnergyForm;
