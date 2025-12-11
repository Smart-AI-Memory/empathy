'use client';

import { useState } from 'react';
import { toast } from 'react-hot-toast';
import WizardLayout from '@/components/wizard/WizardLayout';
import WizardNavigation from '@/components/wizard/WizardNavigation';
import WizardExport from '@/components/wizard/WizardExport';
import { useWizard } from '@/hooks/useWizard';
import { WizardConfig } from '@/types/wizard';
import TextInputWithDictation from '@/components/ui/TextInputWithDictation';

const wizardConfig: WizardConfig = {
  id: 'multi-agent-orchestration',
  title: 'Multi-Agent Orchestration Wizard',
  description: 'Design systems with multiple AI agents working together',
  icon: '🤖',
  category: 'development',
  estimatedTime: '30-40 minutes',
  steps: [
    { id: 'welcome', title: 'Welcome', description: 'Introduction', isComplete: false },
    { id: 'system-overview', title: 'System Overview', description: 'Problem to solve', isComplete: false },
    { id: 'agent-roles', title: 'Agent Roles', description: 'Define agents', isComplete: false },
    { id: 'communication', title: 'Communication', description: 'Agent interaction', isComplete: false },
    { id: 'task-delegation', title: 'Task Delegation', description: 'Workflow routing', isComplete: false },
    { id: 'error-handling', title: 'Error Handling', description: 'Failure recovery', isComplete: false },
    { id: 'review', title: 'Review', description: 'Export config', isComplete: false },
  ],
  exportFormats: [
    { id: 'markdown', label: 'Architecture Document (Markdown)', extension: 'md', mimeType: 'text/markdown' },
    { id: 'json', label: 'Configuration (JSON)', extension: 'json', mimeType: 'application/json' },
  ],
};

interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  capabilities: string[];
  template?: string;
}

interface Communication {
  pattern: string;
  protocol: string;
  channels: string[];
}

interface TaskRoute {
  trigger: string;
  targetAgent: string;
  priority: string;
  strategy: string;
}

interface ErrorHandling {
  strategy: string;
  retryAttempts: number;
  fallbackAgent?: string;
  escalationPath: string[];
}

const AGENT_TEMPLATES = [
  {
    value: 'researcher',
    label: 'Researcher',
    description: 'Gathers and synthesizes information',
    defaultCapabilities: ['web search', 'data analysis', 'fact checking', 'citation']
  },
  {
    value: 'writer',
    label: 'Writer',
    description: 'Creates content and documentation',
    defaultCapabilities: ['content generation', 'editing', 'formatting', 'tone adjustment']
  },
  {
    value: 'reviewer',
    label: 'Reviewer',
    description: 'Quality assurance and validation',
    defaultCapabilities: ['quality check', 'consistency review', 'error detection', 'feedback']
  },
  {
    value: 'coordinator',
    label: 'Coordinator',
    description: 'Manages workflow and orchestration',
    defaultCapabilities: ['task routing', 'priority management', 'status tracking', 'delegation']
  },
  {
    value: 'specialist',
    label: 'Specialist',
    description: 'Domain-specific expertise',
    defaultCapabilities: ['expert knowledge', 'technical analysis', 'problem solving', 'consultation']
  },
  {
    value: 'analyst',
    label: 'Analyst',
    description: 'Data processing and insights',
    defaultCapabilities: ['data processing', 'pattern recognition', 'reporting', 'visualization']
  },
  {
    value: 'custom',
    label: 'Custom Agent',
    description: 'Define your own agent type',
    defaultCapabilities: []
  }
];

const COMMUNICATION_PATTERNS = [
  {
    value: 'sequential',
    label: 'Sequential',
    description: 'Agents work one after another in a chain',
    icon: '→'
  },
  {
    value: 'parallel',
    label: 'Parallel',
    description: 'Multiple agents work simultaneously',
    icon: '⇉'
  },
  {
    value: 'hierarchical',
    label: 'Hierarchical',
    description: 'Tree structure with coordinator at top',
    icon: '🌳'
  },
  {
    value: 'democratic',
    label: 'Democratic',
    description: 'Agents vote or reach consensus',
    icon: '🗳️'
  },
  {
    value: 'hub-spoke',
    label: 'Hub-Spoke',
    description: 'Central coordinator routes to specialists',
    icon: '⊛'
  },
  {
    value: 'mesh',
    label: 'Mesh',
    description: 'Any agent can communicate with any other',
    icon: '⋈'
  }
];

