# Claude Agents Repository

A production-ready, multi-runtime agent template system that generates artifacts for **Claude Code Subagents**, **LangGraph**, and **OpenAI Assistants** from a single YAML specification.

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone <repository-url>
cd claude-code-agents
pip install -e ".[dev]"

# 2. Validate existing agents
agents validate

# 3. Generate Claude Code subagents
agents render claude --install

# 4. Generate LangGraph agents
agents render langgraph

# 5. List available agents
agents list-agents
```

## 📋 What's Inside

- **`agents/`** — YAML specifications organized by domain (engineering, data, ops, product)
- **`recipes/`** — Multi-agent workflows for complex tasks  
- **`adapters/`** — Runtime-specific generators (Claude, LangGraph, Assistants)
- **`templates/`** — Jinja2 templates for artifact generation
- **`schemas/`** — JSON Schema validation for specifications
- **`scripts/`** — CLI tools for validation, rendering, and management

## 🏗️ Architecture

### Single Source of Truth
Write once in YAML, deploy everywhere:

```yaml
id: security-auditor
name: Security Auditor  
summary: Reviews code for vulnerabilities using OWASP standards
role: |
  You are a senior security engineer specializing in application security...

model:
  provider: anthropic
  family: claude
  tier: sonnet
  
tools:
  - id: code_scanner
    type: mcp
    spec: tools/mcp_servers/security_scanner.yaml
```

### Multi-Runtime Support

**Claude Code Subagent** → `~/.claude/agents/security-auditor.md`
```markdown
---
name: security-auditor
description: Reviews code for vulnerabilities using OWASP standards
model: sonnet
tools: code_scanner
---

You are a senior security engineer...
```

**LangGraph Agent** → `adapters/langgraph/security_auditor_agent.py`
```python
from langgraph.prebuilt import create_react_agent

class SecurityAuditorAgent:
    def __init__(self):
        self.model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        # ... implementation
```

## 🔧 CLI Commands

### Validation
```bash
# Validate all specifications
agents validate

# Validate specific file
agents validate agents/engineering/security-auditor.yaml

# Verbose validation with detailed errors
agents validate --verbose
```

### Rendering
```bash
# Generate Claude subagents 
agents render claude

# Generate and install to ~/.claude/agents
agents render claude --install

# Generate LangGraph agents
agents render langgraph

# Render specific agent
agents render claude --agent-id security-auditor
```

### Management
```bash
# List all agents
agents list-agents

# Filter by domain
agents list-agents --domain engineering

# Filter by tag
agents list-agents --tag security

# Create new agent from template
agents init-agent my-new-agent --domain custom --name "My New Agent"
```

## 📖 Agent Specification

Agents follow the [Agent Spec v1](schemas/agent-spec-v1.json) schema:

### Required Fields
- **`id`**: Unique identifier (kebab-case)
- **`name`**: Human-readable name
- **`summary`**: Brief capability description  
- **`role`**: System prompt defining behavior
- **`model`**: Provider, family, and tier configuration
- **`ownership`**: Owner contact information
- **`version`**: Semantic version

### Optional Fields
- **`invocation`**: Auto-trigger or explicit invocation
- **`tools`**: MCP servers, HTTP APIs, built-in functions
- **`constraints`**: Token limits, cost budgets, PII policies
- **`memory`**: Ephemeral, persistent, or hybrid storage
- **`evaluation`**: Acceptance criteria and test cases
- **`observability`**: Logging, tracing, and metrics

## 🔄 Multi-Agent Workflows

Recipes define complex workflows combining multiple agents:

```yaml
id: feature-development
name: Complete Feature Development Workflow
graph:
  - stage: planning
    sequence:
      - agent: business-analyst
      - agent: backend-architect
        
  - stage: security_review
    sequence:
      - agent: security-auditor
        
  - stage: implementation
    parallel:
      - agent: docs-architect
      - agent: test-automator
```

## 🏢 Available Agents

### Engineering
- **`backend-architect`** — Scalable system design and API architecture
- **`security-auditor`** — OWASP/CIS compliance and vulnerability assessment  
- **`test-automator`** — Test strategy, automation, and coverage analysis

### Data
- **`data-engineer`** — ETL pipelines, data quality, and warehouse design

### Operations  
- **`incident-responder`** — Structured incident response and post-mortems

### Product
- **`business-analyst`** — Requirements gathering and user story creation
- **`docs-architect`** — Technical documentation and API guides

## 🛡️ Security & Quality

### Built-in Safeguards
- **Schema validation** for all YAML specifications
- **Secret detection** in pre-commit hooks and CI
- **PII policies** configurable per agent
- **Security scanning** with Bandit and Safety

### Quality Gates
- **Automated testing** with pytest (>80% coverage)
- **Code formatting** with Ruff and Black
- **YAML linting** with yamllint  
- **Type checking** with mypy

## 🚀 Getting Started

### 1. Installation
```bash
git clone <repository-url>
cd claude-code-agents
pip install -e ".[dev]"
```

### 2. Set up development environment
```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Validate all specs
agents validate
```

### 3. Create your first agent
```bash
# Initialize from template
agents init-agent my-expert --domain engineering --name "My Expert"

# Edit the generated file
vim agents/engineering/my-expert.yaml

# Validate and render
agents validate agents/engineering/my-expert.yaml
agents render claude --agent-id my-expert --install
```

### 4. Deploy to your runtime

**Claude Code**: Agents are automatically installed to `~/.claude/agents/` with `--install` flag

**LangGraph**: 
```bash
agents render langgraph
cd adapters/langgraph
pip install -r requirements.txt
python app.py  # Starts FastAPI server on :8000
```

## 📊 Success Metrics

- **Time-to-first-agent**: ≤ 10 minutes from clone to working subagent
- **Time-to-first-workflow**: ≤ 20 minutes for 3-stage recipe  
- **Test coverage**: ≥ 80% for critical paths
- **Zero secrets** committed to repository

## 📚 Documentation

- [Architecture Overview](docs/OVERVIEW.md)
- [Agent Style Guide](docs/STYLEGUIDE.md)  
- [Security Policies](docs/SECURITY.md)
- [Contribution Guidelines](docs/CONTRIBUTING.md)

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-agent`)
3. **Follow** the [style guide](docs/STYLEGUIDE.md) for prompts and naming
4. **Add tests** for new functionality
5. **Run** the full validation suite (`make test`)
6. **Submit** a pull request

## 📄 License

Apache-2.0 — see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)  
- **Docs**: [Full Documentation](docs/)

---

**⚡ Built for production** • **🔒 Security-first** • **🚀 Developer-friendly**