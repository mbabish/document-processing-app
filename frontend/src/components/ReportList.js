import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const ReportList = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSchema, setSelectedSchema] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const url = selectedSchema === 'all' 
          ? `${process.env.REACT_APP_API_URL}/api/reports`
          : `${process.env.REACT_APP_API_URL}/api/reports/${selectedSchema}`;
          
        const response = await axios.get(url);
        setReportData(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch report data');
        setLoading(false);
        console.error(err);
      }
    };

    fetchData();
  }, [selectedSchema]);

  if (loading) return <div>Loading reports...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!reportData) return <div>No data available</div>;

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.9) return 'tag tag-high';
    if (confidence >= 0.7) return 'tag tag-medium';
    return 'tag tag-low';
  };

  // Get schema options for filter
  const schemaOptions = Object.keys(reportData.schemas_used || {}).map(key => ({
    id: key,
    title: reportData.schemas_used[key].title
  }));

  const documents = reportData.document_list || [];

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <h2>Document Reports</h2>
          <div>
            <Link to="/">Back to Dashboard</Link>
            &nbsp; | &nbsp;
            <select 
              value={selectedSchema} 
              onChange={(e) => setSelectedSchema(e.target.value)}
            >
              <option value="all">All Schemas</option>
              {schemaOptions.map(schema => (
                <option key={schema.id} value={schema.id}>{schema.title}</option>
              ))}
            </select>
          </div>
        </div>
        
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Schema</th>
              <th>Processed At</th>
              <th>Confidence</th>
              <th>Fields</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.classification_id}>
                <td>{doc.filename}</td>
                <td>{doc.schema_title}</td>
                <td>{new Date(doc.processed_at).toLocaleString()}</td>
                <td>
                  <span className={getConfidenceClass(doc.confidence)}>
                    {(doc.confidence * 100).toFixed(1)}%
                  </span>
                </td>
                <td>{doc.fields_count || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportList;
