import React, { useState } from 'react';
import axios from 'axios';

interface FileUploadProps {
  onUploadSuccess?: (document: any) => void;
}

const FileUpload = (props: FileUploadProps): JSX.Element => {
  const [file, setFile] = useState(null as File | null);
  const [uploading, setUploading] = useState(false as boolean);
  const [error, setError] = useState(null as string | null);
  const [success, setSuccess] = useState(null as string | null);

  const handleFileChange = (e: { target: { files: FileList | null } }): void => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleSubmit = async (e: { preventDefault: () => void }): Promise<void> => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    // Check file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      setSuccess('File uploaded successfully!');
      setFile(null);
      
      // If a callback was provided for successful uploads, call it with the document data
      if (props.onUploadSuccess && response.data.document) {
        props.onUploadSuccess(response.data.document);
      }
      
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Upload Document</h2>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '15px' }}>
            <label htmlFor="file-upload" style={{ display: 'block', marginBottom: '5px' }}>
              Select PDF Document:
            </label>
            <input
              id="file-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={{ 
                display: 'block',
                marginBottom: '10px',
                width: '100%' 
              }}
            />
            {file && (
              <div className="file-info" style={{ fontSize: '0.9em', color: '#666' }}>
                Selected file: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={!file || uploading}
            style={{
              padding: '8px 16px',
              backgroundColor: '#4682B4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: file && !uploading ? 'pointer' : 'not-allowed',
              opacity: file && !uploading ? 1 : 0.7
            }}
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
          
          {error && (
            <div className="error-message" style={{ color: '#d9534f', marginTop: '10px' }}>
              Error: {error}
            </div>
          )}
          
          {success && (
            <div className="success-message" style={{ color: '#5cb85c', marginTop: '10px' }}>
              {success}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default FileUpload;