/**
 * Memory API Service
 *
 * HTTP client for communicating with the Python backend Memory Control Panel.
 * Provides typed interfaces for all memory operations including Redis management,
 * pattern storage, and health monitoring.
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

import * as http from 'http';

/**
 * Classification levels for patterns (must match Python backend)
 */
export enum Classification {
    PUBLIC = 'PUBLIC',
    INTERNAL = 'INTERNAL',
    SENSITIVE = 'SENSITIVE'
}

/**
 * Redis status information
 */
export interface RedisStatus {
    status: 'running' | 'stopped';
    host: string;
    port: number;
    method: string;
}

/**
 * Long-term storage information
 */
export interface LongTermStatus {
    status: 'available' | 'not_initialized';
    storage_dir: string;
    pattern_count: number;
}

/**
 * Overall memory system status
 */
export interface MemoryStatus {
    timestamp: string;
    redis: RedisStatus;
    long_term: LongTermStatus;
    config: {
        auto_start_redis: boolean;
        audit_dir: string;
    };
}

/**
 * Memory statistics
 */
export interface MemoryStats {
    // Redis stats
    redis_available: boolean;
    redis_method: string;
    redis_keys_total: number;
    redis_keys_working: number;
    redis_keys_staged: number;
    redis_memory_used: string;

    // Long-term stats
    long_term_available: boolean;
    patterns_total: number;
    patterns_public: number;
    patterns_internal: number;
    patterns_sensitive: number;
    patterns_encrypted: number;

    // Timestamp
    collected_at: string;
}

/**
 * Pattern summary
 */
export interface PatternSummary {
    pattern_id: string;
    pattern_type: string;
    classification: Classification;
    created_at: string;
    updated_at?: string;
    user_id: string;
    encrypted: boolean;
}

/**
 * Health check result
 */
export interface HealthCheck {
    overall: 'healthy' | 'degraded' | 'unhealthy';
    checks: Array<{
        name: string;
        status: 'pass' | 'warn' | 'fail' | 'info';
        message: string;
    }>;
    recommendations: string[];
}

/**
 * API error response
 */
export interface APIError {
    error: string;
    message: string;
    status_code: number;
}

/**
 * Memory API Service Configuration
 */
export interface APIConfig {
    host: string;
    port: number;
    timeout: number; // milliseconds
    apiKey?: string; // Optional API key for authentication
}

// =============================================================================
// Input Validation
// =============================================================================

/**
 * Pattern ID validation regex - matches format: pat_YYYYMMDDHHMMSS_hexstring
 */
const PATTERN_ID_REGEX = /^pat_\d{14}_[a-f0-9]{8,16}$/;

/**
 * Alternative pattern ID format
 */
const PATTERN_ID_ALT_REGEX = /^[a-zA-Z][a-zA-Z0-9_-]{2,63}$/;

/**
 * Valid classifications
 */
const VALID_CLASSIFICATIONS = ['PUBLIC', 'INTERNAL', 'SENSITIVE'];

/**
 * Validate pattern ID to prevent path traversal and injection attacks.
 */
function validatePatternId(patternId: string): boolean {
    if (!patternId || typeof patternId !== 'string') {
        return false;
    }

    // Check for path traversal attempts
    if (patternId.includes('..') || patternId.includes('/') || patternId.includes('\\')) {
        return false;
    }

    // Check for null bytes
    if (patternId.includes('\x00')) {
        return false;
    }

    // Check length bounds
    if (patternId.length < 3 || patternId.length > 64) {
        return false;
    }

    // Must match one of the valid formats
    return PATTERN_ID_REGEX.test(patternId) || PATTERN_ID_ALT_REGEX.test(patternId);
}

/**
 * Validate agent ID format.
 */
function validateAgentId(agentId: string): boolean {
    if (!agentId || typeof agentId !== 'string') {
        return false;
    }

    // Check for dangerous characters
    const dangerous = ['.', '/', '\\', '\x00', ';', '|', '&'];
    if (dangerous.some(c => agentId.includes(c))) {
        return false;
    }

    // Check length bounds
    if (agentId.length < 1 || agentId.length > 64) {
        return false;
    }

    // Simple alphanumeric with some allowed chars
    return /^[a-zA-Z0-9_@.-]+$/.test(agentId);
}

/**
 * Validate classification parameter.
 */
function validateClassification(classification: string | undefined): boolean {
    if (classification === undefined) {
        return true;
    }
    if (typeof classification !== 'string') {
        return false;
    }
    return VALID_CLASSIFICATIONS.includes(classification.toUpperCase());
}

/**
 * Service for communicating with Memory Control Panel backend
 */
export class MemoryAPIService {
    private config: APIConfig;

    constructor(config: Partial<APIConfig> = {}) {
        this.config = {
            host: config.host || 'localhost',
            port: config.port || 8765,
            timeout: config.timeout || 10000,
            apiKey: config.apiKey
        };
    }

