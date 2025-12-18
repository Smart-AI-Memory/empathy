/**
 * Debug Wizard Analysis API Route
 *
 * Handles bug analysis requests with:
 * - Error classification
 * - Historical pattern correlation
 * - Fix recommendations
 * - Tier-based access control
 */

export const dynamic = 'force-dynamic';

import {
  type AnalysisInput,
  type AnalysisResponse,
  type ErrorType,
  type ErrorClassification,
  type LikelyCause,
  type HistoricalMatch,
  type RecommendedFix,
  type Prediction,
  type MemoryBenefit,
} from '@/lib/debug-wizard/types';

import {
  DEFAULT_TIER,
  getTierLimits,
  validateFilesForTier,
} from '@/lib/debug-wizard/tiers';

// ============================================================================
// Error Pattern Classifiers (mirrors Python wizard)
// ============================================================================

const ERROR_PATTERNS: Record<ErrorType, RegExp[]> = {
  null_reference: [
    /cannot read property .* of (undefined|null)/i,
    /TypeError:.*undefined/i,
    /NoneType.*has no attribute/i,
    /null pointer/i,
    /undefined is not an object/i,
  ],
  type_mismatch: [
    /TypeError:.*expected.*got/i,
    /cannot assign.*to/i,
    /incompatible types/i,
    /type.*is not assignable/i,
  ],
  async_timing: [
    /promise.*rejected/i,
    /unhandled.*promise/i,
    /await.*undefined/i,
    /race condition/i,
    /cannot read.*before initialization/i,
  ],
  import_error: [
    /cannot find module/i,
    /ModuleNotFoundError/i,
    /ImportError/i,
    /no module named/i,
    /module not found/i,
  ],
  api_error: [
    /fetch.*failed/i,
    /network.*error/i,
    /connection.*refused/i,
    /timeout.*exceeded/i,
    /ECONNREFUSED/i,
  ],
  unknown: [],
};

// ============================================================================
// Likely Causes by Error Type
// ============================================================================

const CAUSES_BY_TYPE: Record<ErrorType, LikelyCause[]> = {
  null_reference: [
    {
      cause: 'Accessing property before data loads',
      check: 'Add null/undefined check before access',
      likelihood: 0.7,
    },
    {
      cause: 'API returned null unexpectedly',
      check: 'Verify API response structure',
      likelihood: 0.5,
    },
    {
      cause: 'Optional chaining missing',
      check: 'Use ?. operator or default values',
      likelihood: 0.6,
    },
  ],
  type_mismatch: [
    {
      cause: 'Wrong data type from API',
      check: 'Validate API response types',
      likelihood: 0.6,
    },
    {
      cause: 'Type conversion missing',
      check: 'Add explicit type conversion',
      likelihood: 0.5,
    },
  ],
  async_timing: [
    {
      cause: 'Missing await keyword',
      check: 'Verify all async calls are awaited',
      likelihood: 0.7,
    },
    {
      cause: 'Race condition in state updates',
      check: 'Use proper state management',
      likelihood: 0.5,
    },
  ],
  import_error: [
    {
      cause: 'Module not installed',
      check: 'Run npm install or pip install',
      likelihood: 0.8,
    },
    {
      cause: 'Wrong import path',
      check: 'Verify relative/absolute path',
      likelihood: 0.6,
    },
  ],
  api_error: [
    {
      cause: 'Network connectivity',
      check: 'Verify server is running',
      likelihood: 0.5,
    },
    {
      cause: 'CORS policy',
      check: 'Check server CORS configuration',
      likelihood: 0.6,
    },
  ],
  unknown: [
    {
      cause: 'Unknown error type',
      check: 'Review stack trace and error message',
      likelihood: 0.3,
    },
  ],
};

// ============================================================================
// Demo Historical Patterns (for website demonstration)
// ============================================================================

