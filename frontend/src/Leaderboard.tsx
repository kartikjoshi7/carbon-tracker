import React, { useEffect, useState } from 'react';

const Leaderboard: React.FC = () => {
  const [leaders, setLeaders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/footprint/leaderboard')
      .then(res => res.json())
      .then(data => {
        setLeaders(data.leaderboard || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="glass-panel"><p>Loading leaderboard...</p></div>;

  return (
    <div className="glass-panel leaderboard-panel">
      <h2>🏆 Campus Eco-Warriors</h2>
      <p className="insight-muted" style={{marginBottom: '2rem'}}>Ranked by lowest total CO₂e footprint.</p>
      
      <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <th style={{ padding: '1rem', color: '#94a3b8' }}>Rank</th>
            <th style={{ padding: '1rem', color: '#94a3b8' }}>Student ID</th>
            <th style={{ padding: '1rem', color: '#94a3b8' }}>Total CO₂e (kg)</th>
          </tr>
        </thead>
        <tbody>
          {leaders.map((leader, index) => {
            let badge = '';
            if (index === 0) badge = '🥇';
            else if (index === 1) badge = '🥈';
            else if (index === 2) badge = '🥉';

            return (
              <tr key={index} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '1rem', fontSize: '1.25rem' }}>{badge} {index + 1}</td>
                <td style={{ padding: '1rem', fontWeight: 600 }}>{leader.user_id}</td>
                <td style={{ padding: '1rem', color: '#10b981', fontWeight: 'bold' }}>{leader.total_co2}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default Leaderboard;