    /**
     * Update configuration
     */
    updateConfig(config: Partial<APIConfig>): void {
        this.config = { ...this.config, ...config };
    }

    /**
     * Make HTTP request to backend
     */
    private async request<T>(
        method: string,
        path: string,
        body?: any
    ): Promise<T> {
        return new Promise((resolve, reject) => {
            const headers: Record<string, string> = {
                'Content-Type': 'application/json'
            };

            // Add API key authentication if configured
            if (this.config.apiKey) {
                headers['Authorization'] = `Bearer ${this.config.apiKey}`;
            }

            const options: http.RequestOptions = {
                hostname: this.config.host,
                port: this.config.port,
                path: path,
                method: method,
                headers: headers,
                timeout: this.config.timeout
            };

            const req = http.request(options, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        const parsed = JSON.parse(data);

                        // Check for error responses
                        if (res.statusCode && res.statusCode >= 400) {
                            const error: APIError = {
                                error: parsed.error || 'Unknown error',
                                message: parsed.message || data,
                                status_code: res.statusCode
                            };
                            reject(error);
                            return;
                        }

                        resolve(parsed as T);
                    } catch (err) {
                        reject(new Error(`Failed to parse response: ${data}`));
                    }
                });
            });

            req.on('error', (err) => {
                reject(new Error(`Request failed: ${err.message}`));
            });

            req.on('timeout', () => {
                req.destroy();
                reject(new Error(`Request timeout after ${this.config.timeout}ms`));
            });

            if (body) {
                req.write(JSON.stringify(body));
            }

            req.end();
        });
    }

    /**
     * Get memory system status
     */
    async getStatus(): Promise<MemoryStatus> {
        return this.request<MemoryStatus>('GET', '/api/status');
    }

    /**
     * Get detailed statistics
     */
    async getStatistics(): Promise<MemoryStats> {
        return this.request<MemoryStats>('GET', '/api/stats');
    }

    /**
     * Start Redis if not running
     */
    async startRedis(): Promise<{ success: boolean; message: string }> {
        return this.request<{ success: boolean; message: string }>('POST', '/api/redis/start');
    }

    /**
     * Stop Redis (if we started it)
     */
    async stopRedis(): Promise<{ success: boolean; message: string }> {
        return this.request<{ success: boolean; message: string }>('POST', '/api/redis/stop');
    }

    /**
     * List patterns with optional filtering
     */
    async listPatterns(
        classification?: Classification,
        limit: number = 100
    ): Promise<PatternSummary[]> {
        // Validate classification
        if (classification && !validateClassification(classification)) {
            throw new Error('Invalid classification. Use PUBLIC, INTERNAL, or SENSITIVE.');
        }

        // Sanitize limit
        const safeLimit = Math.max(1, Math.min(limit, 1000));

        let path = `/api/patterns?limit=${safeLimit}`;
        if (classification) {
            path += `&classification=${encodeURIComponent(classification)}`;
        }
        return this.request<PatternSummary[]>('GET', path);
    }

    /**
     * Get a specific pattern
     */
    async getPattern(patternId: string): Promise<any> {
        // Validate pattern ID to prevent path traversal
        if (!validatePatternId(patternId)) {
            throw new Error('Invalid pattern ID format');
        }
        return this.request<any>('GET', `/api/patterns/${encodeURIComponent(patternId)}`);
    }

    /**
     * Delete a pattern
     */
    async deletePattern(patternId: string): Promise<{ success: boolean }> {
        // Validate pattern ID to prevent path traversal
        if (!validatePatternId(patternId)) {
            throw new Error('Invalid pattern ID format');
        }
        return this.request<{ success: boolean }>('DELETE', `/api/patterns/${encodeURIComponent(patternId)}`);
    }

    /**
     * Export patterns to file
     */
    async exportPatterns(
        classification?: Classification
    ): Promise<{ pattern_count: number; export_data: any }> {
        // Validate classification
        if (classification && !validateClassification(classification)) {
            throw new Error('Invalid classification. Use PUBLIC, INTERNAL, or SENSITIVE.');
        }

        let path = '/api/patterns/export';
        if (classification) {
            path += `?classification=${encodeURIComponent(classification)}`;
        }
        return this.request<{ pattern_count: number; export_data: any }>('GET', path);
    }

    /**
     * Run health check
     */
    async healthCheck(): Promise<HealthCheck> {
        return this.request<HealthCheck>('GET', '/api/health');
    }

    /**
     * Clear short-term memory for an agent
     */
    async clearShortTerm(agentId: string = 'admin'): Promise<{ keys_deleted: number }> {
        // Validate agent ID
        if (!validateAgentId(agentId)) {
            throw new Error('Invalid agent ID format');
        }
        return this.request<{ keys_deleted: number }>('POST', '/api/memory/clear', { agent_id: agentId });
    }

    /**
     * Check if API is reachable
     */
    async ping(): Promise<boolean> {
        try {
            await this.request<any>('GET', '/api/ping');
            return true;
        } catch (err) {
            return false;
        }
    }
}
