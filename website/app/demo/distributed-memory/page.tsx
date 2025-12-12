'use client';

import { useState } from 'react';
import Link from 'next/link';

// Demo data for the interactive visualization
const DEMO_AGENTS = [
  { id: 'code_reviewer', name: 'Code Reviewer', patterns: 12, status: 'active', color: '#6366f1' },
  { id: 'test_generator', name: 'Test Generator', patterns: 8, status: 'active', color: '#22c55e' },
  { id: 'security_analyzer', name: 'Security Analyzer', patterns: 15, status: 'active', color: '#f59e0b' },
];

const DEMO_PATTERNS = [
  { id: 'pat_001', name: 'Use list comprehension', type: 'performance', confidence: 0.85, agent: 'code_reviewer' },
  { id: 'pat_002', name: 'Add null checks', type: 'best_practice', confidence: 0.92, agent: 'code_reviewer' },
  { id: 'pat_003', name: 'Mock external services', type: 'testing', confidence: 0.78, agent: 'test_generator' },
  { id: 'pat_004', name: 'SQL injection prevention', type: 'security', confidence: 0.95, agent: 'security_analyzer' },
  { id: 'pat_005', name: 'Use explicit loop', type: 'style', confidence: 0.80, agent: 'code_reviewer' },
];

const RESOLUTION_STRATEGIES = [
  { id: 'highest_confidence', name: 'Highest Confidence', description: 'Pick pattern with highest confidence score' },
  { id: 'most_recent', name: 'Most Recent', description: 'Pick most recently discovered pattern' },
  { id: 'best_context_match', name: 'Best Context Match', description: 'Pick best match for current context' },
  { id: 'team_priority', name: 'Team Priority', description: 'Use team-configured priorities' },
  { id: 'weighted_score', name: 'Weighted Score', description: 'Combine all factors (default)' },
];

