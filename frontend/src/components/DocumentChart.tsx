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
  const schemaData: number[] = Object.keys(props.reportData.schemas_used).map(
    key => props.reportData.schemas_used[key].count
  );

  const schemaChartData: ChartData<'bar'> = {
    labels: schemaLabels,
    datasets: [
      {
        label: 'Documents by Schema',
        data: schemaData,
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
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
    </div>
  );
};

export default DocumentChart;