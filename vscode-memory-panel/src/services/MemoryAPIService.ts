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
            timeout: config.timeout || 10000
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
            const options: http.RequestOptions = {
                hostname: this.config.host,
                port: this.config.port,
                path: path,
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
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
        let path = `/api/patterns?limit=${limit}`;
        if (classification) {
            path += `&classification=${classification}`;
        }
        return this.request<PatternSummary[]>('GET', path);
    }

    /**
     * Get a specific pattern
     */
    async getPattern(patternId: string): Promise<any> {
        return this.request<any>('GET', `/api/patterns/${patternId}`);
    }

    /**
     * Delete a pattern
     */
    async deletePattern(patternId: string): Promise<{ success: boolean }> {
        return this.request<{ success: boolean }>('DELETE', `/api/patterns/${patternId}`);
    }

    /**
     * Export patterns to file
     */
    async exportPatterns(
        classification?: Classification
    ): Promise<{ pattern_count: number; export_data: any }> {
        let path = '/api/patterns/export';
        if (classification) {
            path += `?classification=${classification}`;
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
