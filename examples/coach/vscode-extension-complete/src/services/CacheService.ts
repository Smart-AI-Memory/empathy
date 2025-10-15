import * as vscode from 'vscode';

interface CacheEntry {
    value: any;
    timestamp: number;
    accessCount: number;
    lastAccessed: number;
}

export class CacheService {
    private cache: Map<string, CacheEntry> = new Map();
    private maxSize: number = 1000;

    get(key: string): any | undefined {
        const config = vscode.workspace.getConfiguration('coach');
        if (!config.get('enableCaching')) {
            return undefined;
        }

        const entry = this.cache.get(key);
        if (!entry) {
            return undefined;
        }

        // Check expiration
        const expirationMs = (config.get<number>('cacheExpirationMinutes') || 60) * 60 * 1000;
        if (Date.now() - entry.timestamp > expirationMs) {
            this.cache.delete(key);
            return undefined;
        }

        // Update access metadata
        entry.accessCount++;
        entry.lastAccessed = Date.now();

        return entry.value;
    }

    set(key: string, value: any): void {
        const config = vscode.workspace.getConfiguration('coach');
        if (!config.get('enableCaching')) {
            return;
        }

        // Check size limit
        if (this.cache.size >= this.maxSize) {
            this.evictLRU();
        }

        this.cache.set(key, {
            value,
            timestamp: Date.now(),
            accessCount: 0,
            lastAccessed: Date.now()
        });
    }

    delete(key: string): void {
        this.cache.delete(key);
    }

    clear(): void {
        this.cache.clear();
    }

    invalidatePattern(pattern: RegExp): void {
        const keysToDelete: string[] = [];
        for (const key of this.cache.keys()) {
            if (pattern.test(key)) {
                keysToDelete.push(key);
            }
        }
        keysToDelete.forEach(key => this.cache.delete(key));
    }

    invalidateFile(filePath: string): void {
        const pattern = new RegExp(`^${this.escapeRegex(filePath)}:`);
        this.invalidatePattern(pattern);
    }

    getStatistics(): {
        size: number;
        maxSize: number;
        hitRate: number;
    } {
        const totalAccesses = Array.from(this.cache.values())
            .reduce((sum, entry) => sum + entry.accessCount, 0);

        return {
            size: this.cache.size,
            maxSize: this.maxSize,
            hitRate: totalAccesses > 0 ? this.cache.size / totalAccesses : 0
        };
    }

    private evictLRU(): void {
        let lruKey: string | undefined;
        let lruTime = Number.MAX_SAFE_INTEGER;

        for (const [key, entry] of this.cache.entries()) {
            if (entry.lastAccessed < lruTime) {
                lruTime = entry.lastAccessed;
                lruKey = key;
            }
        }

        if (lruKey) {
            this.cache.delete(lruKey);
        }
    }

    private escapeRegex(str: string): string {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}
