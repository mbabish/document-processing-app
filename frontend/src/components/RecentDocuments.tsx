import React from 'react';
import { Link } from 'react-router-dom';
import { ReportData, ReportDocument } from '../types/report.types';

interface RecentDocumentsProps {
  reportData: ReportData;
}

const RecentDocuments = (props: RecentDocumentsProps): JSX.Element => {
  return (
    <div className="card">
      <div className="card-header">
        <h2>Recent Documents</h2>
        <Link to="/reports">View All</Link>
      </div>
      <table>
        <thead>
          <tr>
            <th>Filename</th>
            <th>Schema</th>
            <th>Processed</th>
          </tr>
        </thead>
        <tbody>
          {props.reportData.document_list
            .sort((a, b) => 
              new Date(b.processed_at).getTime() - new Date(a.processed_at).getTime()
            )
            .slice(0, 5)
            .map((doc: ReportDocument) => (
              <tr key={doc.classification_id}>
                <td>{doc.filename}</td>
                <td>{doc.schema_id}</td>
                <td>{new Date(doc.processed_at).toLocaleDateString()}</td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default RecentDocuments;