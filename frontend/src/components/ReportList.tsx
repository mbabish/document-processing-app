import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ReportData, SchemaReportData, ReportDocument } from '../types/report.types';

type ReportDataType = ReportData | SchemaReportData;

interface SchemaOption {
  id: string;
  title: string;
}

interface ReportListProps {}

const ReportList = (props: ReportListProps): JSX.Element => {
  const [reportData, setReportData] = useState(null as ReportDataType | null);
  const [loading, setLoading] = useState(true as boolean);
  const [error, setError] = useState(null as string | null);
  const [selectedSchema, setSelectedSchema] = useState('all' as string);

  useEffect(() => {
    const fetchData = async (): Promise<void> => {
      try {
        const url: string = selectedSchema === 'all' 
          ? `/api/reports`
          : `/api/reports/${selectedSchema}`;
          
        const response = await axios.get<ReportDataType>(url);
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

  // Get schema options for filter - check if schemas_used exists before mapping
  const schemaOptions: SchemaOption[] = 'schemas_used' in reportData 
    ? Object.keys(reportData.schemas_used).map(key => ({
        id: key,
        title: reportData.schemas_used[key].title
      }))
    : [];

  const documents: ReportDocument[] = reportData.document_list || [];

  const handleSchemaChange = (e: { target: { value: string } }): void => {
    setSelectedSchema(e.target.value);
  };

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
              onChange={handleSchemaChange}
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
              <th>Fields</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.classification_id}>
                <td>{doc.filename}</td>
                <td>{doc.schema_title}</td>
                <td>{new Date(doc.processed_at).toLocaleString()}</td>
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