const DEMO_HISTORICAL_PATTERNS: HistoricalMatch[] = [
  {
    date: '2025-11-15',
    file: 'src/components/UserList.tsx',
    error_type: 'null_reference',
    root_cause: 'API returned undefined instead of empty array',
    fix_applied: 'Added optional chaining and default array fallback',
    fix_code: "const users = data?.users ?? [];",
    resolution_time_minutes: 15,
    similarity_score: 0.85,
    matching_factors: ['Same error type: null_reference', 'Same file type: .tsx'],
  },
  {
    date: '2025-10-28',
    file: 'src/api/fetchData.ts',
    error_type: 'async_timing',
    root_cause: 'Missing await on async function call',
    fix_applied: 'Added await keyword to async call',
    fix_code: "const result = await fetchData();",
    resolution_time_minutes: 5,
    similarity_score: 0.72,
    matching_factors: ['Same error type: async_timing'],
  },
  {
    date: '2025-09-12',
    file: 'src/utils/parser.py',
    error_type: 'import_error',
    root_cause: 'Package not in requirements.txt',
    fix_applied: 'Added package to dependencies and installed',
    fix_code: null,
    resolution_time_minutes: 3,
    similarity_score: 0.68,
    matching_factors: ['Same error type: import_error'],
  },
];

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Classify error based on message and stack trace
 */
function classifyError(errorMessage: string, stackTrace?: string): ErrorType {
  const combinedText = `${errorMessage} ${stackTrace || ''}`.toLowerCase();

  for (const [errorType, patterns] of Object.entries(ERROR_PATTERNS)) {
    if (errorType === 'unknown') continue;
    for (const pattern of patterns) {
      if (pattern.test(combinedText)) {
        return errorType as ErrorType;
      }
    }
  }

  return 'unknown';
}

/**
 * Get file extension from path
 */
function getFileExtension(filePath: string): string {
  const parts = filePath.split('.');
  return parts.length > 1 ? `.${parts[parts.length - 1]}` : 'unknown';
}

/**
 * Find matching historical patterns based on error
 */
function findHistoricalMatches(
  errorType: ErrorType,
  filePath: string,
  maxMatches: number
): HistoricalMatch[] {
  const fileExt = getFileExtension(filePath);

  // Filter and adjust similarity scores based on current error
  const matches = DEMO_HISTORICAL_PATTERNS
    .map((pattern) => {
      let adjustedScore = pattern.similarity_score;
      const newFactors = [...pattern.matching_factors];

      // Boost score if same error type
      if (pattern.error_type === errorType) {
        adjustedScore += 0.1;
      }

      // Boost score if same file extension
      if (getFileExtension(pattern.file) === fileExt) {
        adjustedScore += 0.05;
        if (!newFactors.some(f => f.includes('file type'))) {
          newFactors.push(`Same file type: ${fileExt}`);
        }
      }

      return {
        ...pattern,
        similarity_score: Math.min(adjustedScore, 1.0),
        matching_factors: newFactors,
      };
    })
    .filter((p) => p.similarity_score > 0.3)
    .sort((a, b) => b.similarity_score - a.similarity_score)
    .slice(0, maxMatches);

  return matches;
}

/**
 * Generate fix recommendation from best match
 */
function generateFixRecommendation(
  bestMatch: HistoricalMatch,
  currentFilePath: string
): RecommendedFix {
  const adaptationNotes: string[] = [];

  if (bestMatch.file !== currentFilePath) {
    const originalFile = bestMatch.file.split('/').pop() || bestMatch.file;
    const currentFile = currentFilePath.split('/').pop() || currentFilePath;
    adaptationNotes.push(
      `Original fix was in ${originalFile}, adapt for ${currentFile}`
    );
  }

  if (bestMatch.similarity_score < 0.8) {
    adaptationNotes.push(
      'Moderate similarity - verify fix applies to your specific case'
    );
  }

  return {
    based_on: `Historical bug from ${bestMatch.date}`,
    original_fix: bestMatch.fix_applied,
    fix_code: bestMatch.fix_code,
    expected_resolution_time: `${bestMatch.resolution_time_minutes} minutes`,
    confidence: bestMatch.similarity_score,
    adaptation_notes: adaptationNotes,
  };
}