const ROUTING_STRATEGIES = [
  { value: 'rule-based', label: 'Rule-Based', description: 'Fixed rules and conditions' },
  { value: 'ml-based', label: 'ML-Based', description: 'Machine learning classification' },
  { value: 'user-driven', label: 'User-Driven', description: 'User selects routing' },
  { value: 'priority-queue', label: 'Priority Queue', description: 'Based on task priority' },
  { value: 'load-balanced', label: 'Load Balanced', description: 'Distribute workload evenly' },
  { value: 'capability-match', label: 'Capability Match', description: 'Match task to agent capabilities' }
];

const ERROR_STRATEGIES = [
  { value: 'retry', label: 'Retry', description: 'Retry the same agent with exponential backoff' },
  { value: 'fallback', label: 'Fallback', description: 'Switch to a backup agent' },
  { value: 'escalate', label: 'Escalate', description: 'Send to higher-level coordinator' },
  { value: 'abort', label: 'Abort', description: 'Fail gracefully and notify user' },
  { value: 'compensate', label: 'Compensate', description: 'Run compensating transaction' },
  { value: 'circuit-breaker', label: 'Circuit Breaker', description: 'Temporarily disable failing agent' }
];

export default function MultiAgentWizard() {
  const wizard = useWizard(wizardConfig);

  // System Overview
  const [systemName, setSystemName] = useState('');
  const [problemStatement, setProblemStatement] = useState('');
  const [goals, setGoals] = useState<string[]>(['']);
  const [constraints, setConstraints] = useState('');

  // Agents
  const [agents, setAgents] = useState<Agent[]>([]);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [agentName, setAgentName] = useState('');
  const [agentRole, setAgentRole] = useState('');
  const [agentDescription, setAgentDescription] = useState('');
  const [agentCapabilities, setAgentCapabilities] = useState<string[]>(['']);

  // Communication
  const [communicationPattern, setCommunicationPattern] = useState('');
  const [communicationProtocol, setCommunicationProtocol] = useState('message-queue');
  const [channels, setChannels] = useState<string[]>(['default']);

  // Task Delegation
  const [taskRoutes, setTaskRoutes] = useState<TaskRoute[]>([]);
  const [routingStrategy, setRoutingStrategy] = useState('');

  // Error Handling
  const [errorStrategy, setErrorStrategy] = useState('');
  const [retryAttempts, setRetryAttempts] = useState(3);
  const [fallbackAgent, setFallbackAgent] = useState('');
  const [escalationPath, setEscalationPath] = useState<string[]>([]);

  const addAgent = () => {
    if (!agentName || !agentRole) {
      toast.error('Please provide agent name and role');
      return;
    }

    const newAgent: Agent = {
      id: `agent-${Date.now()}`,
      name: agentName,
      role: agentRole,
      description: agentDescription,
      capabilities: agentCapabilities.filter(c => c.trim() !== ''),
      template: agentRole !== 'custom' ? agentRole : undefined
    };

    if (editingAgent) {
      setAgents(agents.map(a => a.id === editingAgent.id ? { ...newAgent, id: editingAgent.id } : a));
      setEditingAgent(null);
      toast.success('Agent updated');
    } else {
      setAgents([...agents, newAgent]);
      toast.success('Agent added');
    }

    // Reset form
    setAgentName('');
    setAgentRole('');
    setAgentDescription('');
    setAgentCapabilities(['']);
  };

  const editAgent = (agent: Agent) => {
    setEditingAgent(agent);
    setAgentName(agent.name);
    setAgentRole(agent.role);
    setAgentDescription(agent.description);
    setAgentCapabilities(agent.capabilities.length > 0 ? agent.capabilities : ['']);
  };

  const deleteAgent = (id: string) => {
    setAgents(agents.filter(a => a.id !== id));
    toast.success('Agent removed');
  };

  const applyTemplate = (templateValue: string) => {
    const template = AGENT_TEMPLATES.find(t => t.value === templateValue);
    if (template && template.defaultCapabilities.length > 0) {
      setAgentCapabilities(template.defaultCapabilities);
    }
  };

  const addGoal = () => {
    setGoals([...goals, '']);
  };

  const updateGoal = (index: number, value: string) => {
    const newGoals = [...goals];
    newGoals[index] = value;
    setGoals(newGoals);
  };

  const removeGoal = (index: number) => {
    setGoals(goals.filter((_, i) => i !== index));
  };

  const addCapability = () => {
    setAgentCapabilities([...agentCapabilities, '']);
  };

  const updateCapability = (index: number, value: string) => {
    const newCapabilities = [...agentCapabilities];
    newCapabilities[index] = value;
    setAgentCapabilities(newCapabilities);
  };

  const removeCapability = (index: number) => {
    setAgentCapabilities(agentCapabilities.filter((_, i) => i !== index));
  };

  const addTaskRoute = () => {
    setTaskRoutes([...taskRoutes, {
      trigger: '',
      targetAgent: agents[0]?.id || '',
      priority: 'medium',
      strategy: routingStrategy
    }]);
  };

  const updateTaskRoute = (index: number, field: keyof TaskRoute, value: string) => {
    const newRoutes = [...taskRoutes];
    newRoutes[index] = { ...newRoutes[index], [field]: value };
    setTaskRoutes(newRoutes);
  };

  const removeTaskRoute = (index: number) => {
    setTaskRoutes(taskRoutes.filter((_, i) => i !== index));
  };

  const generateMarkdown = () => {
    const sections = [];

    // Header
    sections.push(`# ${systemName || 'Multi-Agent System'} - Architecture Document`);
    sections.push('');
    sections.push(`**Generated:** ${new Date().toLocaleDateString()}`);
    sections.push('');

    // System Overview
    sections.push('## System Overview');
    sections.push('');
    sections.push('### Problem Statement');
    sections.push(problemStatement || 'Not specified');
    sections.push('');

    sections.push('### Goals');
    goals.filter(g => g.trim()).forEach(goal => {
      sections.push(`- ${goal}`);
    });
    sections.push('');

    if (constraints) {
      sections.push('### Constraints');
      sections.push(constraints);
      sections.push('');
    }

    // Agents
    sections.push('## Agent Definitions');
    sections.push('');
    agents.forEach(agent => {
      sections.push(`### ${agent.name}`);
      sections.push('');
      sections.push(`**Role:** ${AGENT_TEMPLATES.find(t => t.value === agent.role)?.label || agent.role}`);
      sections.push('');
      sections.push(`**Description:** ${agent.description}`);
      sections.push('');
      sections.push('**Capabilities:**');
      agent.capabilities.forEach(cap => {
        sections.push(`- ${cap}`);
      });
      sections.push('');
    });

    // Communication
    sections.push('## Communication Architecture');
    sections.push('');
    const pattern = COMMUNICATION_PATTERNS.find(p => p.value === communicationPattern);
    if (pattern) {
      sections.push(`**Pattern:** ${pattern.label} ${pattern.icon}`);
      sections.push('');
      sections.push(pattern.description);
      sections.push('');
    }
    sections.push(`**Protocol:** ${communicationProtocol}`);
    sections.push('');
    sections.push('**Channels:**');
    channels.forEach(channel => {
      sections.push(`- ${channel}`);
    });
    sections.push('');

    // Visual Workflow
    sections.push('## Workflow Diagram');
    sections.push('');
    sections.push('```mermaid');
    sections.push('graph TD');

    if (communicationPattern === 'sequential' && agents.length > 0) {
      agents.forEach((agent, i) => {
        sections.push(`    ${agent.id}[${agent.name}]`);
        if (i < agents.length - 1) {
          sections.push(`    ${agent.id} --> ${agents[i + 1].id}`);
        }
      });
    } else if (communicationPattern === 'parallel' && agents.length > 0) {
      sections.push(`    Start[Start]`);
      agents.forEach(agent => {
        sections.push(`    ${agent.id}[${agent.name}]`);
        sections.push(`    Start --> ${agent.id}`);
      });
      sections.push(`    End[End]`);
      agents.forEach(agent => {
        sections.push(`    ${agent.id} --> End`);
      });
    } else if (communicationPattern === 'hierarchical' && agents.length > 0) {
      sections.push(`    ${agents[0].id}[${agents[0].name} - Coordinator]`);
      agents.slice(1).forEach(agent => {
        sections.push(`    ${agent.id}[${agent.name}]`);
        sections.push(`    ${agents[0].id} --> ${agent.id}`);
      });
    } else {
      agents.forEach(agent => {
        sections.push(`    ${agent.id}[${agent.name}]`);
      });
    }
    sections.push('```');
    sections.push('');

    // Task Delegation
    sections.push('## Task Delegation');
    sections.push('');
    const strategy = ROUTING_STRATEGIES.find(s => s.value === routingStrategy);
    sections.push(`**Strategy:** ${strategy?.label || 'Not specified'}`);
    sections.push('');
    if (strategy) {
      sections.push(strategy.description);
      sections.push('');
    }

    if (taskRoutes.length > 0) {
      sections.push('### Routing Rules');
      sections.push('');
      taskRoutes.forEach((route, i) => {
        const agent = agents.find(a => a.id === route.targetAgent);
        sections.push(`${i + 1}. **Trigger:** ${route.trigger}`);
        sections.push(`   - Target: ${agent?.name || 'Unknown'}`);
        sections.push(`   - Priority: ${route.priority}`);
        sections.push('');
      });
    }

    // Error Handling
    sections.push('## Error Handling');
    sections.push('');
    const errorStrat = ERROR_STRATEGIES.find(s => s.value === errorStrategy);
    sections.push(`**Primary Strategy:** ${errorStrat?.label || 'Not specified'}`);
    sections.push('');
    if (errorStrat) {
      sections.push(errorStrat.description);
      sections.push('');
    }

    if (errorStrategy === 'retry') {
      sections.push(`**Retry Attempts:** ${retryAttempts}`);
      sections.push('');
    }

    if (errorStrategy === 'fallback' && fallbackAgent) {
      const fallback = agents.find(a => a.id === fallbackAgent);
      sections.push(`**Fallback Agent:** ${fallback?.name || 'Unknown'}`);
      sections.push('');
    }

    if (escalationPath.length > 0) {
      sections.push('**Escalation Path:**');
      escalationPath.forEach((agentId, i) => {
        const agent = agents.find(a => a.id === agentId);
        sections.push(`${i + 1}. ${agent?.name || 'Unknown'}`);
      });
      sections.push('');
    }

    // Implementation Notes
    sections.push('## Implementation Considerations');
    sections.push('');
    sections.push('### Scalability');
    sections.push(`- Number of agents: ${agents.length}`);
    sections.push(`- Communication pattern: ${pattern?.label || 'Not specified'}`);
    sections.push(`- Routing strategy: ${strategy?.label || 'Not specified'}`);
    sections.push('');
    sections.push('### Reliability');
    sections.push(`- Error handling: ${errorStrat?.label || 'Not specified'}`);
    sections.push(`- Retry attempts: ${retryAttempts}`);
    sections.push(`- Fallback mechanisms: ${fallbackAgent ? 'Configured' : 'Not configured'}`);
    sections.push('');
    sections.push('### Monitoring');
    sections.push('- Log all agent interactions');
    sections.push('- Track task completion rates');
    sections.push('- Monitor error frequencies');
    sections.push('- Measure response times');
    sections.push('');

    return sections.join('\n');
  };

  const generateJSON = () => {
    const config = {
      system: {
        name: systemName,
        problem: problemStatement,
        goals: goals.filter(g => g.trim()),
        constraints: constraints
      },
      agents: agents.map(agent => ({
        id: agent.id,
        name: agent.name,
        role: agent.role,
        description: agent.description,
        capabilities: agent.capabilities
      })),
      communication: {
        pattern: communicationPattern,
        protocol: communicationProtocol,
        channels: channels
      },
      delegation: {
        strategy: routingStrategy,
        routes: taskRoutes
      },
      errorHandling: {
        strategy: errorStrategy,
        retryAttempts: retryAttempts,
        fallbackAgent: fallbackAgent,
        escalationPath: escalationPath
      },
      metadata: {
        version: '1.0',
        created: new Date().toISOString(),
        wizard: 'multi-agent-orchestration'
      }
    };

    return JSON.stringify(config, null, 2);
  };

  const renderStep = () => {
    const currentStep = wizardConfig.steps[wizard.currentStep];

    switch (currentStep.id) {
      case 'welcome':
        return (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🤖</div>
              <h2 className="text-3xl font-bold mb-4">Multi-Agent Orchestration Wizard</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Design sophisticated systems where multiple AI agents collaborate to solve complex problems.
                This wizard will help you architect the relationships, communication patterns, and workflows
                for your multi-agent system.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="font-semibold mb-2">Define Agent Roles</h3>
                <p className="text-sm text-gray-400">
                  Create specialized agents with distinct capabilities and responsibilities
                </p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🔄</div>
                <h3 className="font-semibold mb-2">Design Communication</h3>
                <p className="text-sm text-gray-400">
                  Set up how agents interact and share information
                </p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">📋</div>
                <h3 className="font-semibold mb-2">Configure Routing</h3>
                <p className="text-sm text-gray-400">
                  Define how tasks are delegated across your agent network
                </p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div className="text-3xl mb-3">🛡️</div>
                <h3 className="font-semibold mb-2">Handle Failures</h3>
                <p className="text-sm text-gray-400">
                  Plan for errors with retry, fallback, and escalation strategies
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                wizard.completeStep('welcome');
                wizard.nextStep();
              }}
              className="w-full mt-8 px-8 py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-medium text-lg hover:opacity-90 transition-opacity"
            >
              Start Designing →
            </button>
          </div>
        );

      case 'system-overview':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">System Overview</h2>
              <p className="text-gray-400">Define the problem your multi-agent system will solve</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">System Name *</label>
              <input
                type="text"
                value={systemName}
                onChange={(e) => setSystemName(e.target.value)}
                placeholder="e.g., Customer Support System, Content Pipeline, Research Assistant"
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Problem Statement *</label>
              <TextInputWithDictation
                multiline
                value={problemStatement}
                onChange={(e) => setProblemStatement(e.target.value)}
                placeholder="Describe the problem or challenge this multi-agent system will address..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                rows={4}
                enableDictation={true}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Goals *</label>
              <p className="text-xs text-gray-500 mb-2">What outcomes should this system achieve?</p>
              {goals.map((goal, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={goal}
                    onChange={(e) => updateGoal(index, e.target.value)}
                    placeholder="e.g., Reduce response time by 50%"
                    className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  />
                  {goals.length > 1 && (
                    <button
                      onClick={() => removeGoal(index)}
                      className="px-3 py-2 bg-red-900/20 text-red-400 rounded-lg hover:bg-red-900/30"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={addGoal}
                className="w-full py-2 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-sm"
              >
                + Add Goal
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Constraints <span className="text-gray-500">(Optional)</span>
              </label>
              <TextInputWithDictation
                multiline
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                placeholder="Budget limits, technical requirements, performance requirements, compliance needs..."
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                rows={4}
                enableDictation={true}
              />
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!systemName && !!problemStatement && goals.some(g => g.trim())}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('system-overview');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'agent-roles':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Define Agent Roles</h2>
              <p className="text-gray-400">Create the agents that will work together in your system</p>
            </div>

            {/* Agent List */}
            {agents.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-sm text-gray-400 uppercase">Your Agents</h3>
                {agents.map((agent) => {
                  const template = AGENT_TEMPLATES.find(t => t.value === agent.role);
                  return (
                    <div key={agent.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-semibold text-lg">{agent.name}</h4>
                            <span className="px-2 py-1 bg-primary/20 text-primary text-xs rounded">
                              {template?.label || agent.role}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400 mb-3">{agent.description}</p>
                          <div className="flex flex-wrap gap-2">
                            {agent.capabilities.map((cap, i) => (
                              <span key={i} className="px-2 py-1 bg-gray-700 text-xs rounded">
                                {cap}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <button
                            onClick={() => editAgent(agent)}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteAgent(agent.id)}
                            className="px-3 py-1 bg-red-900/20 text-red-400 hover:bg-red-900/30 rounded text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Add/Edit Agent Form */}
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h3 className="font-semibold mb-4">
                {editingAgent ? 'Edit Agent' : 'Add New Agent'}
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Agent Template</label>
                  <select
                    value={agentRole}
                    onChange={(e) => {
                      setAgentRole(e.target.value);
                      applyTemplate(e.target.value);
                    }}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  >
                    <option value="">Select a template...</option>
                    {AGENT_TEMPLATES.map((template) => (
                      <option key={template.value} value={template.value}>
                        {template.label} - {template.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Agent Name</label>
                  <input
                    type="text"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    placeholder="e.g., Data Researcher, Content Writer, Quality Reviewer"
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <TextInputWithDictation
                    multiline
                    value={agentDescription}
                    onChange={(e) => setAgentDescription(e.target.value)}
                    placeholder="What is this agent responsible for?"
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary resize-none"
                    rows={3}
                    enableDictation={true}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Capabilities</label>
                  {agentCapabilities.map((cap, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={cap}
                        onChange={(e) => updateCapability(index, e.target.value)}
                        placeholder="e.g., web search, data analysis, content generation"
                        className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                      />
                      {agentCapabilities.length > 1 && (
                        <button
                          onClick={() => removeCapability(index)}
                          className="px-3 py-2 bg-red-900/20 text-red-400 rounded-lg hover:bg-red-900/30"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    onClick={addCapability}
                    className="w-full py-2 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-sm"
                  >
                    + Add Capability
                  </button>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={addAgent}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-secondary hover:opacity-90 rounded-lg font-medium transition-opacity"
                  >
                    {editingAgent ? 'Update Agent' : 'Add Agent'}
                  </button>
                  {editingAgent && (
                    <button
                      onClick={() => {
                        setEditingAgent(null);
                        setAgentName('');
                        setAgentRole('');
                        setAgentDescription('');
                        setAgentCapabilities(['']);
                      }}
                      className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={agents.length >= 2}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('agent-roles');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'communication':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Communication Architecture</h2>
              <p className="text-gray-400">Define how your agents will interact with each other</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-3">Communication Pattern *</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {COMMUNICATION_PATTERNS.map((pattern) => (
                  <button
                    key={pattern.value}
                    onClick={() => setCommunicationPattern(pattern.value)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      communicationPattern === pattern.value
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{pattern.icon}</span>
                      <span className="font-semibold">{pattern.label}</span>
                    </div>
                    <div className="text-sm text-gray-400">{pattern.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Communication Protocol</label>
              <select
                value={communicationProtocol}
                onChange={(e) => setCommunicationProtocol(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
              >
                <option value="message-queue">Message Queue (RabbitMQ, Kafka)</option>
                <option value="rest-api">REST API</option>
                <option value="graphql">GraphQL</option>
                <option value="grpc">gRPC</option>
                <option value="websocket">WebSocket</option>
                <option value="event-bus">Event Bus</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Communication Channels</label>
              <p className="text-xs text-gray-500 mb-2">Define channels for different types of messages</p>
              {channels.map((channel, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={channel}
                    onChange={(e) => {
                      const newChannels = [...channels];
                      newChannels[index] = e.target.value;
                      setChannels(newChannels);
                    }}
                    placeholder="e.g., default, priority, notifications, errors"
                    className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                  />
                  {channels.length > 1 && (
                    <button
                      onClick={() => setChannels(channels.filter((_, i) => i !== index))}
                      className="px-3 py-2 bg-red-900/20 text-red-400 rounded-lg hover:bg-red-900/30"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => setChannels([...channels, ''])}
                className="w-full py-2 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-sm"
              >
                + Add Channel
              </button>
            </div>

            <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">💡</div>
                <div>
                  <div className="font-semibold text-blue-400 mb-1">Pattern Guidelines</div>
                  <div className="text-sm text-gray-300 space-y-1">
                    <p><strong>Sequential:</strong> Best for linear workflows where each agent builds on previous results</p>
                    <p><strong>Parallel:</strong> Ideal when agents can work independently on different aspects</p>
                    <p><strong>Hierarchical:</strong> Use when you need clear coordination and decision-making hierarchy</p>
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!communicationPattern}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('communication');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'task-delegation':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Task Delegation Strategy</h2>
              <p className="text-gray-400">Define how tasks are routed to appropriate agents</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-3">Routing Strategy *</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {ROUTING_STRATEGIES.map((strategy) => (
                  <button
                    key={strategy.value}
                    onClick={() => setRoutingStrategy(strategy.value)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      routingStrategy === strategy.value
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold mb-1">{strategy.label}</div>
                    <div className="text-sm text-gray-400">{strategy.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Routing Rules</label>
              <p className="text-xs text-gray-500 mb-3">Define specific rules for task routing</p>

              {taskRoutes.length > 0 && (
                <div className="space-y-3 mb-3">
                  {taskRoutes.map((route, index) => (
                    <div key={index} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs mb-1">Trigger Condition</label>
                          <input
                            type="text"
                            value={route.trigger}
                            onChange={(e) => updateTaskRoute(index, 'trigger', e.target.value)}
                            placeholder="e.g., task.type === 'research'"
                            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-xs mb-1">Target Agent</label>
                          <select
                            value={route.targetAgent}
                            onChange={(e) => updateTaskRoute(index, 'targetAgent', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary text-sm"
                          >
                            {agents.map((agent) => (
                              <option key={agent.id} value={agent.id}>
                                {agent.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs mb-1">Priority</label>
                          <select
                            value={route.priority}
                            onChange={(e) => updateTaskRoute(index, 'priority', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-primary text-sm"
                          >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="critical">Critical</option>
                          </select>
                        </div>
                        <div className="flex items-end">
                          <button
                            onClick={() => removeTaskRoute(index)}
                            className="w-full px-3 py-2 bg-red-900/20 text-red-400 rounded hover:bg-red-900/30 text-sm"
                          >
                            Remove Rule
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={addTaskRoute}
                disabled={agents.length === 0}
                className="w-full py-3 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                + Add Routing Rule
              </button>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!routingStrategy}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('task-delegation');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'error-handling':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Error Handling Strategy</h2>
              <p className="text-gray-400">Define how your system handles failures and errors</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-3">Primary Strategy *</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {ERROR_STRATEGIES.map((strategy) => (
                  <button
                    key={strategy.value}
                    onClick={() => setErrorStrategy(strategy.value)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      errorStrategy === strategy.value
                        ? 'border-primary bg-primary/10'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                  >
                    <div className="font-semibold mb-1">{strategy.label}</div>
                    <div className="text-sm text-gray-400">{strategy.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {errorStrategy === 'retry' && (
              <div>
                <label className="block text-sm font-medium mb-2">Maximum Retry Attempts</label>
                <input
                  type="number"
                  value={retryAttempts}
                  onChange={(e) => setRetryAttempts(parseInt(e.target.value) || 0)}
                  min="1"
                  max="10"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Uses exponential backoff between attempts
                </p>
              </div>
            )}

            {errorStrategy === 'fallback' && agents.length > 0 && (
              <div>
                <label className="block text-sm font-medium mb-2">Fallback Agent</label>
                <select
                  value={fallbackAgent}
                  onChange={(e) => setFallbackAgent(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                >
                  <option value="">Select fallback agent...</option>
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {errorStrategy === 'escalate' && agents.length > 0 && (
              <div>
                <label className="block text-sm font-medium mb-2">Escalation Path</label>
                <p className="text-xs text-gray-500 mb-2">
                  Define the order of agents to escalate to when errors occur
                </p>
                <div className="space-y-2">
                  {escalationPath.map((agentId, index) => (
                    <div key={index} className="flex gap-2 items-center">
                      <span className="text-sm text-gray-400 w-8">#{index + 1}</span>
                      <select
                        value={agentId}
                        onChange={(e) => {
                          const newPath = [...escalationPath];
                          newPath[index] = e.target.value;
                          setEscalationPath(newPath);
                        }}
                        className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-primary"
                      >
                        <option value="">Select agent...</option>
                        {agents.map((agent) => (
                          <option key={agent.id} value={agent.id}>
                            {agent.name}
                          </option>
                        ))}
                      </select>
                      <button
                        onClick={() => setEscalationPath(escalationPath.filter((_, i) => i !== index))}
                        className="px-3 py-2 bg-red-900/20 text-red-400 rounded-lg hover:bg-red-900/30"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => setEscalationPath([...escalationPath, ''])}
                    className="w-full py-2 border-2 border-dashed border-gray-700 rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-sm"
                  >
                    + Add Escalation Level
                  </button>
                </div>
              </div>
            )}

            <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-2xl">⚠️</div>
                <div>
                  <div className="font-semibold text-yellow-400 mb-1">Best Practices</div>
                  <div className="text-sm text-gray-300 space-y-1">
                    <p>• Always implement monitoring and logging for failed operations</p>
                    <p>• Set appropriate timeout values for each agent</p>
                    <p>• Consider implementing circuit breakers for frequently failing agents</p>
                    <p>• Plan for graceful degradation when agents are unavailable</p>
                  </div>
                </div>
              </div>
            </div>

            <WizardNavigation
              canGoBack={wizard.currentStep > 0}
              canGoNext={wizard.currentStep < wizardConfig.steps.length - 1}
              isLastStep={wizard.currentStep === wizardConfig.steps.length - 1}
              isCurrentStepComplete={!!errorStrategy}
              onBack={() => wizard.previousStep()}
              onNext={() => {
                wizard.completeStep('error-handling');
                wizard.nextStep();
              }}
            />
          </div>
        );

      case 'review':
        const markdownContent = generateMarkdown();
        const jsonContent = generateJSON();
        const [exportFormat, setExportFormat] = useState('markdown');

        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Review Your Multi-Agent System</h2>
              <p className="text-gray-400">Export your architecture documentation and configuration</p>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Total Agents</div>
                <div className="text-3xl font-bold">{agents.length}</div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Pattern</div>
                <div className="text-lg font-bold truncate">
                  {COMMUNICATION_PATTERNS.find(p => p.value === communicationPattern)?.label || 'N/A'}
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Routing</div>
                <div className="text-lg font-bold truncate">
                  {ROUTING_STRATEGIES.find(s => s.value === routingStrategy)?.label || 'N/A'}
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <div className="text-sm text-gray-400 mb-1">Error Strategy</div>
                <div className="text-lg font-bold truncate">
                  {ERROR_STRATEGIES.find(s => s.value === errorStrategy)?.label || 'N/A'}
                </div>
              </div>
            </div>

            {/* Agent Summary */}
            <div>
              <h3 className="font-semibold mb-3">Agent Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {agents.map((agent) => (
                  <div key={agent.id} className="bg-gray-800 p-3 rounded-lg border border-gray-700">
                    <div className="font-semibold">{agent.name}</div>
                    <div className="text-xs text-gray-400">
                      {AGENT_TEMPLATES.find(t => t.value === agent.role)?.label}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {agent.capabilities.length} capabilities
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Export Section */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="font-semibold mb-4">Export Format</h3>

              <div className="flex gap-3 mb-4">
                <button
                  onClick={() => setExportFormat('markdown')}
                  className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                    exportFormat === 'markdown'
                      ? 'bg-primary text-white'
                      : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  Architecture Doc (Markdown)
                </button>
                <button
                  onClick={() => setExportFormat('json')}
                  className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                    exportFormat === 'json'
                      ? 'bg-primary text-white'
                      : 'bg-gray-700 hover:bg-gray-600'
                  }`}
                >
                  Configuration (JSON)
                </button>
              </div>

              <WizardExport
                formats={wizardConfig.exportFormats.filter(f => f.id === exportFormat)}
                content={exportFormat === 'markdown' ? markdownContent : jsonContent}
                filename={`${systemName.toLowerCase().replace(/\s+/g, '-') || 'multi-agent-system'}-${exportFormat === 'markdown' ? 'architecture' : 'config'}`}
              />
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => wizard.goToStep(0)}
                className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium transition-colors"
              >
                Start New System
              </button>
              <button
                onClick={() => {
                  wizard.completeStep('review');
                  toast.success('Multi-agent system design complete!');
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-secondary hover:opacity-90 rounded-lg font-medium transition-opacity"
              >
                Complete Wizard
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <WizardLayout
      config={wizardConfig}
      currentStep={wizard.currentStep}
      totalSteps={wizardConfig.steps.length}
      progress={wizard.progress}
      onStepClick={wizard.goToStep}
    >
      {renderStep()}
    </WizardLayout>
  );
}
