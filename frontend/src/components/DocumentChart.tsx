import React from 'react';
import { Bar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';
import { ReportData } from '../types/report.types';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface DocumentChartProps {
  reportData: ReportData;
}

const DocumentChart = (props: DocumentChartProps): JSX.Element => {
  // Prepare data for schema usage chart
  const schemaLabels: string[] = Object.keys(props.reportData.schemas_used).map(
    key => props.reportData.schemas_used[key].title
  );
  
  // Add "Uncategorized" to schema labels
  const allLabels = [...schemaLabels, "Uncategorized"];

  // Get categorized document counts
  const categorizedCounts: number[] = Object.keys(props.reportData.schemas_used).map(
    key => props.reportData.schemas_used[key].count
  );
  
  // Calculate uncategorized count (assuming total_documents includes all documents)
  const totalDocuments = props.reportData.total_documents || 0;
  const categorizedTotal = categorizedCounts.reduce((sum, count) => sum + count, 0);
  const uncategorizedCount = Math.max(0, totalDocuments - categorizedTotal);
  
  // Combine categorized and uncategorized counts
  const allData = [...categorizedCounts, uncategorizedCount];

  const schemaChartData: ChartData<'bar'> = {
    labels: allLabels,
    datasets: [
      {
        label: 'Documents by Schema',
        data: allData,
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(153, 102, 255, 0.6)', // Color for uncategorized
        ],
      },
    ],
  };

  const chartOptions: ChartOptions<'bar'> = {
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Documents'
        }
      }
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Documents by Schema</h2>
      </div>
      <div style={{ height: '300px' }}>
        <Bar 
          data={schemaChartData}
          options={chartOptions}
        />
      </div>
      {uncategorizedCount > 0 && (
        <div className="card-footer text-muted">
          <small>{uncategorizedCount} documents are uncategorized ({Math.round((uncategorizedCount / totalDocuments) * 100)}% of total)</small>
        </div>
      )}
    </div>
  );
};

export default DocumentChart;