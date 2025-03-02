import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ReportData, ReportDocument } from '../types/report.types';
import DashboardOverview from './DashboardOverview';
import MainView from './MainView';
import UploadResults from './UploadResults';

interface DashboardProps {}

const Dashboard = (props: DashboardProps): JSX.Element => {
  // State declarations with proper typing
  const [reportData, setReportData] = useState(null as ReportData | null);
  const [loading, setLoading] = useState(true as boolean);
  const [error, setError] = useState(null as string | null);
  const [showUploadResult, setShowUploadResult] = useState(false as boolean);
  const [uploadedDocument, setUploadedDocument] = useState(null as ReportDocument | null);

  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      try {
        const response = await axios.get<ReportData>(`${process.env.REACT_APP_API_URL}/api/reports`);
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
    // Store the uploaded document
    setUploadedDocument(document);
    
    // Show upload result
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
    
    // After 5 seconds, switch back to main view
    setTimeout(() => {
      setShowUploadResult(false);
    }, 5000);
  };

  const handleReturnToMainView = () => {
    setShowUploadResult(false);
  };

  if (loading) return <div>Loading dashboard data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!reportData) return <div>No data available</div>;

  return (
    <div>
      <div className="card">
        <DashboardOverview reportData={reportData} />
      </div>

      {showUploadResult && uploadedDocument ? (
        <div style={{ marginTop: '20px' }}>
          <UploadResults 
            document={uploadedDocument} 
            onReturnToUpload={handleReturnToMainView} 
          />
        </div>
      ) : (
        <div style={{ marginTop: '20px' }}>
          <MainView reportData={reportData} onUploadSuccess={handleUploadSuccess} />
        </div>
      )}
    </div>
  );
};

export default Dashboard;