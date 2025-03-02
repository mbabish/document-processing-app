import React from 'react';
import { ReportData, ReportDocument } from '../types/report.types';
import DocumentChart from './DocumentChart';
import RecentDocuments from './RecentDocuments';
import FileUpload from './FileUpload';

interface MainViewProps {
  reportData: ReportData;
  onUploadSuccess: (document: ReportDocument) => void;
}

const MainView = ({ reportData, onUploadSuccess }: MainViewProps): JSX.Element => {
  return (
    <div>
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <h2>Upload Document</h2>
        </div>
        <div style={{ padding: '20px' }}>
          <FileUpload onUploadSuccess={onUploadSuccess} />
        </div>
      </div>
      
      <DocumentChart reportData={reportData} />
      <RecentDocuments documents={reportData.recent_classifications || []} />
    </div>
  );
};

export default MainView;