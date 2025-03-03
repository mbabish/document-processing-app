import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ReportData, ReportDocument } from '../types/report.types';
import DashboardOverview from './DashboardOverview';
import DocumentChart from './DocumentChart';
import FileUpload from './FileUpload';
import RecentDocuments from './RecentDocuments';

interface DashboardProps {}

const Dashboard = (props: DashboardProps): JSX.Element => {
  // State declarations with proper typing
  const [reportData, setReportData] = useState(null as ReportData | null);
  const [loading, setLoading] = useState(true as boolean);
  const [error, setError] = useState(null as string | null);
  const [recentlyUploadedDoc, setRecentlyUploadedDoc] = useState(null as ReportDocument | null);
  const [showUploadResult, setShowUploadResult] = useState(false as boolean);

  const fetchReportData = async (): Promise<void> => {
    try {
      const response = await axios.get<ReportData>(
        `/api/reports`
      );
      setReportData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch report data');
      setLoading(false);
      console.error(err);
    }
  };

  useEffect(() => {
    fetchReportData();
  }, []);

  const handleUploadSuccess = (document: ReportDocument) => {
    setRecentlyUploadedDoc(document);
    setShowUploadResult(true);
    
    // Reload the entire report data
    fetchReportData();
  };

  const handleReturnToDashboard = () => {
    setShowUploadResult(false);
  };

  if (loading) return <div>Loading dashboard data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!reportData) return <div>No data available</div>;

  return (
    <div className="dashboard">
      {/* Overview Section */}
      <DashboardOverview reportData={reportData} />

      {/* File Upload Section */}
      <div className="card">
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
                  <div>{recentlyUploadedDoc.schema_id}</div>
                </div>
                <div style={{ display: 'flex', marginBottom: '10px' }}>
                  <div style={{ width: '150px', fontWeight: 'bold' }}>Processed At:</div>
                  <div>{new Date(recentlyUploadedDoc.processed_at).toLocaleString()}</div>
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

      {/* Document Chart Section */}
      <DocumentChart reportData={reportData} />

      {/* Recent Documents Section */}
      <RecentDocuments reportData={reportData} />
    </div>
  );
};

export default Dashboard;