import React, { useState } from 'react';
import { ReportDocument } from '../types/report.types';
import FileUpload from './FileUpload';
import UploadResults from './UploadResults';

interface UploadSectionProps {
  onUploadSuccess: (document: ReportDocument) => void;
}

const UploadSection = ({ onUploadSuccess }: UploadSectionProps): JSX.Element => {
  const [showUploadResult, setShowUploadResult] = useState(false as boolean);
  const [uploadedDocument, setUploadedDocument] = useState(null as ReportDocument | null);

  const handleUploadSuccess = (document: ReportDocument) => {
    setUploadedDocument(document);
    setShowUploadResult(true);
    onUploadSuccess(document);
  };

  const handleReturnToUpload = () => {
    setShowUploadResult(false);
  };

  return (
    <div style={{ marginTop: '20px' }}>
      {showUploadResult && uploadedDocument ? (
        <UploadResults 
          document={uploadedDocument} 
          onReturnToUpload={handleReturnToUpload} 
        />
      ) : (
        <FileUpload onUploadSuccess={handleUploadSuccess} />
      )}
    </div>
  );
};

export default UploadSection;