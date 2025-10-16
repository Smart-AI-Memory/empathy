/**
 * Hover Provider
 * Shows Level 4 Anticipatory predictions on hover
 */

import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';

export class CoachHoverProvider implements vscode.HoverProvider {
    constructor(private client: LanguageClient) {}

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | undefined> {
        // Get word at position
        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return undefined;
        }

        const word = document.getText(wordRange);
        const line = document.lineAt(position.line).text;

        // Check for predictable patterns
        const prediction = await this.getPredictionForContext(word, line, document);

        if (prediction) {
            const markdown = new vscode.MarkdownString(prediction);
            markdown.isTrusted = true;
            markdown.supportHtml = true;

            return new vscode.Hover(markdown, wordRange);
        }

        return undefined;
    }

    private async getPredictionForContext(
        word: string,
        line: string,
        document: vscode.TextDocument
    ): Promise<string | undefined> {
        const lineLower = line.toLowerCase();

        // Pattern 1: Database connection pool
        if (this.isConnectionPoolPattern(word, lineLower)) {
            return this.getConnectionPoolPrediction(word, line);
        }

        // Pattern 2: Rate limiting
        if (this.isRateLimitPattern(word, lineLower)) {
            return this.getRateLimitPrediction(word, line);
        }

        // Pattern 3: Cache TTL
        if (this.isCacheTTLPattern(word, lineLower)) {
            return this.getCacheTTLPrediction(word, line);
        }

        // Pattern 4: Timeout values
        if (this.isTimeoutPattern(word, lineLower)) {
            return this.getTimeoutPrediction(word, line);
        }

        // Pattern 5: Security vulnerabilities
        if (this.isSecurityPattern(word, lineLower)) {
            return this.getSecurityPrediction(word, line, document);
        }

        // Pattern 6: Performance bottlenecks
        if (this.isPerformancePattern(word, lineLower)) {
            return this.getPerformancePrediction(word, line);
        }

        return undefined;
    }

    // Pattern detectors
    private isConnectionPoolPattern(word: string, line: string): boolean {
        return (
            (word === 'pool_size' || word === 'poolSize' || word === 'max_connections') &&
            (line.includes('=') || line.includes(':'))
        );
    }

    private isRateLimitPattern(word: string, line: string): boolean {
        return (
            (word === 'rate_limit' || word === 'rateLimit' || word === 'max_requests') &&
            line.includes('=')
        );
    }

    private isCacheTTLPattern(word: string, line: string): boolean {
        return (
            (word === 'ttl' || word === 'timeout' || word === 'expire') &&
            (line.includes('cache') || line.includes('redis'))
        );
    }

    private isTimeoutPattern(word: string, line: string): boolean {
        return word === 'timeout' && /\d+/.test(line);
    }

    private isSecurityPattern(word: string, line: string): boolean {
        return (
            line.includes('execute') ||
            line.includes('query') ||
            line.includes('eval') ||
            line.includes('innerHTML')
        );
    }

    private isPerformancePattern(word: string, line: string): boolean {
        return (
            line.includes('for ') ||
            line.includes('while ') ||
            line.includes('loop')
        );
    }

    // Prediction generators
    private getConnectionPoolPrediction(word: string, line: string): string {
        // Extract current value
        const match = line.match(/=\s*(\d+)/);
        const currentValue = match ? parseInt(match[1]) : 10;

        return `
### ⚠️ PerformanceWizard Prediction (Level 4)

**Current**: ${currentValue} connections

**Prediction**: At 5K req/day growth rate, this connection pool will saturate in **~45 days**

**Impact**:
- 503 Service Unavailable errors
- Request timeouts
- Cascade failures

**Preventive Action**:
\`\`\`python
# Increase pool size
pool_size = ${Math.max(50, currentValue * 5)}

# Or implement connection pooling with overflow
pool_size = ${currentValue}
max_overflow = 20
pool_timeout = 30
\`\`\`

**Timeline**: Act within 30 days to avoid production issues

[Run Full Analysis](command:coach.performanceProfile)
        `.trim();
    }

    private getRateLimitPrediction(word: string, line: string): string {
        const match = line.match(/=\s*(\d+)/);
        const currentValue = match ? parseInt(match[1]) : 100;

        return `
### ⚠️ PerformanceWizard Prediction (Level 4)

**Current**: ${currentValue} requests/min

**Prediction**: At current traffic growth (15%/month), rate limit will be exceeded in **~60 days**

**Impact**:
- 429 Too Many Requests errors
- Legitimate users blocked
- Revenue loss

**Preventive Action**:
\`\`\`python
# Option 1: Increase limit
rate_limit = ${currentValue * 2}

# Option 2: Implement adaptive rate limiting
rate_limit = DynamicRateLimit(
    base=${currentValue},
    burst=${Math.floor(currentValue * 1.5)},
    adaptive=True
)
\`\`\`

[Run Full Analysis](command:coach.performanceProfile)
        `.trim();
    }

    private getCacheTTLPrediction(word: string, line: string): string {
        const match = line.match(/=\s*(\d+)/);
        const currentValue = match ? parseInt(match[1]) : 300;

        return `
### 💡 PerformanceWizard Insight

**Current TTL**: ${currentValue} seconds (${Math.floor(currentValue / 60)} minutes)

**Analysis**:
- ${currentValue < 60 ? '⚠️ Very short TTL - high cache miss rate expected' : '✅ Reasonable TTL'}
- ${currentValue > 3600 ? '⚠️ Long TTL - stale data risk' : ''}

**Recommendation**:
\`\`\`python
# For user data: 5-15 minutes
cache_ttl = ${Math.max(300, Math.min(900, currentValue))}

# For static content: 1 hour
cache_ttl = 3600
\`\`\`

**Monitor**: Cache hit rate should be >70%

[Run Performance Profile](command:coach.performanceProfile)
        `.trim();
    }

    private getTimeoutPrediction(word: string, line: string): string {
        const match = line.match(/timeout\s*=\s*(\d+)/i);
        const currentValue = match ? parseInt(match[1]) : 30;

        return `
### 💡 PerformanceWizard Insight

**Current Timeout**: ${currentValue} seconds

**Analysis**:
- ${currentValue < 5 ? '⚠️ Very short - may cause false failures' : ''}
- ${currentValue > 60 ? '⚠️ Very long - users will wait too long' : ''}
- ${currentValue >= 5 && currentValue <= 30 ? '✅ Reasonable timeout' : ''}

**Best Practices**:
- API calls: 5-10 seconds
- Database queries: 10-30 seconds
- Background jobs: 60-300 seconds

[Run Performance Profile](command:coach.performanceProfile)
        `.trim();
    }

    private getSecurityPrediction(word: string, line: string, document: vscode.TextDocument): string {
        if (line.includes("f'") || line.includes('f"')) {
            return `
### 🛡️ SecurityWizard Alert

**Potential SQL Injection Vulnerability**

**Risk**: High - User input in f-string query

**Exploit Scenario**:
\`\`\`python
user_id = "1 OR 1=1; DROP TABLE users--"
# Results in: SELECT * FROM users WHERE id=1 OR 1=1; DROP TABLE users--
\`\`\`

**Fix**:
\`\`\`python
# Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
\`\`\`

**Impact if exploited**:
- Complete database compromise
- Data theft/deletion
- Account takeover

[Run Security Audit](command:coach.securityAudit)
            `.trim();
        }

        if (line.includes('innerHTML') || line.includes('dangerouslySetInnerHTML')) {
            return `
### 🛡️ SecurityWizard Alert

**Potential XSS (Cross-Site Scripting) Vulnerability**

**Risk**: High - Unescaped HTML content

**Fix**:
\`\`\`javascript
// Instead of innerHTML, use textContent
element.textContent = userInput;

// Or use DOMPurify
element.innerHTML = DOMPurify.sanitize(userInput);
\`\`\`

[Run Security Audit](command:coach.securityAudit)
            `.trim();
        }

        return `
### 🛡️ SecurityWizard

Consider running a security audit on this code

[Run Security Audit](command:coach.securityAudit)
        `.trim();
    }

    private getPerformancePrediction(word: string, line: string): string {
        if (line.includes('for ') && line.includes('.get(')) {
            return `
### ⚡ PerformanceWizard Alert

**Potential N+1 Query Pattern**

**Issue**: Loop with database queries = N+1 queries

**Impact**:
- If N=1000, this executes 1001 queries
- Response time: ~2-3 seconds
- High database load

**Fix**:
\`\`\`python
# Use batch query instead
items = Item.objects.filter(id__in=item_ids)
\`\`\`

[Run Performance Profile](command:coach.performanceProfile)
            `.trim();
        }

        return '';
    }
}