/**
 * Generate Level 4 predictions
 */
function generatePredictions(
  errorType: ErrorType,
  historicalMatches: HistoricalMatch[]
): Prediction[] {
  const predictions: Prediction[] = [];

  // Null reference cluster prediction
  if (errorType === 'null_reference') {
    predictions.push({
      type: 'related_null_errors',
      severity: 'medium',
      description:
        'Based on patterns, null reference errors often cluster. ' +
        'Check similar components for the same issue.',
      prevention_steps: [
        'Add defensive null checks across related files',
        'Consider TypeScript strict null checks',
        'Review API contract for nullable fields',
      ],
    });
  }

  // Resolution time estimate
  if (historicalMatches.length >= 2) {
    const avgTime =
      historicalMatches.slice(0, 3).reduce((sum, m) => sum + m.resolution_time_minutes, 0) /
      Math.min(historicalMatches.length, 3);

    predictions.push({
      type: 'resolution_time_estimate',
      severity: 'info',
      description: `Based on ${historicalMatches.length} similar past bugs, expect ~${Math.round(avgTime)} minute resolution time.`,
      prevention_steps: [],
    });
  }

  // Recurring pattern warning
  const sameTypeCount = historicalMatches.filter(
    (m) => m.error_type === errorType
  ).length;
  if (sameTypeCount >= 2) {
    predictions.push({
      type: 'recurring_pattern',
      severity: 'high',
      description:
        `This error type has occurred ${sameTypeCount} times before. ` +
        'Consider a systematic fix to prevent recurrence.',
      prevention_steps: [
        'Add linting rule to catch this pattern',
        'Create code review checklist item',
        'Consider architectural change to eliminate root cause',
      ],
    });
  }

  return predictions;
}

/**
 * Generate recommendations
 */
function generateRecommendations(
  classification: ErrorClassification,
  historicalMatches: HistoricalMatch[],
  recommendedFix: RecommendedFix | null
): string[] {
  const recommendations: string[] = [];

  // Historical match recommendation
  if (recommendedFix) {
    recommendations.push(
      `Historical match found! Try: ${recommendedFix.original_fix}`
    );
    if (recommendedFix.fix_code) {
      recommendations.push(
        `Example fix code available from ${recommendedFix.based_on}`
      );
    }
  }

  // Likely cause recommendations
  for (const cause of classification.likely_causes.slice(0, 2)) {
    recommendations.push(`Check: ${cause.cause} - ${cause.check}`);
  }

  // Memory benefit reminder
  if (historicalMatches.length > 0) {
    recommendations.push(
      `Memory saved you time: ${historicalMatches.length} similar bugs found instantly`
    );
  } else {
    recommendations.push(
      'Tip: After fixing, resolution will be stored for future reference'
    );
  }

  return recommendations;
}

/**
 * Calculate memory benefit metrics
 */
function calculateMemoryBenefit(
  historicalMatches: HistoricalMatch[]
): MemoryBenefit {
  if (historicalMatches.length === 0) {
    return {
      matches_found: 0,
      time_saved_estimate: 'N/A - no historical data yet',
      value_statement: 'Once resolved, this bug will help future debugging',
      historical_insight: null,
    };
  }

  const avgResolution =
    historicalMatches.slice(0, 3).reduce((sum, m) => sum + m.resolution_time_minutes, 0) /
    Math.min(historicalMatches.length, 3);

  const timeSaved = Math.round(avgResolution * 0.6); // 60% time savings estimate

  return {
    matches_found: historicalMatches.length,
    time_saved_estimate: `~${timeSaved} minutes`,
    value_statement:
      `Persistent memory found ${historicalMatches.length} similar bugs. ` +
      "Without memory, you'd start from zero every time.",
    historical_insight: historicalMatches[0]?.fix_applied || null,
  };
}

