/**
 * Structured Logging Framework for Empathy Website
 *
 * Features:
 * - Environment-aware log levels
 * - Structured JSON output for production
 * - Human-readable output for development
 * - Context propagation for request tracing
 * - Type-safe log methods
 *
 * Usage:
 *   import { logger } from '@/lib/logger';
 *   logger.info('User action', { userId: '123', action: 'login' });
 *   logger.error('Failed to process', { error: err.message });
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  [key: string]: unknown;
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: LogContext;
  service: string;
  environment: string;
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

class Logger {
  private service: string;
  private environment: string;
  private minLevel: LogLevel;

  constructor(service: string = 'empathy-website') {
    this.service = service;
    this.environment = process.env.NODE_ENV || 'development';
    this.minLevel = this.getMinLevel();
  }

  private getMinLevel(): LogLevel {
    const envLevel = process.env.LOG_LEVEL as LogLevel;
    if (envLevel && LOG_LEVELS[envLevel] !== undefined) {
      return envLevel;
    }
    // Default: debug in development, info in production
    return this.environment === 'production' ? 'info' : 'debug';
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.minLevel];
  }

  private formatEntry(level: LogLevel, message: string, context?: LogContext): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      service: this.service,
      environment: this.environment,
    };
  }

  private output(entry: LogEntry): void {
    // In production, output structured JSON
    if (this.environment === 'production') {
      const output = JSON.stringify(entry);
      switch (entry.level) {
        case 'error':
          console.error(output);
          break;
        case 'warn':
          console.warn(output);
          break;
        default:
          console.log(output);
      }
      return;
    }

    // In development, output human-readable format
    const contextStr = entry.context ? ` ${JSON.stringify(entry.context)}` : '';
    const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]`;

    switch (entry.level) {
      case 'error':
        console.error(`${prefix} ${entry.message}${contextStr}`);
        break;
      case 'warn':
        console.warn(`${prefix} ${entry.message}${contextStr}`);
        break;
      case 'debug':
        console.debug(`${prefix} ${entry.message}${contextStr}`);
        break;
      default:
        console.log(`${prefix} ${entry.message}${contextStr}`);
    }
  }

  debug(message: string, context?: LogContext): void {
    if (this.shouldLog('debug')) {
      this.output(this.formatEntry('debug', message, context));
    }
  }

  info(message: string, context?: LogContext): void {
    if (this.shouldLog('info')) {
      this.output(this.formatEntry('info', message, context));
    }
  }

  warn(message: string, context?: LogContext): void {
    if (this.shouldLog('warn')) {
      this.output(this.formatEntry('warn', message, context));
    }
  }

  error(message: string, context?: LogContext): void {
    if (this.shouldLog('error')) {
      this.output(this.formatEntry('error', message, context));
    }
  }

  /**
   * Create a child logger with additional context
   */
  child(context: LogContext): ChildLogger {
    return new ChildLogger(this, context);
  }
}

class ChildLogger {
  private parent: Logger;
  private context: LogContext;

  constructor(parent: Logger, context: LogContext) {
    this.parent = parent;
    this.context = context;
  }

  debug(message: string, context?: LogContext): void {
    this.parent.debug(message, { ...this.context, ...context });
  }

  info(message: string, context?: LogContext): void {
    this.parent.info(message, { ...this.context, ...context });
  }

  warn(message: string, context?: LogContext): void {
    this.parent.warn(message, { ...this.context, ...context });
  }

  error(message: string, context?: LogContext): void {
    this.parent.error(message, { ...this.context, ...context });
  }
}

// Export singleton instance
export const logger = new Logger();

// Export class for custom instances
export { Logger, ChildLogger };
export type { LogLevel, LogContext, LogEntry };
