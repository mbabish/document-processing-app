import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';
import axios from 'axios';
import { ReportData, ReportDocument } from '../types/report.types';
import FileUpload from './FileUpload';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface DashboardProps {}

const Dashboard = (props: DashboardProps): JSX.Element => {
  // State declarations with proper typing
  const [reportData, setReportData] = useState(null as ReportData | null);
  const [loading, setLoading] = useState(true as boolean);
  const [error, setError] = useState(null as string | null);
  const [recentlyUploadedDoc, setRecentlyUploadedDoc] = useState(null as ReportDocument | null);
  const [showUploadResult, setShowUploadResult] = useState(false as boolean);

  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      try {
        const response = await axios.get<ReportData>(`/api/reports`);
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

  const handleUploadSuccess = (document: ReportDocument) => {
    setRecentlyUploadedDoc(document);
    setShowUploadResult(true);
    
    // If we have report data, add the new document to recent classifications
    if (reportData) {
      const updatedReportData = { 
        ...reportData,
        recent_classifications: [document, ...(reportData.recent_classifications || []).slice(0, 4)],
        total_documents: reportData.total_documents + 1
      };
      setReportData(updatedReportData);
    }
  };

  const handleReturnToDashboard = () => {
    setShowUploadResult(false);
  };

  if (loading) return <div>Loading dashboard data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!reportData) return <div>No data available</div>;

  // Prepare data for schema usage chart
  const schemaLabels: string[] = Object.keys(reportData.schemas_used).map(
    key => reportData.schemas_used[key].title
  );
  const schemaData: number[] = Object.keys(reportData.schemas_used).map(
    key => reportData.schemas_used[key].count
  );

  const schemaChartData: ChartData<'bar'> = {
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

  const chartOptions: ChartOptions<'bar'> = {
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
            <h3>Schemas Used</h3>
            <p>{Object.keys(reportData.schemas_used).length}</p>
          </div>
        </div>
        
        <div style={{ marginTop: '20px' }}>
          {showUploadResult && recentlyUploadedDoc ? (
            <div style={{ 
              padding: '20px', 
              backgroundColor: '#f8f9fa', 
              borderRadius: '4px',
              border: '1px solid #dee2e6'
            }}>
              <h3 style={{ marginTop: 0 }}>Document Processed Successfully</h3>
              
              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', marginBottom: '10px' }}>
                  <div style={{ width: '150px', fontWeight: 'bold' }}>Filename:</div>
                  <div>{recentlyUploadedDoc.filename}</div>
                </div>
                <div style={{ display: 'flex', marginBottom: '10px' }}>
                  <div style={{ width: '150px', fontWeight: 'bold' }}>Document Type:</div>
                  <div>{recentlyUploadedDoc.schema_title}</div>
                </div>
                <div style={{ display: 'flex', marginBottom: '10px' }}>
                  <div style={{ width: '150px', fontWeight: 'bold' }}>Processed At:</div>
                  <div>{new Date(recentlyUploadedDoc.processed_at).toLocaleString()}</div>
                </div>
                <div style={{ display: 'flex', marginBottom: '10px' }}>
                  <div style={{ width: '150px', fontWeight: 'bold' }}>Fields Extracted:</div>
                  <div>{recentlyUploadedDoc.fields_count || 'N/A'}</div>
                </div>
              </div>
              
              <button 
                onClick={handleReturnToDashboard}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#4682B4',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Return to Upload
              </button>
            </div>
          ) : (
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Documents by Schema</h2>
        </div>
        <div style={{ height: '300px' }}>
          <Bar 
            data={schemaChartData}
            options={chartOptions}
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
                <th>Fields</th>
              </tr>
            </thead>
            <tbody>
              {reportData.recent_classifications?.map((doc: ReportDocument) => (
                <tr key={doc.classification_id}>
                  <td>{doc.filename}</td>
                  <td>{doc.schema_title}</td>
                  <td>{new Date(doc.processed_at).toLocaleDateString()}</td>
                  <td>{doc.fields_count || 'N/A'}</td>
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