/**
 * Generate a unique bug ID
 */
function generateBugId(): string {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const hash = Math.random().toString(36).substring(2, 10);
  return `bug_${date}_${hash}`;
}

// ============================================================================
// API Route Handler
// ============================================================================

export async function POST(request: Request): Promise<Response> {
  try {
    const body: AnalysisInput = await request.json();
    const {
      error_message,
      file_path,
      stack_trace,
      line_number,
      code_snippet: _code_snippet,
      correlate_with_history = true,
      file_contents,
    } = body;

    // Validate required fields
    if (!error_message) {
      return Response.json(
        {
          success: false,
          error: 'error_message is required',
        } as AnalysisResponse,
        { status: 400 }
      );
    }

    // Get tier (default to FREE for unauthenticated requests)
    // TODO: Implement actual auth check
    const tier = DEFAULT_TIER;
    const limits = getTierLimits(tier);

    // Validate files if provided
    if (file_contents && file_contents.length > 0) {
      const validation = validateFilesForTier(tier, file_contents);
      if (!validation.valid) {
        return Response.json(
          {
            success: false,
            error: validation.errors.join('; '),
            tier,
          } as AnalysisResponse,
          { status: 400 }
        );
      }
    }

    // Step 1: Classify the error
    const errorType = classifyError(error_message, stack_trace);

    // Step 2: Build error classification
    const classification: ErrorClassification = {
      error_type: errorType,
      error_message,
      file_path: file_path || 'unknown',
      line_number: line_number || null,
      file_type: file_path ? getFileExtension(file_path) : 'unknown',
      likely_causes: CAUSES_BY_TYPE[errorType] || CAUSES_BY_TYPE.unknown,
    };

    // Step 3: Find historical matches (if enabled and tier allows)
    let historicalMatches: HistoricalMatch[] = [];
    let recommendedFix: RecommendedFix | null = null;

    if (correlate_with_history && limits.historicalCorrelationEnabled) {
      historicalMatches = findHistoricalMatches(
        errorType,
        file_path || '',
        limits.maxHistoricalMatches
      );

      if (historicalMatches.length > 0) {
        recommendedFix = generateFixRecommendation(
          historicalMatches[0],
          file_path || ''
        );
      }
    }

    // Step 4: Generate predictions (if tier allows)
    const predictions = limits.advancedPredictionsEnabled
      ? generatePredictions(errorType, historicalMatches)
      : [];

    // Step 5: Generate recommendations
    const recommendations = generateRecommendations(
      classification,
      historicalMatches,
      recommendedFix
    );

    // Step 6: Calculate memory benefit
    const memoryBenefit = calculateMemoryBenefit(historicalMatches);

    // Step 7: Generate bug ID for tracking
    const bugId = generateBugId();

    // Build response
    const result: AnalysisResponse = {
      success: true,
      data: {
        error_classification: classification,
        historical_matches: historicalMatches,
        historical_correlation_enabled: correlate_with_history,
        matches_found: historicalMatches.length,
        recommended_fix: recommendedFix,
        predictions,
        recommendations,
        confidence: recommendedFix?.confidence || 0.5,
        memory_benefit: memoryBenefit,
        bug_id: bugId,
      },
      tier,
      usage: {
        requests_used: 1, // TODO: Track actual usage
        requests_limit: limits.dailyRequestLimit || Infinity,
        storage_used_mb: 0, // TODO: Track actual storage
        storage_limit_mb: limits.patternStorageMB || Infinity,
      },
    };

    return Response.json(result);
  } catch (error) {
    console.error('Debug wizard analysis error:', error);

    return Response.json(
      {
        success: false,
        error: 'Internal server error',
      } as AnalysisResponse,
      { status: 500 }
    );
  }
}
