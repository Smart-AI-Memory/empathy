/**
 * Wizard Service
 * Client-side service for interacting with wizard APIs
 */

import { WizardData, WizardExport, WizardEventType, WizardTimingMetrics } from '@/types/wizard';

export interface SaveWizardSessionParams {
  userId: string;
  wizardId: string;
  data: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface UpdateWizardSessionParams {
  sessionId: string;
  data: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface TrackEventParams {
  event: WizardEventType;
  wizardId: string;
  userId?: string;
  sessionId?: string;
  stepId?: string;
  fieldId?: string;
  timing?: WizardTimingMetrics;
  metadata?: Record<string, any>;
}

class WizardService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api';
  }

  /**
   * Save a new wizard session to the server
   */
  async saveSession(params: SaveWizardSessionParams): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/wizards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error('Failed to save wizard session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving wizard session:', error);
      throw error;
    }
  }

  /**
   * Retrieve all wizard sessions for a user
   */
  async getSessions(userId: string): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/wizards?userId=${userId}`);

      if (!response.ok) {
        throw new Error('Failed to fetch wizard sessions');
      }

      const data = await response.json();
      return data.sessions;
    } catch (error) {
      console.error('Error fetching wizard sessions:', error);
      throw error;
    }
  }

  /**
   * Retrieve a specific wizard session
   */
  async getSession(sessionId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/wizards/${sessionId}`);

      if (!response.ok) {
        throw new Error('Failed to fetch wizard session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching wizard session:', error);
      throw error;
    }
  }

  /**
   * Update an existing wizard session
   */
  async updateSession(params: UpdateWizardSessionParams): Promise<any> {
    try {
      const { sessionId, ...body } = params;
      const response = await fetch(`${this.baseUrl}/wizards/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error('Failed to update wizard session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating wizard session:', error);
      throw error;
    }
  }

  /**
   * Delete a wizard session
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/wizards/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete wizard session');
      }
    } catch (error) {
      console.error('Error deleting wizard session:', error);
      throw error;
    }
  }

  /**
   * Track an analytics event
   */
  async trackEvent(params: TrackEventParams): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/analytics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        console.warn('Failed to track analytics event');
      }
    } catch (error) {
      // Don't throw errors for analytics failures
      console.warn('Error tracking analytics event:', error);
    }
  }

  /**
   * Export wizard data to localStorage (fallback)
   */
  exportToLocalStorage(wizardId: string, data: WizardData): void {
    try {
      const key = `wizard_${wizardId}`;
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }

  /**
   * Import wizard data from localStorage (fallback)
   */
  importFromLocalStorage(wizardId: string): WizardData | null {
    try {
      const key = `wizard_${wizardId}`;
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error loading from localStorage:', error);
      return null;
    }
  }

  /**
   * Clear wizard data from localStorage
   */
  clearLocalStorage(wizardId: string): void {
    try {
      const key = `wizard_${wizardId}`;
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }

  /**
   * Get all wizard sessions from localStorage
   */
  getAllFromLocalStorage(): Record<string, WizardData> {
    try {
      const sessions: Record<string, WizardData> = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('wizard_')) {
          const data = localStorage.getItem(key);
          if (data) {
            const wizardId = key.replace('wizard_', '');
            sessions[wizardId] = JSON.parse(data);
          }
        }
      }
      return sessions;
    } catch (error) {
      console.error('Error loading from localStorage:', error);
      return {};
    }
  }

  /**
   * Track field-level interaction
   */
  async trackFieldInteraction(
    event: 'field_focused' | 'field_changed' | 'field_blurred',
    wizardId: string,
    sessionId: string,
    stepId: string,
    fieldId: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    return this.trackEvent({
      event,
      wizardId,
      sessionId,
      stepId,
      fieldId,
      metadata,
    });
  }

  /**
   * Track step timing
   */
  async trackStepTiming(
    wizardId: string,
    sessionId: string,
    stepId: string,
    timing: WizardTimingMetrics
  ): Promise<void> {
    return this.trackEvent({
      event: 'step_completed',
      wizardId,
      sessionId,
      stepId,
      timing,
    });
  }

  /**
   * Track wizard session start
   */
  async trackWizardStart(
    wizardId: string,
    sessionId: string,
    userId?: string
  ): Promise<void> {
    return this.trackEvent({
      event: 'wizard_started',
      wizardId,
      sessionId,
      userId,
      timing: {
        sessionStartTime: Date.now(),
      },
    });
  }

  /**
   * Track wizard session completion
   */
  async trackWizardComplete(
    wizardId: string,
    sessionId: string,
    sessionStartTime: number,
    userId?: string
  ): Promise<void> {
    const now = Date.now();
    return this.trackEvent({
      event: 'wizard_completed',
      wizardId,
      sessionId,
      userId,
      timing: {
        sessionStartTime,
        totalSessionDuration: now - sessionStartTime,
      },
    });
  }

  /**
   * Track wizard abandonment
   */
  async trackWizardAbandon(
    wizardId: string,
    sessionId: string,
    currentStepId: string,
    sessionStartTime: number,
    userId?: string
  ): Promise<void> {
    const now = Date.now();
    return this.trackEvent({
      event: 'wizard_abandoned',
      wizardId,
      sessionId,
      stepId: currentStepId,
      userId,
      timing: {
        sessionStartTime,
        totalSessionDuration: now - sessionStartTime,
      },
    });
  }

  /**
   * Get analytics metrics for a specific wizard
   */
  async getWizardMetrics(wizardId: string, dateRange?: { start: Date; end: Date }): Promise<any> {
    try {
      const params = new URLSearchParams({ wizardId });
      if (dateRange) {
        params.append('startDate', dateRange.start.toISOString());
        params.append('endDate', dateRange.end.toISOString());
      }

      const response = await fetch(`${this.baseUrl}/analytics/wizards/metrics?${params}`);

      if (!response.ok) {
        throw new Error('Failed to fetch wizard metrics');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching wizard metrics:', error);
      throw error;
    }
  }

  /**
   * Get analytics for all wizards
   */
  async getAllWizardMetrics(dateRange?: { start: Date; end: Date }): Promise<any> {
    try {
      const params = new URLSearchParams();
      if (dateRange) {
        params.append('startDate', dateRange.start.toISOString());
        params.append('endDate', dateRange.end.toISOString());
      }

      const response = await fetch(`${this.baseUrl}/analytics/wizards/all?${params}`);

      if (!response.ok) {
        throw new Error('Failed to fetch all wizard metrics');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching all wizard metrics:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const wizardService = new WizardService();
