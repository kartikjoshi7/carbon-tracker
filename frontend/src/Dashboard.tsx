import React from 'react';
import EnergyForm from './EnergyForm';
import TransitForm from './TransitForm';
import WasteForm from './WasteForm';

const Dashboard: React.FC = () => {
  return (
    <main>
      <h1>Smart Campus Sustainability Engine</h1>
      <div className="dashboard-grid">
        <EnergyForm />
        <TransitForm />
        <WasteForm />
      </div>
    </main>
  );
};

export default Dashboard;
