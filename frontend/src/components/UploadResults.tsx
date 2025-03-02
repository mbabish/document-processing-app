import React from 'react';
import { ReportDocument } from '../types/report.types';

interface UploadResultsProps {
  document: ReportDocument;
  onReturnToUpload: () => void;
}

const UploadResults = ({ document, onReturnToUpload }: UploadResultsProps): JSX.Element => {
  return (
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
          <div>{document.filename}</div>
        </div>
        <div style={{ display: 'flex', marginBottom: '10px' }}>
          <div style={{ width: '150px', fontWeight: 'bold' }}>Document Type:</div>
          <div>{document.schema_title}</div>
        </div>
        <div style={{ display: 'flex', marginBottom: '10px' }}>
          <div style={{ width: '150px', fontWeight: 'bold' }}>Processed At:</div>
          <div>{new Date(document.processed_at).toLocaleString()}</div>
        </div>
        <div style={{ display: 'flex', marginBottom: '10px' }}>
          <div style={{ width: '150px', fontWeight: 'bold' }}>Fields Extracted:</div>
          <div>{document.fields_count || 'N/A'}</div>
        </div>
      </div>
      
      <button 
        onClick={onReturnToUpload}
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
  );
};

export default UploadResults;
