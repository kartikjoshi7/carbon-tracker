import React, { useState } from 'react';

interface Props {
  onTrackStart: () => void;
  onTrackSuccess: (text: string) => void;
  onTrackError: () => void;
}

const WasteForm: React.FC<Props> = ({ onTrackStart, onTrackSuccess, onTrackError }) => {
  const [mealType, setMealType] = useState<string>('lunch');
  const [grams, setGrams] = useState<number>(250);
  const [co2, setCo2] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    onTrackStart();
    try {
      const res = await fetch('http://localhost:8000/api/v1/footprint/waste', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          meal_type: mealType,
          estimated_waste_grams: grams
        })
      });
      const data = await res.json();
      setCo2(data.calculated_co2);
      
      setTimeout(() => {
        onTrackSuccess(`University cafeteria portions are large. Saving ${grams}g of food lowers waste footprint by ${data.calculated_co2}kg CO2e.`);
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
      <h2>Waste Tracking</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="waste-meal-type">Meal Type</label>
          <select id="waste-meal-type" value={mealType} onChange={e => setMealType(e.target.value)}>
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="waste-grams">Estimated Waste (grams)</label>
          <input id="waste-grams" type="number" min="0" max="5000" step="0.1" value={grams} onChange={e => setGrams(Number(e.target.value))} required />
        </div>
        <button type="submit" disabled={loading} aria-busy={loading}>Track Waste</button>
      </form>
      
      {co2 !== null && (
        <div className="score-display">
          Calculated CO₂e: <span>{co2} kg</span>
        </div>
      )}
    </section>
  );
};

export default WasteForm;
