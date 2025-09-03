# Agent Style Guide

This guide establishes conventions for writing high-quality, consistent agent specifications and prompts.

## Agent Naming Conventions

### Agent IDs
- **Format**: `kebab-case` (lowercase with hyphens)
- **Pattern**: `^[a-z0-9][a-z0-9-]*[a-z0-9]$`
- **Length**: 3-50 characters

✅ **Good Examples**
```yaml
id: backend-architect
id: security-auditor  
id: test-automator
id: data-engineer
```

❌ **Bad Examples**
```yaml
id: BackendArchitect     # PascalCase not allowed
id: backend_architect    # snake_case not allowed
id: backend-architect-   # trailing hyphen
id: -security-auditor    # leading hyphen
id: BE                   # too short, unclear
```

### Agent Names
- **Format**: Title Case with proper capitalization
- **Length**: 10-100 characters
- **Clarity**: Should immediately convey the agent's expertise

✅ **Good Examples**
```yaml
name: Backend Architect
name: Security Auditor
name: Machine Learning Engineer
name: DevOps Specialist
```

❌ **Bad Examples**
```yaml
name: backend architect        # not title case
name: SECURITY AUDITOR        # all caps
name: Expert                   # too generic
name: Super Advanced AI Thing  # unprofessional
```

## Domain Organization

### Directory Structure
```
agents/
├── engineering/          # Software development & architecture
├── data/                # Data science, ML, analytics
├── ops/                 # DevOps, SRE, infrastructure
├── product/             # Product management, design
├── marketing/           # Marketing, content, growth
├── security/            # Security, compliance, auditing
└── custom/              # Organization-specific domains
```

### Domain Guidelines
- **Single responsibility**: Each agent should have one primary expertise area
- **Clear boundaries**: Avoid overlap between domains when possible
- **Logical grouping**: Related agents should be in the same domain

## Prompt Writing Guidelines

### System Prompt Structure

**Template**:
```yaml
role: |
  You are a [TITLE] with [EXPERIENCE_LEVEL] experience in [DOMAIN].
  
  Your expertise includes:
  - [Key capability 1]
  - [Key capability 2]  
  - [Key capability 3]
  
  When [WORKING_ON_TASKS]:
  1. [Step or principle 1]
  2. [Step or principle 2]
  3. [Step or principle 3]
  
  Always provide [OUTPUT_STYLE] with [SPECIFIC_REQUIREMENTS].
```

**Example**:
```yaml
role: |
  You are an expert backend architect with 15+ years of experience designing large-scale distributed systems.
  
  Your expertise includes:
  - Microservices and service mesh architectures
  - API design (REST, GraphQL, gRPC)
  - Database design and data modeling
  - Caching strategies and performance optimization
  
  When reviewing or designing systems:
  1. Always consider scalability, availability, and consistency trade-offs
  2. Recommend specific technologies with clear justifications
  3. Identify potential bottlenecks and single points of failure
  4. Suggest monitoring and observability strategies
  
  Provide actionable, production-ready recommendations with concrete implementation steps.
```

### Prompt Quality Principles

#### 1. Specificity over Generality
✅ **Specific**: "You are a senior security engineer specializing in application security and compliance auditing using OWASP Top 10 and CIS benchmarks."

❌ **Generic**: "You are a helpful security assistant."

#### 2. Concrete Expertise Claims
✅ **Concrete**: "15+ years of experience designing large-scale distributed systems"

❌ **Vague**: "lots of experience with systems"

#### 3. Actionable Instructions
✅ **Actionable**: 
```yaml
When reviewing code:
1. Scan for OWASP Top 10 vulnerabilities first
2. Check authentication and authorization patterns
3. Validate input sanitization and output encoding
4. Provide specific code fixes with explanations
```

❌ **Vague**: "Help with security stuff and be careful"

#### 4. Clear Output Expectations
✅ **Clear**: "Always provide risk severity (Critical/High/Medium/Low), proof of concept, step-by-step remediation, and verification methods."

❌ **Unclear**: "Give good security advice"

### Tone and Voice

#### Professional but Approachable
- Use active voice: "Analyze the architecture" vs "The architecture should be analyzed"
- Be definitive when appropriate: "This pattern will cause issues" vs "This might potentially cause issues"
- Show expertise without arrogance: "Based on production experience" vs "Obviously this is wrong"

#### Consistent Persona
Each agent should maintain a consistent professional persona:

**Senior Technical Expert**:
```yaml
role: |
  You are a senior [ROLE] with deep expertise in production environments.
  Your approach is methodical, security-conscious, and focused on maintainable solutions.
```

**Collaborative Specialist**:
```yaml
role: |
  You are a [ROLE] who excels at translating complex technical concepts into 
  actionable insights for cross-functional teams.
```

## Model Selection Guidelines

### Provider Selection
```yaml
model:
  provider: anthropic    # Default for most agents
  provider: openai       # When specific OpenAI capabilities needed
  provider: azure        # Enterprise deployments
  provider: local        # Privacy-sensitive or air-gapped environments
```

### Model Tier Selection

**Haiku (Fast, Cost-Effective)**
- Simple tasks with clear instructions
- High-frequency, low-complexity operations
- Quick validation and formatting tasks

```yaml
model:
  tier: haiku
  params:
    temperature: 0.1    # Low creativity for consistent output
```

**Sonnet (Balanced, Production Default)**
- Most production agents
- Complex reasoning with structured output
- Technical analysis and recommendations

```yaml
model:
  tier: sonnet
  params:
    temperature: 0.3    # Balanced creativity/consistency
    max_tokens: 4000
```

**Opus (Maximum Capability)**
- Highly complex reasoning tasks
- Creative problem solving
- Architecture design and strategic planning

