import React from 'react';
import { Link } from 'react-router-dom';
import { ReportDocument } from '../types/report.types';

interface RecentDocumentsProps {
  documents: ReportDocument[];
}

const RecentDocuments = ({ documents }: RecentDocumentsProps): JSX.Element => {
  return (
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
            {documents.map((doc: ReportDocument) => (
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
  );
};

export default RecentDocuments;
