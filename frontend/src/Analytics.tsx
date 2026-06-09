import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const COLORS = ['#10b981', '#0ea5e9', '#f59e0b'];

const Analytics: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/footprint/history/user_123')
      .then(res => res.json())
      .then(resData => {
        setData(resData.history || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="glass-panel"><p>Loading analytics...</p></div>;

  const categoryTotals = data.reduce((acc, curr) => {
    acc[curr.category] = (acc[curr.category] || 0) + curr.calculated_co2;
    return acc;
  }, {});

  const pieData = Object.keys(categoryTotals).map(key => ({
    name: key,
    value: categoryTotals[key]
  }));

  const barData = data.slice(-5).map((d, i) => ({
    name: `Log ${i+1}`,
    co2: d.calculated_co2,
    category: d.category
  }));

  return (
    <div className="analytics-container">
      <div className="glass-panel">
        <h2>Emissions by Category</h2>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {pieData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        {/* Screen-reader data table fallback */}
        <table className="sr-only">
          <caption>Emissions by category data</caption>
          <thead><tr><th>Category</th><th>CO₂e (kg)</th></tr></thead>
          <tbody>
            {pieData.map(d => <tr key={d.name}><td>{d.name}</td><td>{d.value.toFixed(2)}</td></tr>)}
          </tbody>
        </table>
      </div>
      
      <div className="glass-panel">
        <h2>Recent Logs CO₂e</h2>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
              <Bar dataKey="co2" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {/* Screen-reader data table fallback */}
        <table className="sr-only">
          <caption>Recent logs data</caption>
          <thead><tr><th>Log</th><th>CO₂e (kg)</th></tr></thead>
          <tbody>
            {barData.map(d => <tr key={d.name}><td>{d.name}</td><td>{d.co2}</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Analytics;
