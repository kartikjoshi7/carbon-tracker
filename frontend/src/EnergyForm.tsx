import React, { useState } from 'react';

interface Props {
  onTrackStart: () => void;
  onTrackSuccess: (text: string) => void;
  onTrackError: () => void;
  initialKwh?: number;
}

const EnergyForm: React.FC<Props> = ({ onTrackStart, onTrackSuccess, onTrackError, initialKwh }) => {
  const [roommates, setRoommates] = useState<number>(3);
  const [acHours, setAcHours] = useState<number>(5.5);
  const [sharedKwh, setSharedKwh] = useState<number>(initialKwh || 120.5);
  const [co2, setCo2] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (initialKwh) setSharedKwh(initialKwh);
  }, [initialKwh]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    onTrackStart();
    try {
      const res = await fetch('/api/v1/footprint/energy', {
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
        onTrackSuccess(`Talk to your roommates to optimize the split AC usage. Saving ${data.calculated_co2}kg CO2e lowers the shared apartment electricity bill for everyone.`);
        setLoading(false);
      }, 2000);

    } catch (err) {
      console.error(err);
      onTrackError();
      setLoading(false);
    }
  };

  return (
    <section className="glass-panel">
      <h2>Energy Tracking</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="energy-roommates">Roommates Count</label>
          <input id="energy-roommates" type="number" min="1" value={roommates} onChange={e => setRoommates(Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label htmlFor="energy-ac-hours">AC Hours Logged</label>
          <input id="energy-ac-hours" type="number" min="0" max="24" step="0.1" value={acHours} onChange={e => setAcHours(Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label htmlFor="energy-shared-kwh">Shared Appliance (kWh)</label>
          <input id="energy-shared-kwh" type="number" min="0" step="0.1" value={sharedKwh} onChange={e => setSharedKwh(Number(e.target.value))} required />
        </div>
        <button type="submit" disabled={loading} aria-busy={loading}>Track Energy</button>
      </form>
      
      {co2 !== null && (
        <div className="score-display">
          Calculated CO₂e: <span>{co2} kg</span>
        </div>
      )}
    </section>
  );
};

export default EnergyForm;
