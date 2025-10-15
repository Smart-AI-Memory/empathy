# Building Custom Wizards with LangChain

Complete guide to creating your own Coach wizards using LangChain.

**Built on LangChain** - Leverage the full power of Lang

Chain's agent framework, tools, and chains.

---

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Wizard Architecture](#wizard-architecture)
- [Quick Start](#quick-start)
- [Tutorial: Build a CostOptimizationWizard](#tutorial-build-a-costoptimizationwizard)
- [Advanced Features](#advanced-features)
- [Testing Your Wizard](#testing-your-wizard)
- [Deployment](#deployment)
- [Best Practices](#best-practices)
- [Examples Gallery](#examples-gallery)

---

## Introduction

Coach's wizard framework is built entirely on **LangChain**, making it:

- **Extensible**: Add custom wizards for your team's needs
- **Powerful**: Access LangChain's full ecosystem (tools, memory, callbacks)
- **Flexible**: Use any LLM (OpenAI, Anthropic, local models)
- **Testable**: LangChain's testing utilities work out-of-the-box

### What You'll Learn

- How to create a custom wizard from scratch
- How to use LangChain tools and chains
- How to implement Level 4 predictions
- How to test and deploy your wizard

---

## Prerequisites

### Required Knowledge

- **Python 3.12+** - Basic Python programming
- **LangChain basics** - Chains, agents, tools (see [LangChain docs](https://python.langchain.com/))
- **Coach concepts** - Understanding of how Coach wizards work

### Required Packages

```bash
pip install langchain langchain-community langchain-openai
pip install coach-ai  # Coach framework (alpha: install from source)
```

### Recommended Tools

- **LangSmith** - For debugging and monitoring (optional)
- **VS Code** + Python extension
- **pytest** - For testing

---

## Wizard Architecture

### Base Wizard Class

All Coach wizards inherit from `BaseWizard`:

```python
from coach.base_wizard import BaseWizard
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class MyWizard(BaseWizard):
    """Your custom wizard"""

    # Required attributes
    name = "MyWizard"
    expertise = "Short description of expertise"

    # Optional attributes
    version = "1.0.0"
    requires_wizards = ["OtherWizard"]  # Dependencies on other wizards

    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)
        # Initialize your wizard-specific components
        self.tools = self._create_tools()
        self.chain = self._create_chain()

    def analyze(self, code: str, context: str = "") -> WizardResult:
        """Main analysis method - implement your logic here"""
        pass

    def predict(self, code: str, context: str = "", timeline_days: int = 90) -> Prediction:
        """Level 4 prediction - forecast future issues"""
        pass

    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools for this wizard"""
        pass

    def _create_chain(self) -> LLMChain:
        """Create LangChain chain for this wizard"""
        pass
```

### Key Components

1. **LLM**: Language model (OpenAI, Anthropic, local)
2. **Tools**: LangChain tools for specific tasks
3. **Chain/Agent**: LangChain chain or agent for orchestration
4. **Prompt Template**: Instructions for the LLM
5. **Memory** (optional): Conversation history or context

---

## Quick Start

### Minimal Working Wizard

Here's the simplest possible custom wizard:

```python
from coach.base_wizard import BaseWizard, WizardResult
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class HelloWizard(BaseWizard):
    """Minimal example wizard"""

    name = "HelloWizard"
    expertise = "Says hello to code"

    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)

        # Create LangChain prompt
        self.prompt = PromptTemplate(
            input_variables=["code"],
            template="Say hello to this code and tell me what it does:\n\n{code}"
        )

        # Create LangChain chain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def analyze(self, code: str, context: str = "") -> WizardResult:
        """Analyze code"""
        # Run LangChain chain
        response = self.chain.run(code=code)

        # Return WizardResult
        return WizardResult(
            wizard=self.name,
            diagnosis=response,
            recommendations=["Keep coding!"],
            confidence=1.0
        )

# Usage
wizard = HelloWizard(llm=ChatOpenAI(model="gpt-4"))
result = wizard.analyze("print('Hello, world!')")
print(result.diagnosis)
# Output: "Hello! This code prints 'Hello, world!' to the console..."
```

### Test Your Wizard

```python
# test_hello_wizard.py
import pytest
from custom_wizards.hello_wizard import HelloWizard
from langchain.chat_models import ChatOpenAI

def test_hello_wizard():
    wizard = HelloWizard(llm=ChatOpenAI(model="gpt-4"))
    result = wizard.analyze("x = 42")

    assert result.wizard == "HelloWizard"
    assert result.confidence == 1.0
    assert len(result.recommendations) > 0
```

---

## Tutorial: Build a CostOptimizationWizard

Let's build a real-world wizard that analyzes cloud infrastructure costs and predicts future expenses.

### Step 1: Define Wizard Structure

```python
# custom_wizards/cost_optimization_wizard.py

from coach.base_wizard import BaseWizard, WizardResult, Prediction, CodeExample
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, Dict
import re

class CostOptimizationWizard(BaseWizard):
    """Analyzes infrastructure code for cost optimization opportunities

    This wizard:
    - Detects over-provisioned resources
    - Recommends cost-effective alternatives
    - Predicts future costs based on growth
    - Suggests reserved instances, spot instances, etc.

    Powered by LangChain with custom tools for cost analysis.
    """

    name = "CostOptimizationWizard"
    expertise = "Cloud infrastructure cost optimization and forecasting"
    version = "1.0.0"
```

### Step 2: Create LangChain Tools

```python
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools for cost analysis"""

        def analyze_instance_sizes(code: str) -> Dict:
            """Detect instance sizes in infrastructure code"""
            # AWS EC2 instances
            ec2_pattern = r'instance_type\s*=\s*["\']([^"\']+)["\']'
            instances = re.findall(ec2_pattern, code, re.IGNORECASE)

            # Known costs (simplified - would use pricing API in production)
            costs_per_hour = {
                't2.micro': 0.0116,
                't2.small': 0.023,
                't2.medium': 0.0464,
                't3.medium': 0.0416,
                'm5.large': 0.096,
                'm5.xlarge': 0.192,
                'c5.large': 0.085,
                'c5.xlarge': 0.17,
            }

            analysis = []
            for instance_type in instances:
                cost = costs_per_hour.get(instance_type, 0)
                monthly_cost = cost * 24 * 30
                analysis.append({
                    'type': instance_type,
                    'hourly_cost': cost,
                    'monthly_cost': monthly_cost
                })

            return analysis

        def suggest_alternatives(instance_type: str) -> List[Dict]:
            """Suggest cheaper alternatives for an instance type"""
            # Simplified mapping (would use AWS pricing API in production)
            alternatives = {
                'm5.xlarge': [
                    {'type': 't3.xlarge', 'savings_percent': 56, 'use_case': 'bursty workloads'},
                    {'type': 'm5.large', 'savings_percent': 50, 'use_case': 'reduce to 2 vCPUs'},
                    {'type': 'm5.xlarge spot', 'savings_percent': 70, 'use_case': 'fault-tolerant workloads'},
                ],
                't2.medium': [
                    {'type': 't3.medium', 'savings_percent': 10, 'use_case': 'better CPU credits'},
                    {'type': 't3.small', 'savings_percent': 50, 'use_case': 'if underutilized'},
                ],
            }
            return alternatives.get(instance_type, [])

        def calculate_reserved_instance_savings(instance_type: str, quantity: int) -> Dict:
            """Calculate savings from reserved instances"""
            # 1-year RI discount: ~30%, 3-year: ~50%
            on_demand_cost = {
                't2.medium': 0.0464,
                'm5.xlarge': 0.192,
            }.get(instance_type, 0.1)

            monthly_on_demand = on_demand_cost * 24 * 30 * quantity
            monthly_1yr_ri = monthly_on_demand * 0.7  # 30% discount
            monthly_3yr_ri = monthly_on_demand * 0.5  # 50% discount

            return {
                'on_demand_monthly': monthly_on_demand,
                '1yr_ri_monthly': monthly_1yr_ri,
                '1yr_savings': monthly_on_demand - monthly_1yr_ri,
                '3yr_ri_monthly': monthly_3yr_ri,
                '3yr_savings': monthly_on_demand - monthly_3yr_ri,
            }

        # Create LangChain Tools
        return [
            Tool(
                name="AnalyzeInstanceSizes",
                func=analyze_instance_sizes,
                description="Analyze instance types in infrastructure code and calculate costs"
            ),
            Tool(
                name="SuggestAlternatives",
                func=suggest_alternatives,
                description="Suggest cheaper alternatives for an instance type"
            ),
            Tool(
                name="CalculateRISavings",
                func=calculate_reserved_instance_savings,
                description="Calculate reserved instance savings"
            ),
        ]
```

### Step 3: Create LangChain Agent

```python
    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)

        # Create tools
        self.tools = self._create_tools()

        # Create LangChain agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5
        )
```

### Step 4: Implement Analysis Method

```python
    def analyze(self, code: str, context: str = "") -> WizardResult:
        """Analyze infrastructure code for cost optimization"""

        # Use LangChain agent to analyze code
        prompt = f"""
        Analyze this infrastructure code for cost optimization opportunities:

        {code}

        Context: {context}

        Use the available tools to:
        1. Identify instance types and calculate current costs
        2. Suggest cheaper alternatives
        3. Calculate reserved instance savings

        Provide:
        - Current monthly cost estimate
        - Optimization recommendations
        - Potential monthly savings

        Be specific and include numbers.
        """

        # Run agent
        agent_response = self.agent.run(prompt)

        # Parse response and extract recommendations
        recommendations = self._parse_recommendations(agent_response)

        # Create code examples
        code_examples = self._generate_code_examples(code, recommendations)

        return WizardResult(
            wizard=self.name,
            diagnosis=agent_response,
            recommendations=recommendations,
            code_examples=code_examples,
            confidence=0.85,
            predicted_impact={
                'timeline': '30 days',
                'severity': 'medium',
                'affected_areas': ['infrastructure cost']
            }
        )

    def _parse_recommendations(self, agent_response: str) -> List[str]:
        """Extract actionable recommendations from agent response"""
        recommendations = []

        # Look for bullet points or numbered lists
        lines = agent_response.split('\n')
        for line in lines:
            if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                recommendation = line.strip().lstrip('-*•0123456789. ')
                if len(recommendation) > 10:  # Filter out short lines
                    recommendations.append(recommendation)

        return recommendations if recommendations else ["Review infrastructure costs monthly"]

    def _generate_code_examples(self, original_code: str, recommendations: List[str]) -> List[CodeExample]:
        """Generate before/after code examples"""
        examples = []

        # Example: Detect t2.medium and suggest t3.medium
        if 't2.medium' in original_code and any('t3.medium' in r for r in recommendations):
            examples.append(CodeExample(
                language='hcl',
                code='''# Before (t2.medium)
resource "aws_instance" "web" {
  instance_type = "t2.medium"
  ami           = "ami-12345678"
}

# After (t3.medium - 10% savings, better CPU credits)
resource "aws_instance" "web" {
  instance_type = "t3.medium"
  ami           = "ami-12345678"
}''',
                explanation="Switching from t2.medium to t3.medium saves 10% and provides better CPU credit performance"
            ))

        # Example: Suggest reserved instances
        if any('reserved' in r.lower() for r in recommendations):
            examples.append(CodeExample(
                language='text',
                code='''# Current: On-demand instances
Monthly cost: $138.24

# Recommended: 1-year Reserved Instances
Monthly cost: $96.77
Annual savings: $497.64 (36%)

# Alternative: 3-year Reserved Instances
Monthly cost: $69.12
Annual savings: $829.44 (60%)''',
                explanation="Reserved instances provide significant savings for steady-state workloads"
            ))

        return examples
```

### Step 5: Implement Level 4 Prediction

```python
    def predict(self, code: str, context: str = "", timeline_days: int = 90) -> Prediction:
        """Predict future infrastructure costs"""

        # Analyze current costs
        result = self.analyze(code, context)

        # Create prediction prompt
        prediction_prompt = f"""
        Based on this infrastructure code analysis:

        {result.diagnosis}

        Predict what will happen in the next {timeline_days} days if no changes are made.

        Consider:
        - Typical growth rate (20% month-over-month for startups, 5% for mature companies)
        - Auto-scaling behavior
        - Seasonal traffic patterns
        - Current spend trend

        Provide:
        - Cost forecast for {timeline_days} days
        - Timeline of when cost thresholds will be hit
        - Impact analysis
        - Preventive actions

        Be specific with dates and dollar amounts.
        """

        # Use LangChain LLM to generate prediction
        prediction_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["prompt"],
                template="{prompt}"
            )
        )

        prediction_text = prediction_chain.run(prompt=prediction_prompt)

        return Prediction(
            wizard=self.name,
            prediction=prediction_text,
            timeline_days=timeline_days,
            confidence=0.75,
            preventive_actions=self._extract_preventive_actions(prediction_text)
        )

    def _extract_preventive_actions(self, prediction_text: str) -> List[str]:
        """Extract preventive actions from prediction"""
        actions = []

        # Look for action-oriented phrases
        action_patterns = [
            r'(?:should|must|need to|recommended to)\s+([^.]+)',
            r'(?:action|step):\s*([^.\n]+)',
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, prediction_text, re.IGNORECASE)
            actions.extend(matches)

        return actions[:5]  # Return top 5 actions
```

### Step 6: Full Implementation

```python
# custom_wizards/cost_optimization_wizard.py

from coach.base_wizard import BaseWizard, WizardResult, Prediction, CodeExample
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, Dict
import re

class CostOptimizationWizard(BaseWizard):
    """Analyzes infrastructure code for cost optimization opportunities

    Built on LangChain with custom tools for cloud cost analysis.
    """

    name = "CostOptimizationWizard"
    expertise = "Cloud infrastructure cost optimization and forecasting"
    version = "1.0.0"

    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)
        self.tools = self._create_tools()
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

    def analyze(self, code: str, context: str = "") -> WizardResult:
        """Analyze infrastructure code for cost optimization"""

        prompt = f"""
        Analyze this infrastructure code for cost optimization:

        {code}

        Context: {context}

        Use tools to:
        1. Identify instance types and costs
        2. Suggest alternatives
        3. Calculate RI savings

        Provide specific recommendations with cost estimates.
        """

        agent_response = self.agent.run(prompt)
        recommendations = self._parse_recommendations(agent_response)
        code_examples = self._generate_code_examples(code, recommendations)

        return WizardResult(
            wizard=self.name,
            diagnosis=agent_response,
            recommendations=recommendations,
            code_examples=code_examples,
            confidence=0.85
        )

    def predict(self, code: str, context: str = "", timeline_days: int = 90) -> Prediction:
        """Predict future infrastructure costs"""

        result = self.analyze(code, context)

        prediction_prompt = f"""
        Based on this analysis: {result.diagnosis}

        Predict costs for next {timeline_days} days.
        Include timeline, thresholds, and preventive actions.
        """

        prediction_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["prompt"],
                template="{prompt}"
            )
        )

        prediction_text = prediction_chain.run(prompt=prediction_prompt)

        return Prediction(
            wizard=self.name,
            prediction=prediction_text,
            timeline_days=timeline_days,
            confidence=0.75,
            preventive_actions=self._extract_preventive_actions(prediction_text)
        )

    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools"""

        def analyze_instance_sizes(code: str) -> str:
            pattern = r'instance_type\s*=\s*["\']([^"\']+)["\']'
            instances = re.findall(pattern, code, re.IGNORECASE)

            costs = {'t2.micro': 0.0116, 't2.medium': 0.0464, 'm5.xlarge': 0.192}

            result = []
            for inst in instances:
                cost = costs.get(inst, 0.1)
                monthly = cost * 24 * 30
                result.append(f"{inst}: ${monthly:.2f}/month")

            return "\n".join(result) if result else "No instances found"

        def suggest_alternatives(instance_type: str) -> str:
            alts = {
                'm5.xlarge': "t3.xlarge (56% savings, bursty workloads)",
                't2.medium': "t3.medium (10% savings, better CPU credits)"
            }
            return alts.get(instance_type, "No alternatives found")

        def calculate_ri_savings(instance_type: str) -> str:
            on_demand_costs = {'t2.medium': 0.0464, 'm5.xlarge': 0.192}
            cost = on_demand_costs.get(instance_type, 0.1)
            monthly_on_demand = cost * 24 * 30

            monthly_1yr = monthly_on_demand * 0.7
            monthly_3yr = monthly_on_demand * 0.5

            return f"""On-demand: ${monthly_on_demand:.2f}/month
1-year RI: ${monthly_1yr:.2f}/month (save ${monthly_on_demand - monthly_1yr:.2f})
3-year RI: ${monthly_3yr:.2f}/month (save ${monthly_on_demand - monthly_3yr:.2f})"""

        return [
            Tool(
                name="AnalyzeInstanceSizes",
                func=analyze_instance_sizes,
                description="Analyze instance types and costs in code"
            ),
            Tool(
                name="SuggestAlternatives",
                func=suggest_alternatives,
                description="Suggest cheaper instance alternatives"
            ),
            Tool(
                name="CalculateRISavings",
                func=calculate_ri_savings,
                description="Calculate reserved instance savings"
            ),
        ]

    def _parse_recommendations(self, response: str) -> List[str]:
        recommendations = []
        for line in response.split('\n'):
            if line.strip().startswith(('-', '*', '•')):
                rec = line.strip().lstrip('-*• ')
                if len(rec) > 10:
                    recommendations.append(rec)
        return recommendations or ["Review costs monthly"]

    def _generate_code_examples(self, code: str, recommendations: List[str]) -> List[CodeExample]:
        examples = []

        if 't2.medium' in code:
            examples.append(CodeExample(
                language='hcl',
                code='# Switch t2.medium → t3.medium for 10% savings',
                explanation="t3 instances have better CPU credits and cost less"
            ))

        return examples

    def _extract_preventive_actions(self, prediction: str) -> List[str]:
        actions = []
        pattern = r'(?:should|must|recommended?)\s+([^.]+)'
        matches = re.findall(pattern, prediction, re.IGNORECASE)
        return matches[:5]
```

### Step 7: Use Your Wizard

```python
# example_usage.py

from custom_wizards.cost_optimization_wizard import CostOptimizationWizard
from langchain.chat_models import ChatOpenAI

# Initialize wizard
wizard = CostOptimizationWizard(llm=ChatOpenAI(model="gpt-4", temperature=0))

# Example infrastructure code
terraform_code = '''
resource "aws_instance" "web" {
  instance_type = "m5.xlarge"
  ami           = "ami-12345678"
  count         = 3
}

resource "aws_instance" "worker" {
  instance_type = "t2.medium"
  ami           = "ami-87654321"
  count         = 10
}
'''

# Analyze
result = wizard.analyze(terraform_code, context="E-commerce platform")

print("=== Cost Analysis ===")
print(result.diagnosis)
print("\n=== Recommendations ===")
for i, rec in enumerate(result.recommendations, 1):
    print(f"{i}. {rec}")

print("\n=== Code Examples ===")
for example in result.code_examples:
    print(f"\n{example.code}")
    print(f"→ {example.explanation}")

# Level 4 Prediction
prediction = wizard.predict(terraform_code, timeline_days=90)

print("\n=== 90-Day Cost Prediction ===")
print(prediction.prediction)
print("\n=== Preventive Actions ===")
for action in prediction.preventive_actions:
    print(f"- {action}")
```

### Expected Output

```
=== Cost Analysis ===
Current infrastructure cost analysis:

Web servers (m5.xlarge × 3):
- Current cost: $414.72/month
- Alternative: t3.xlarge for $183.17/month (56% savings)
- Recommendation: Consider t3.xlarge for bursty workloads or use Reserved Instances

Worker instances (t2.medium × 10):
- Current cost: $334.08/month
- Alternative: t3.medium for $299.52/month (10% savings)
- Recommendation: Upgrade to t3.medium for better CPU credits

Total current cost: $748.80/month
Potential savings: $265.03/month (35%)

=== Recommendations ===
1. Consider t3.xlarge for web servers (bursty workloads) - save $231.55/month
2. Use 1-year Reserved Instances for steady-state workloads - save ~30%
3. Upgrade t2.medium to t3.medium for better performance at lower cost
4. Enable auto-scaling to reduce instance count during off-peak hours

=== Code Examples ===
# Switch t2.medium → t3.medium for 10% savings
→ t3 instances have better CPU credits and cost less

=== 90-Day Cost Prediction ===
Based on current configuration and typical growth patterns:

Timeline:
- Day 0-30: $748.80/month (current)
- Day 30-60: $898.56/month (20% growth)
- Day 60-90: $1,078.27/month (20% growth)

Cost Milestones:
- Day 40: Cross $1,000/month threshold
- Day 75: Approach $1,200/month

Impact if no action taken:
- Total 90-day cost: $2,725.63
- Missed savings: $795.09 (from recommended optimizations)

=== Preventive Actions ===
- Purchase 1-year Reserved Instances for web servers within 14 days
- Migrate to t3 instances before Day 30
- Set up cost alerts at $800/month threshold
- Enable auto-scaling for worker instances
- Schedule monthly cost reviews
```

---

## Advanced Features

### 1. Using LangChain Memory

Add conversation memory to your wizard:

```python
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor

class StatefulWizard(BaseWizard):
    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)

        # Add memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Create agent with memory
        self.agent = AgentExecutor.from_agent_and_tools(
            agent=self._create_agent(),
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def analyze(self, code: str, context: str = "") -> WizardResult:
        # Memory automatically tracks conversation
        result = self.agent.run(f"Analyze: {code}")
        return WizardResult(wizard=self.name, diagnosis=result)
```

### 2. Using Custom LangChain Tools

Create sophisticated tools:

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class DatabaseQueryTool(BaseTool):
    name = "database_query_analyzer"
    description = "Analyzes database queries for performance issues"

    class InputSchema(BaseModel):
        query: str = Field(description="SQL query to analyze")

    def _run(self, query: str) -> str:
        # Your analysis logic
        if 'SELECT *' in query:
            return "Warning: SELECT * is inefficient"
        return "Query looks good"

    async def _arun(self, query: str) -> str:
        # Async version
        return self._run(query)

# Use in wizard
class DatabasePerformanceWizard(BaseWizard):
    def _create_tools(self):
        return [DatabaseQueryTool()]
```

### 3. Using Lang Chain Callbacks

Track wizard execution:

```python
from langchain.callbacks import StdOutCallbackHandler, StreamingStdOutCallbackHandler

class MyWizard(BaseWizard):
    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)

        # Add callbacks for debugging
        callbacks = [
            StdOutCallbackHandler(),
            CustomCallbackHandler()
        ]

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            callbacks=callbacks
        )

class CustomCallbackHandler:
    def on_tool_start(self, tool, input_str, **kwargs):
        print(f"[TOOL START] {tool}: {input_str}")

    def on_tool_end(self, output, **kwargs):
        print(f"[TOOL END] {output}")

    def on_llm_start(self, prompts, **kwargs):
        print(f"[LLM START] Prompt length: {len(prompts[0])}")
```

### 4. Using Multiple LLMs

Use different models for different tasks:

```python
from langchain.chat_models import ChatOpenAI, ChatAnthropic

class HybridWizard(BaseWizard):
    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)

        # Fast model for simple tasks
        self.fast_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # Powerful model for complex analysis
        self.smart_llm = ChatAnthropic(model="claude-3-opus", temperature=0)

    def analyze(self, code: str, context: str = "") -> WizardResult:
        # Use fast model for initial classification
        classification_chain = LLMChain(
            llm=self.fast_llm,
            prompt=PromptTemplate(
                input_variables=["code"],
                template="Classify this code: {code}\nCategory:"
            )
        )

        category = classification_chain.run(code=code)

        # Use smart model for deep analysis
        analysis_chain = LLMChain(
            llm=self.smart_llm,
            prompt=PromptTemplate(
                input_variables=["code", "category"],
                template="Deep analysis of {category} code:\n{code}"
            )
        )

        diagnosis = analysis_chain.run(code=code, category=category)

        return WizardResult(wizard=self.name, diagnosis=diagnosis)
```

### 5. Wizard Collaboration

Make your wizard consult other wizards:

```python
class CollaborativeWizard(BaseWizard):
    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)
        self.coach = config.get('coach_instance')  # Access to Coach

    def analyze(self, code: str, context: str = "") -> WizardResult:
        # Do your analysis
        my_analysis = self._my_analysis(code)

        # Consult SecurityWizard if needed
        if 'password' in code.lower():
            security_result = self.coach.run_wizard(
                "SecurityWizard",
                code=code,
                context="Security review requested by CostOptimizationWizard"
            )

            my_analysis += f"\n\nSecurity concerns: {security_result.diagnosis}"

        return WizardResult(wizard=self.name, diagnosis=my_analysis)
```

---

## Testing Your Wizard

### Unit Tests

```python
# tests/test_cost_optimization_wizard.py

import pytest
from unittest.mock import Mock, patch
from custom_wizards.cost_optimization_wizard import CostOptimizationWizard
from langchain.chat_models import ChatOpenAI

@pytest.fixture
def wizard():
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    return CostOptimizationWizard(llm=llm)

def test_wizard_initialization(wizard):
    assert wizard.name == "CostOptimizationWizard"
    assert wizard.expertise == "Cloud infrastructure cost optimization and forecasting"
    assert len(wizard.tools) == 3

def test_analyze_terraform_code(wizard):
    terraform_code = '''
    resource "aws_instance" "web" {
      instance_type = "t2.medium"
    }
    '''

    result = wizard.analyze(terraform_code)

    assert result.wizard == "CostOptimizationWizard"
    assert result.confidence > 0.5
    assert len(result.recommendations) > 0

def test_tool_analyze_instance_sizes(wizard):
    tool = wizard.tools[0]  # AnalyzeInstanceSizes

    code = 'instance_type = "m5.xlarge"'
    result = tool.func(code)

    assert "m5.xlarge" in result
    assert "$" in result  # Should contain cost

def test_predict_costs(wizard):
    code = 'instance_type = "t2.medium"'

    prediction = wizard.predict(code, timeline_days=90)

    assert prediction.wizard == "CostOptimizationWizard"
    assert prediction.timeline_days == 90
    assert len(prediction.preventive_actions) > 0

@patch('langchain.agents.AgentExecutor.run')
def test_analyze_with_mocked_agent(mock_run, wizard):
    # Mock agent response
    mock_run.return_value = "Current cost: $100/month. Recommend switching to t3.medium."

    result = wizard.analyze('instance_type = "t2.medium"')

    assert "t3.medium" in result.diagnosis
    mock_run.assert_called_once()
```

### Integration Tests

```python
# tests/test_wizard_integration.py

import pytest
from custom_wizards.cost_optimization_wizard import CostOptimizationWizard
from langchain.chat_models import ChatOpenAI

@pytest.mark.integration
def test_end_to_end_analysis():
    """Full end-to-end test with real LLM"""

    wizard = CostOptimizationWizard(llm=ChatOpenAI(model="gpt-4"))

    terraform_code = '''
    resource "aws_instance" "app" {
      instance_type = "m5.2xlarge"
      count         = 5
    }
    '''

    # Analyze
    result = wizard.analyze(terraform_code, context="Production environment")

    # Assertions
    assert result.wizard == "CostOptimizationWizard"
    assert result.confidence > 0.7
    assert len(result.recommendations) >= 3
    assert any('cost' in r.lower() for r in result.recommendations)
    assert len(result.code_examples) > 0

    # Predict
    prediction = wizard.predict(terraform_code, timeline_days=60)

    assert prediction.timeline_days == 60
    assert '$' in prediction.prediction  # Should mention costs
    assert len(prediction.preventive_actions) > 0
```

### Test with Different LLMs

```python
@pytest.mark.parametrize("llm_model", [
    "gpt-3.5-turbo",
    "gpt-4",
    "claude-3-sonnet",
])
def test_wizard_with_different_llms(llm_model):
    from langchain.chat_models import ChatOpenAI, ChatAnthropic

    if llm_model.startswith("gpt"):
        llm = ChatOpenAI(model=llm_model)
    else:
        llm = ChatAnthropic(model=llm_model)

    wizard = CostOptimizationWizard(llm=llm)
    result = wizard.analyze('instance_type = "t2.micro"')

    assert result.confidence > 0.5
```

---

## Deployment

### 1. Register Your Wizard

```python
# coach/wizards/__init__.py

from coach.wizards.security import SecurityWizard
from coach.wizards.performance import PerformanceWizard
# ... other wizards ...

# Import your custom wizard
from custom_wizards.cost_optimization_wizard import CostOptimizationWizard

def get_all_wizards():
    """Return all available wizards"""
    return [
        SecurityWizard(),
        PerformanceWizard(),
        # ... other wizards ...
        CostOptimizationWizard(),  # Add yours!
    ]
```

### 2. Package Your Wizard

```python
# setup.py

from setuptools import setup, find_packages

setup(
    name="coach-cost-optimization-wizard",
    version="1.0.0",
    description="Cost optimization wizard for Coach",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.5",
        "coach-ai>=0.1.0",
    ],
    entry_points={
        "coach.wizards": [
            "cost_optimization = custom_wizards.cost_optimization_wizard:CostOptimizationWizard",
        ],
    },
)
```

### 3. Share with Team

```bash
# Install from local directory
pip install -e /path/to/your/wizard

# Or build and share wheel
python setup.py bdist_wheel
# Share dist/coach-cost-optimization-wizard-1.0.0-py3-none-any.whl
```

---

## Best Practices

### 1. Prompt Engineering

**Good Prompt** (specific, structured):
```python
template = """
You are a {wizard_name} analyzing code for {purpose}.

Code to analyze:
```
{code}
```

Context: {context}

Tasks:
1. Identify {specific_thing_1}
2. Check for {specific_thing_2}
3. Recommend {specific_action}

Format your response as:
- Diagnosis: [clear description]
- Issues Found: [bulleted list]
- Recommendations: [numbered list]
- Confidence: [0-100%]

Be concise but specific. Include code examples where helpful.
"""
```

**Bad Prompt** (vague):
```python
template = "Analyze this code: {code}"
```

### 2. Tool Design

**Good Tool** (focused, single purpose):
```python
def detect_sql_injection(code: str) -> List[Dict]:
    """Detect SQL injection vulnerabilities"""
    # ... specific logic ...
    return [{'line': 42, 'issue': 'SQL injection', 'severity': 'high'}]
```

**Bad Tool** (does everything):
```python
def analyze_everything(code: str) -> str:
    """Analyze code for all issues"""
    # Too broad, agent doesn't know when to use this
```

### 3. Error Handling

```python
from langchain.schema import OutputParserException

class RobustWizard(BaseWizard):
    def analyze(self, code: str, context: str = "") -> WizardResult:
        try:
            result = self.agent.run(code)
            return self._parse_result(result)

        except OutputParserException as e:
            # Fallback to simpler analysis
            return WizardResult(
                wizard=self.name,
                diagnosis="Analysis partially failed. Basic check: code is valid Python.",
                recommendations=["Rerun analysis with more context"],
                confidence=0.3
            )

        except Exception as e:
            # Log error but return graceful failure
            logger.error(f"Wizard {self.name} failed: {e}")
            return WizardResult(
                wizard=self.name,
                diagnosis=f"Analysis failed: {str(e)}",
                recommendations=["Check wizard configuration"],
                confidence=0.0
            )
```

### 4. Confidence Scoring

```python
def analyze(self, code: str, context: str = "") -> WizardResult:
    result = self.agent.run(code)

    # Calculate confidence based on multiple factors
    confidence = 0.5  # Base confidence

    # Increase if specific patterns detected
    if re.search(r'instance_type\s*=', code):
        confidence += 0.2

    # Increase if context provided
    if context:
        confidence += 0.1

    # Decrease if uncertain language in response
    uncertain_words = ['maybe', 'possibly', 'might', 'unclear']
    if any(word in result.lower() for word in uncertain_words):
        confidence -= 0.2

    confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

    return WizardResult(
        wizard=self.name,
        diagnosis=result,
        confidence=confidence
    )
```

### 5. Performance Optimization

```python
from functools import lru_cache
import hashlib

class CachedWizard(BaseWizard):
    @lru_cache(maxsize=100)
    def _analyze_cached(self, code_hash: str, context: str) -> str:
        """Cache expensive LLM calls"""
        return self.agent.run(f"Analyze: {code_hash}")

    def analyze(self, code: str, context: str = "") -> WizardResult:
        # Hash code for caching
        code_hash = hashlib.md5(code.encode()).hexdigest()

        # Use cached result if available
        diagnosis = self._analyze_cached(code_hash, context)

        return WizardResult(wizard=self.name, diagnosis=diagnosis)
```

---

## Examples Gallery

### Example 1: ContractComplianceWizard

```python
class ContractComplianceWizard(BaseWizard):
    """Checks code against legal/contract requirements"""

    name = "ContractComplianceWizard"
    expertise = "SLA and contract compliance verification"

    def _create_tools(self):
        return [
            Tool(
                name="CheckSLA",
                func=lambda code: self._check_sla_compliance(code),
                description="Check if code meets SLA requirements"
            ),
            Tool(
                name="CheckDataRetention",
                func=lambda code: self._check_data_retention(code),
                description="Verify data retention policies"
            ),
        ]

    def _check_sla_compliance(self, code: str) -> str:
        # Example: Check for 99.9% uptime requirements
        if 'availability' not in code.lower():
            return "⚠️ No availability metrics found. SLA requires 99.9% uptime tracking."
        return "✓ Availability tracking detected"
```

### Example 2: A11yReviewWizard (Enhanced Accessibility)

```python
class A11yReviewWizard(AccessibilityWizard):
    """Enhanced accessibility wizard with AI-powered recommendations"""

    def __init__(self, llm=None, config=None):
        super().__init__(llm, config)

        # Add LangChain agent for semantic analysis
        self.semantic_agent = initialize_agent(
            tools=[
                Tool(
                    name="CheckSemanticHTML",
                    func=self._check_semantic_html,
                    description="Analyze HTML for semantic correctness"
                ),
            ],
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )

    def analyze(self, code: str, context: str = "") -> WizardResult:
        # Run base accessibility checks
        base_result = super().analyze(code, context)

        # Add AI-powered semantic analysis
        semantic_analysis = self.semantic_agent.run(
            f"Check this HTML for semantic issues:\n{code}"
        )

        # Combine results
        enhanced_diagnosis = f"{base_result.diagnosis}\n\n### Semantic Analysis\n{semantic_analysis}"

        return WizardResult(
            wizard=self.name,
            diagnosis=enhanced_diagnosis,
            recommendations=base_result.recommendations,
            confidence=base_result.confidence
        )
```

### Example 3: LicenseComplianceWizard

```python
class LicenseComplianceWizard(BaseWizard):
    """Checks open source license compliance"""

    name = "LicenseComplianceWizard"
    expertise = "Open source license compliance"

    def _create_tools(self):
        return [
            Tool(
                name="DetectLicenses",
                func=self._detect_licenses,
                description="Detect licenses in dependencies"
            ),
            Tool(
                name="CheckCompatibility",
                func=self._check_license_compatibility,
                description="Check if licenses are compatible"
            ),
        ]

    def _detect_licenses(self, code: str) -> str:
        # Parse package.json or requirements.txt
        # Return licenses found
        pass

    def _check_license_compatibility(self, licenses: List[str]) -> str:
        # Check for incompatibilities (e.g., GPL + Proprietary)
        pass
```

---

## Resources

### LangChain Documentation
- [LangChain Docs](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)

### Coach Resources
- [Coach Discord](https://discord.gg/coach-alpha) - Get help from the community
- [Coach GitHub](https://github.com/deepstudyai/coach-alpha) - Examples and issues
- [Wizard Examples](https://github.com/deepstudyai/coach-alpha/tree/main/examples/wizards)

### Tutorials
- [LangChain Tutorial](https://python.langchain.com/docs/get_started/quickstart)
- [Building Custom Agents](https://python.langchain.com/docs/modules/agents/how_to/custom_agent)
- [Creating Tools](https://python.langchain.com/docs/modules/agents/tools/custom_tools)

---

## Next Steps

1. **Build your wizard**: Start with the Quick Start wizard and customize it
2. **Test thoroughly**: Use pytest and test with different inputs
3. **Share with team**: Package and deploy your wizard
4. **Contribute**: Share your wizard with the Coach community!

---

**Questions?** Join [Coach Discord](https://discord.gg/coach-alpha) #custom-wizards channel

**Built with** ❤️ **using LangChain**
