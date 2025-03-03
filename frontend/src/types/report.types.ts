/**
 * Report-related type definitions
 */

export interface ReportDocument {
  classification_id: string;
  filename: string;
  schema_id: string;
  processed_at: string;
  confidence: number;
}

export interface SchemaUsageStats {
  title: string;
  count: number;
  percentage: number;
}

export interface FieldCoverage {
  count: number;
  total: number;
  coverage: number;
}

export interface SchemaFieldCoverage {
  fields: Record<string, FieldCoverage>;
  overall_coverage: number;
}

export interface ReportData {
  generated_at: string;
  total_documents: number;
  schemas_used: Record<string, SchemaUsageStats>;
  field_coverage: Record<string, SchemaFieldCoverage>;
  recent_classifications?: Array<ReportDocument>;
  document_list: Array<ReportDocument>;
}

export interface SchemaReportData {
  generated_at: string;
  schema_id: string;
  total_documents: number;
  field_coverage: Record<string, SchemaFieldCoverage>;
  document_list: Array<ReportDocument>;
}