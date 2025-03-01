import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';

const Dashboard = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/reports`);
        setReportData(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch report data');
        setLoading(false);
        console.error(err);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading dashboard data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!reportData) return <div>No data available</div>;

  // Prepare data for schema usage chart
  const schemaLabels = Object.keys(reportData.schemas_used).map(
    key => reportData.schemas_used[key].title
  );
  const schemaData = Object.keys(reportData.schemas_used).map(
    key => reportData.schemas_used[key].count
  );

  const schemaChartData = {
    labels: schemaLabels,
    datasets: [
      {
        label: 'Documents by Schema',
        data: schemaData,
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
        ],
      },
    ],
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.9) return 'tag tag-high';
    if (confidence >= 0.7) return 'tag tag-medium';
    return 'tag tag-low';
  };

  return (
    <div>
      <div className="card">
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
            <h3>Average Confidence</h3>
            <p>{(reportData.confidence_metrics.average * 100).toFixed(1)}%</p>
          </div>
          <div className="stat-card">
            <h3>Schemas Used</h3>
            <p>{Object.keys(reportData.schemas_used).length}</p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Documents by Schema</h2>
        </div>
        <div style={{ height: '300px' }}>
          <Bar 
            data={schemaChartData}
            options={{
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Number of Documents'
                  }
                }
              }
            }}
          />
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Recent Documents</h2>
          <Link to="/reports">View All</Link>
        </div>
        <div>
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Schema</th>
                <th>Processed</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {reportData.recent_classifications?.map((doc) => (
                <tr key={doc.classification_id}>
                  <td>{doc.filename}</td>
                  <td>{doc.schema_title}</td>
                  <td>{new Date(doc.processed_at).toLocaleDateString()}</td>
                  <td>
                    <span className={getConfidenceClass(doc.confidence)}>
                      {(doc.confidence * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
