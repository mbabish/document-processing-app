import React from 'react';
import { ReportData } from '../types/report.types';

interface DashboardOverviewProps {
  reportData: ReportData;
}

const DashboardOverview = ({ reportData }: DashboardOverviewProps): JSX.Element => {
  return (
    <div>
      <div className="card-header">
        <h2>Dashboard Overview</h2>
        <p>Generated at: {new Date(reportData.generated_at).toLocaleString()}</p>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Documents</h3>
          <p>{reportData.total_documents}</p>
        </div>
        <div className="stat-card">
          <h3>Total Schemas</h3>
          <p>{Object.keys(reportData.schemas_used).length}</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
