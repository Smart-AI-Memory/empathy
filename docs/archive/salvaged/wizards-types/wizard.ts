/**
 * Unified Wizard Types for SmartAI Memory
 * Provides consistent structure across all wizard implementations
 */

export interface WizardStep {
  id: string;
  title: string;
  description: string;
  component?: React.ComponentType<any>;
  isComplete: boolean;
  isOptional?: boolean;
}

export interface WizardConfig {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: 'training' | 'development' | 'analysis' | 'optimization';
  estimatedTime: string; // e.g., "5-10 minutes"
  steps: WizardStep[];
  exportFormats: ExportFormat[];
}

export interface ExportFormat {
  id: string;
  label: string;
  extension: string;
  mimeType: string;
}

export interface WizardData {
  wizardId: string;
  currentStep: number;
  completedSteps: string[];
  data: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface WizardExport {
  version: string;
  wizardId: string;
  data: WizardData;
  metadata: {
    exportedAt: Date;
    exportFormat: string;
  };
}

// Common wizard field types
export type FieldType =
  | 'text'
  | 'textarea'
  | 'select'
  | 'multiselect'
  | 'radio'
  | 'checkbox'
  | 'slider'
  | 'code'
  | 'file'
  | 'custom';

export interface WizardField {
  id: string;
  type: FieldType;
  label: string;
  placeholder?: string;
  description?: string;
  required?: boolean;
  validation?: (value: any) => string | null;
  options?: Array<{ value: string; label: string; description?: string }>;
  defaultValue?: any;
  min?: number;
  max?: number;
  step?: number;
}

// Wizard categories for the hub
export interface WizardCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  wizards: WizardConfig[];
}

// Analytics tracking
export interface WizardAnalytics {
  wizardId: string;
  userId?: string;
  sessionId: string;
  events: WizardEvent[];
}

export type WizardEventType =
  | 'wizard_started'
  | 'wizard_completed'
  | 'wizard_abandoned'
  | 'step_started'
  | 'step_completed'
  | 'step_skipped'
  | 'step_back'
  | 'field_focused'
  | 'field_changed'
  | 'field_blurred'
  | 'validation_error'
  | 'export_triggered'
  | 'export_completed'
  | 'data_saved'
  | 'data_loaded';

export interface WizardEvent {
  type: WizardEventType;
  timestamp: Date;
  stepId?: string;
  fieldId?: string;
  data?: Record<string, any>;
  timing?: WizardTimingMetrics;
}

export interface WizardTimingMetrics {
  duration?: number; // Duration in milliseconds
  stepStartTime?: number; // Timestamp when step started
  stepEndTime?: number; // Timestamp when step ended
  sessionStartTime?: number; // Timestamp when wizard session started
  totalSessionDuration?: number; // Total session duration in milliseconds
}

export interface WizardAnalyticsMetrics {
  wizardId: string;
  totalSessions: number;
  completedSessions: number;
  abandonedSessions: number;
  completionRate: number;
  averageCompletionTime: number; // in milliseconds
  averageTimePerStep: Record<string, number>; // stepId -> average time in ms
  dropOffByStep: Record<string, number>; // stepId -> drop off count
  popularityScore: number;
  lastUpdated: Date;
}

export interface WizardSessionAnalytics {
  sessionId: string;
  wizardId: string;
  userId?: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  completedSteps: string[];
  totalSteps: number;
  isCompleted: boolean;
  isAbandoned: boolean;
  lastStepVisited: string;
  fieldInteractions: number;
  validationErrors: number;
  navigationBackCount: number;
}

// Template system for common patterns
export interface WizardTemplate {
  id: string;
  name: string;
  description: string;
  prefilledData: Record<string, any>;
  tags: string[];
}