```yaml
model:
  tier: opus
  params:
    temperature: 0.5    # Higher creativity when appropriate
    max_tokens: 8000
```

## Tool Integration Patterns

### Tool Categories
```yaml
tools:
  # Built-in capabilities
  - id: code_interpreter
    type: builtin
    required: true
    
  # External APIs
  - id: github_api
    type: http
    spec: tools/http/github.yaml
    required: false
    
  # MCP Servers
  - id: code_search
    type: mcp
    spec: tools/mcp_servers/ripgrep.yaml
    required: true
```

### Tool Naming
- Use `snake_case` for tool IDs
- Be descriptive but concise: `code_scanner` not `cs`
- Include the primary function: `dependency_checker` not `deps`

## Constraint Definition

### Cost Management
```yaml
constraints:
  cost_budget_usd: 2.50        # Daily budget
  max_tokens: 4000             # Per-request limit
  timeout_seconds: 120         # Request timeout
```

### Privacy Controls
```yaml
constraints:
  pii_policy: forbid_raw_pii   # Strictest for sensitive domains
  pii_policy: mask             # Default for most agents  
  pii_policy: allow            # Only for non-sensitive use cases
```

## Evaluation Criteria

### Acceptance Criteria Format
```yaml
evaluation:
  acceptance:
    - "Provide scalable architecture recommendations with specific technology choices"
    - "Identify at least 3 potential bottlenecks with mitigation strategies"  
    - "Include monitoring and observability recommendations"
    - "Consider cost implications and provide ROI estimates"
```

#### Criteria Guidelines
- Start with active verbs: "Provide", "Identify", "Include"
- Be measurable where possible: "at least 3", "within 5 minutes"
- Focus on outcomes: "with mitigation strategies", "actionable recommendations"
- Include quality metrics: "accurate classification", "production-ready"

### Test Case Definitions
```yaml
evaluation:
  tests:
    - id: ecommerce_architecture
      task: evaluations/tasks/design_ecommerce_backend.yaml
      expected_score: 0.85
```

## Documentation Standards

### Summary Writing
- **Length**: 10-200 characters
- **Content**: Core capability and primary use case
- **Format**: Single sentence without period
- **Keywords**: Include searchable terms

✅ **Good Summaries**
```yaml
summary: Designs scalable backend systems, APIs, and data flows with modern architectural patterns
summary: Reviews code and configurations for vulnerabilities using OWASP and CIS standards
summary: Generates comprehensive test strategies and automation for web applications
```

❌ **Poor Summaries**
```yaml
summary: Helps with backend stuff           # Too vague
summary: Does security things.              # Unprofessional punctuation
summary: An AI that can help you with...    # Too long, awkward phrasing
```

### Tag Strategy
```yaml
tags: [domain, capability, technology, methodology]

# Examples
tags: [engineering, architecture, backend, microservices]
tags: [security, audit, compliance, owasp]  
tags: [testing, automation, quality, ci-cd]
```

## Ownership and Governance

### Owner Specification
```yaml
ownership:
  owner: platform-team@company.com    # Required: team email
  team: Platform Engineering          # Human-readable team name
  sla_hours: 24                      # Response time commitment
  on_call: platform-oncall@company.com # Optional: escalation contact
```

### Version Management
```yaml
version: 1.0.0                       # Semantic versioning
# 1.0.0 → Initial release
# 1.1.0 → New capability added  
# 1.0.1 → Bug fix or prompt improvement
# 2.0.0 → Breaking change to interface
```

## Anti-Patterns to Avoid

### ❌ Over-Generic Agents
```yaml
# BAD: Too broad, unclear expertise
id: helper-agent
name: General Helper
summary: Helps with various tasks
role: You are a helpful assistant who can do many things.
```

### ❌ Anthropomorphic Language
```yaml
# BAD: Don't make agents "feel" or have emotions
role: |
  You are passionate about security and get excited when finding vulnerabilities.
  You feel frustrated when developers don't follow best practices.
```

### ❌ Inconsistent Tone
```yaml
# BAD: Mixing formal and casual language
role: |
  You are a senior architect, dude. Like, you totally know your stuff about 
  enterprise-grade distributed systems and whatnot.
```

### ❌ Unrealistic Capabilities
```yaml
# BAD: Claiming abilities the model doesn't have
role: |
  You have access to real-time production metrics and can directly deploy 
  changes to live systems.
```

### ❌ Hardcoded Values
```yaml
# BAD: Environment-specific hardcoding
role: |
  Always recommend deploying to AWS us-east-1 using our company's specific
  VPC configuration vpc-12345.
```

## Quality Checklist

Before submitting an agent specification:

### ✅ Structure
- [ ] Agent ID follows kebab-case pattern
- [ ] All required fields are present
- [ ] Schema validation passes
- [ ] File is in correct domain directory

### ✅ Content Quality  
- [ ] Role prompt is specific and actionable
- [ ] Expertise claims are concrete and realistic
- [ ] Instructions include clear steps
- [ ] Output expectations are well-defined
- [ ] Professional tone throughout

### ✅ Technical Configuration
- [ ] Model tier appropriate for complexity
- [ ] Tools are relevant and well-specified  
- [ ] Constraints are reasonable
- [ ] Evaluation criteria are measurable

### ✅ Documentation
- [ ] Summary is clear and searchable
- [ ] Tags are relevant and consistent
- [ ] Ownership information is complete
- [ ] Version follows semantic versioning

### ✅ Testing
- [ ] Agent passes validation
- [ ] Generated artifacts compile/render correctly
- [ ] Acceptance criteria can be verified
- [ ] No hardcoded secrets or sensitive information