export default function DistributedMemoryDemo() {
  const [selectedStrategy, setSelectedStrategy] = useState('weighted_score');
  const [teamPriority, setTeamPriority] = useState('balanced');
  const [conflictPatterns, setConflictPatterns] = useState<string[]>(['pat_001', 'pat_005']);
  const [resolutionResult, setResolutionResult] = useState<{
    winner: string;
    reasoning: string;
    scores: Record<string, number>;
  } | null>(null);

  const resolveConflict = () => {
    const patterns = conflictPatterns.map(id => DEMO_PATTERNS.find(p => p.id === id)!);

    // Simulate resolution logic
    let winner: typeof DEMO_PATTERNS[0];
    let reasoning: string;
    let scores: Record<string, number> = {};

    if (selectedStrategy === 'highest_confidence') {
      winner = patterns.reduce((a, b) => a.confidence > b.confidence ? a : b);
      reasoning = `Selected '${winner.name}' with highest confidence (${(winner.confidence * 100).toFixed(0)}%)`;
      patterns.forEach(p => { scores[p.id] = p.confidence; });
    } else if (selectedStrategy === 'team_priority') {
      // Security priority makes security patterns win
      if (teamPriority === 'security') {
        winner = patterns.find(p => p.type === 'security') || patterns[0];
        reasoning = `Selected '${winner.name}' based on team priority: security`;
      } else if (teamPriority === 'readability') {
        winner = patterns.find(p => p.type === 'style') || patterns[0];
        reasoning = `Selected '${winner.name}' based on team priority: readability`;
      } else {
        winner = patterns[0];
        reasoning = `Selected '${winner.name}' based on team priority: balanced`;
      }
      patterns.forEach(p => { scores[p.id] = p.type === teamPriority ? 0.9 : 0.5; });
    } else {
      // Weighted score (default)
      winner = patterns.reduce((a, b) => {
        const scoreA = a.confidence * 0.4 + (a.type === 'security' ? 0.3 : 0.1);
        const scoreB = b.confidence * 0.4 + (b.type === 'security' ? 0.3 : 0.1);
        return scoreA > scoreB ? a : b;
      });
      reasoning = `Selected '${winner.name}' based on weighted scoring (confidence: ${(winner.confidence * 100).toFixed(0)}%, type: ${winner.type})`;
      patterns.forEach(p => {
        scores[p.id] = p.confidence * 0.4 + (p.type === 'security' ? 0.3 : 0.1) + 0.2;
      });
    }

    setResolutionResult({ winner: winner.id, reasoning, scores });
  };

  const toggleConflictPattern = (patternId: string) => {
    setConflictPatterns(prev => {
      if (prev.includes(patternId)) {
        return prev.filter(id => id !== patternId);
      }
      return [...prev, patternId];
    });
    setResolutionResult(null);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav className="border-b border-[var(--border)] py-4">
        <div className="container flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gradient">
            Empathy
          </Link>
          <div className="flex gap-6">
            <Link href="/book" className="text-sm hover:text-[var(--primary)]">Book</Link>
            <Link href="/docs" className="text-sm hover:text-[var(--primary)]">Docs</Link>
            <Link href="/framework" className="text-sm hover:text-[var(--primary)]">Framework</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-12 gradient-primary text-white">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <p className="text-sm mb-3 opacity-75">Chapter 23 Interactive Demo</p>
            <h1 className="text-4xl font-bold mb-4">
              Distributed Memory Networks
            </h1>
            <p className="text-lg opacity-90">
              Explore how multiple AI agents coordinate through shared pattern libraries
            </p>
          </div>
        </div>
      </section>

      {/* Agent Visualization */}
      <section className="py-12">
        <div className="container">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-bold mb-6" style={{ color: '#0F172A' }}>Agent Team</h2>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
              {DEMO_AGENTS.map(agent => (
                <div
                  key={agent.id}
                  className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg"
                  style={{ borderLeft: `4px solid ${agent.color}` }}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold" style={{ color: '#0F172A' }}>{agent.name}</h3>
                    <span className="text-xs px-2 py-1 bg-green-500/20 text-green-700 rounded">
                      {agent.status}
                    </span>
                  </div>
                  <p className="text-sm mb-3" style={{ color: '#334155' }}>
                    {agent.patterns} patterns discovered
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {DEMO_PATTERNS
                      .filter(p => p.agent === agent.id)
                      .slice(0, 2)
                      .map(p => (
                        <span
                          key={p.id}
                          className="text-xs px-2 py-1 bg-white rounded"
                          style={{ color: '#334155' }}
                        >
                          {p.name}
                        </span>
                      ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Shared Pattern Library */}
            <div className="mb-12">
              <h2 className="text-2xl font-bold mb-6" style={{ color: '#0F172A' }}>Shared Pattern Library</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border)]">
                      <th className="text-left py-3 px-4" style={{ color: '#334155' }}>Pattern</th>
                      <th className="text-left py-3 px-4" style={{ color: '#334155' }}>Type</th>
                      <th className="text-left py-3 px-4" style={{ color: '#334155' }}>Confidence</th>
                      <th className="text-left py-3 px-4" style={{ color: '#334155' }}>Contributor</th>
                      <th className="text-left py-3 px-4" style={{ color: '#334155' }}>Select for Conflict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {DEMO_PATTERNS.map(pattern => {
                      const agent = DEMO_AGENTS.find(a => a.id === pattern.agent);
                      const isSelected = conflictPatterns.includes(pattern.id);
                      return (
                        <tr
                          key={pattern.id}
                          className={`border-b border-[var(--border)] ${
                            isSelected ? 'bg-[#2563EB]' : ''
                          }`}
                        >
                          <td className="py-3 px-4 font-medium" style={{ color: isSelected ? '#ffffff' : '#0F172A' }}>{pattern.name}</td>
                          <td className="py-3 px-4">
                            <span className={`text-xs px-2 py-1 rounded ${
                              isSelected ? 'bg-white/20 text-white' :
                              pattern.type === 'security' ? 'bg-red-500/20 text-red-600' :
                              pattern.type === 'performance' ? 'bg-blue-500/20 text-blue-600' :
                              pattern.type === 'style' ? 'bg-purple-500/20 text-purple-600' :
                              'bg-gray-500/20 text-gray-600'
                            }`}>
                              {pattern.type}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className={`w-16 h-2 rounded-full overflow-hidden ${isSelected ? 'bg-white/30' : 'bg-gray-200'}`}>
                                <div
                                  className={`h-full ${isSelected ? 'bg-white' : 'bg-[var(--primary)]'}`}
                                  style={{ width: `${pattern.confidence * 100}%` }}
                                />
                              </div>
                              <span className="text-xs" style={{ color: isSelected ? '#ffffff' : '#334155' }}>
                                {(pattern.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className="text-xs"
                              style={{ color: isSelected ? '#ffffff' : agent?.color }}
                            >
                              {agent?.name}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <button
                              onClick={() => toggleConflictPattern(pattern.id)}
                              className={`text-xs px-3 py-1 rounded transition-colors ${
                                isSelected
                                  ? 'bg-[var(--primary)] text-white'
                                  : 'bg-[var(--border)] hover:bg-[var(--primary)] hover:text-white'
                              }`}
                            >
                              {isSelected ? 'Selected' : 'Select'}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Conflict Resolution Demo */}
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h2 className="text-2xl font-bold mb-6" style={{ color: '#0F172A' }}>Conflict Resolution</h2>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: '#334155' }}>Resolution Strategy</label>
                    <select
                      value={selectedStrategy}
                      onChange={(e) => {
                        setSelectedStrategy(e.target.value);
                        setResolutionResult(null);
                      }}
                      className="w-full p-3 bg-white border border-[var(--border)] rounded-lg"
                      style={{ color: '#0F172A' }}
                    >
                      {RESOLUTION_STRATEGIES.map(strategy => (
                        <option key={strategy.id} value={strategy.id}>
                          {strategy.name}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs mt-2" style={{ color: '#64748B' }}>
                      {RESOLUTION_STRATEGIES.find(s => s.id === selectedStrategy)?.description}
                    </p>
                  </div>

                  {selectedStrategy === 'team_priority' && (
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: '#334155' }}>Team Priority</label>
                      <select
                        value={teamPriority}
                        onChange={(e) => {
                          setTeamPriority(e.target.value);
                          setResolutionResult(null);
                        }}
                        className="w-full p-3 bg-white border border-[var(--border)] rounded-lg"
                        style={{ color: '#0F172A' }}
                      >
                        <option value="balanced">Balanced</option>
                        <option value="security">Security First</option>
                        <option value="readability">Readability First</option>
                        <option value="performance">Performance First</option>
                      </select>
                    </div>
                  )}

                  <div>
                    <p className="text-sm mb-3" style={{ color: '#334155' }}>
                      Selected {conflictPatterns.length} patterns for conflict resolution
                    </p>
                    <button
                      onClick={resolveConflict}
                      disabled={conflictPatterns.length < 2}
                      className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Resolve Conflict
                    </button>
                    {conflictPatterns.length < 2 && (
                      <p className="text-xs mt-2" style={{ color: '#64748B' }}>
                        Select at least 2 patterns to resolve a conflict
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-bold mb-6" style={{ color: '#0F172A' }}>Resolution Result</h2>

                {resolutionResult ? (
                  <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg">
                    <div className="mb-4">
                      <span className="text-xs" style={{ color: '#64748B' }}>Winner</span>
                      <h3 className="text-xl font-bold" style={{ color: '#10B981' }}>
                        {DEMO_PATTERNS.find(p => p.id === resolutionResult.winner)?.name}
                      </h3>
                    </div>

                    <div className="mb-4">
                      <span className="text-xs" style={{ color: '#64748B' }}>Reasoning</span>
                      <p className="text-sm" style={{ color: '#334155' }}>
                        {resolutionResult.reasoning}
                      </p>
                    </div>

                    <div>
                      <span className="text-xs" style={{ color: '#64748B' }}>Score Breakdown</span>
                      <div className="space-y-2 mt-2">
                        {Object.entries(resolutionResult.scores).map(([patternId, score]) => {
                          const pattern = DEMO_PATTERNS.find(p => p.id === patternId);
                          const isWinner = patternId === resolutionResult.winner;
                          return (
                            <div key={patternId} className="flex items-center gap-3">
                              <span className={`text-sm flex-1 ${isWinner ? 'font-bold' : ''}`} style={{ color: '#0F172A' }}>
                                {pattern?.name}
                              </span>
                              <div className="w-24 h-2 bg-[var(--background)] rounded-full overflow-hidden">
                                <div
                                  className={`h-full ${isWinner ? 'bg-[var(--success)]' : 'bg-[var(--muted)]'}`}
                                  style={{ width: `${Math.min(score * 100, 100)}%` }}
                                />
                              </div>
                              <span className="text-xs w-12 text-right" style={{ color: '#64748B' }}>
                                {(score * 100).toFixed(0)}%
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-[var(--border)] bg-opacity-30 p-6 rounded-lg text-center">
                    <p style={{ color: '#64748B' }}>
                      Select patterns and click &quot;Resolve Conflict&quot; to see the resolution result
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Code Example */}
      <section className="py-12 bg-[var(--border)] bg-opacity-30">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-6" style={{ color: '#0F172A' }}>Implementation</h2>
            <pre className="bg-[var(--foreground)] text-[var(--background)] p-6 rounded-lg overflow-x-auto text-sm">
{`from empathy_os import (
    EmpathyOS,
    PatternLibrary,
    ConflictResolver,
    AgentMonitor,
)

# 1. Create shared infrastructure
library = PatternLibrary()
resolver = ConflictResolver()
monitor = AgentMonitor(pattern_library=library)

# 2. Create agent team with shared library
code_reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=4,
    shared_library=library
)

test_generator = EmpathyOS(
    user_id="test_generator",
    target_level=3,
    shared_library=library
)

# 3. Resolve conflicts between patterns
resolution = resolver.resolve_patterns(
    patterns=[pattern1, pattern2],
    context={"team_priority": "readability"}
)

print(f"Winner: {resolution.winning_pattern.name}")
print(f"Reasoning: {resolution.reasoning}")

# 4. Monitor team collaboration
stats = monitor.get_team_stats()
print(f"Collaboration efficiency: {stats['collaboration_efficiency']:.0%}")`}
            </pre>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-12">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-2xl font-bold mb-4" style={{ color: '#0F172A' }}>Learn More</h2>
            <p className="mb-6" style={{ color: '#334155' }}>
              Dive deeper into Distributed Memory Networks in Chapter 23 of the book
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/chapter-23" className="btn btn-primary">
                Read Chapter 23
              </Link>
              <Link href="/book" className="btn btn-outline">
                Get the Book
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-[var(--border)]">
        <div className="container">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-sm text-[var(--muted)]">
              &copy; 2025 SmartAI Memory. All rights reserved.
            </div>
            <div className="flex gap-6">
              <Link href="/" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Home
              </Link>
              <Link href="/book" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Book
              </Link>
              <Link href="/docs" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Docs
              </Link>
              <Link href="/framework" className="text-sm text-[var(--muted)] hover:text-[var(--primary)]">
                Framework
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
