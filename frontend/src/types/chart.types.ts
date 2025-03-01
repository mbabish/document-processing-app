import { ChartData, ChartOptions } from 'chart.js';

export interface BarChartProps {
  data: ChartData;
  options?: ChartOptions;
  height?: number;
  width?: number;
}
