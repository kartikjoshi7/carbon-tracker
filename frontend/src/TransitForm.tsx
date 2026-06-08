import React, { useState } from 'react';

interface Props {
  onTrackStart: () => void;
  onTrackSuccess: (text: string) => void;
  onTrackError: () => void;
}

const TransitForm: React.FC<Props> = ({ onTrackStart, onTrackSuccess, onTrackError }) => {
  const [distance, setDistance] = useState<number>(0);
  const [mode, setMode] = useState<string>('shared_rickshaw');
  const [passengers, setPassengers] = useState<number>(1);
  const [co2, setCo2] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    onTrackStart();
    try {
      const res = await fetch('http://localhost:8000/api/v1/footprint/transit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          distance_km: distance,
          transport_mode: mode,
          passenger_count: passengers
        })
      });
      const data = await res.json();
      setCo2(data.calculated_co2);
      
      setTimeout(() => {
        onTrackSuccess(`Coordinating a shared commute to campus reduces your per-capita emission by ${data.calculated_co2}kg CO2e compared to riding alone!`);
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
      <h2>Transit Tracking</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Distance (km)</label>
          <input type="number" min="0" max="500" step="0.1" value={distance} onChange={e => setDistance(Number(e.target.value))} required />
        </div>
        <div className="form-group">
          <label>Transport Mode</label>
          <select value={mode} onChange={e => setMode(e.target.value)}>
            <option value="shared_rickshaw">Shared Rickshaw</option>
            <option value="campus_shuttle">Campus Shuttle</option>
            <option value="two_wheeler">Two Wheeler</option>
            <option value="walking">Walking</option>
          </select>
        </div>
        <div className="form-group">
          <label>Passenger Count</label>
          <input type="number" min="1" value={passengers} onChange={e => setPassengers(Number(e.target.value))} required />
        </div>
        <button type="submit" disabled={loading}>Track Transit</button>
      </form>
      
      {co2 !== null && (
        <div className="score-display">
          Calculated CO₂e: <span>{co2} kg</span>
        </div>
      )}
    </section>
  );
};

export default TransitForm;
