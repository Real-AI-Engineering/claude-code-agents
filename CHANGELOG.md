# Changelog

All notable changes to the Claude Agents Repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- **Agent Specification v1**: Complete JSON Schema for agent definitions
- **Recipe Specification v1**: Multi-agent workflow definitions
- **Claude Code Adapter**: Generate Markdown subagents compatible with `~/.claude/agents`
- **LangGraph Adapter**: Generate Python agents with prebuilt LangGraph integration
- **CLI Tools**: Comprehensive command-line interface for validation, rendering, and management
- **Production Agents**: 6+ ready-to-use agents across engineering, data, ops, and product domains
- **Multi-Agent Recipes**: Feature development, incident response, and performance optimization workflows
- **Security Framework**: PII policies, secret detection, and secure-by-default configurations
- **Testing Suite**: Unit, integration, and property-based tests with >80% coverage
- **CI/CD Pipeline**: GitHub Actions with linting, validation, security scanning, and automated releases
- **Documentation**: Comprehensive guides for architecture, style, and security

### Agent Catalog
- **backend-architect**: Scalable system design and API architecture
- **security-auditor**: OWASP/CIS compliance and vulnerability assessment
- **test-automator**: Test strategy, automation, and coverage analysis
- **data-engineer**: ETL pipelines, data quality, and warehouse design
- **incident-responder**: Structured incident response and post-mortems
- **business-analyst**: Requirements gathering and user story creation
- **docs-architect**: Technical documentation and API guides

### Recipes
- **feature-development**: End-to-end feature development with security review
- **incident-response**: Production incident handling with communication
- **performance-optimization**: Systematic performance analysis and improvement

### Technical Features
- **Multi-Runtime Support**: Single YAML → Claude/LangGraph/Assistant artifacts
- **Schema Validation**: JSON Schema Draft 2020-12 with semantic validation
- **Template Engine**: Jinja2-based generation with extensible filters
- **Quality Gates**: Pre-commit hooks, linting, secret detection
- **Modular Architecture**: Loosely coupled adapters for easy extension

### Security
- **Zero Secrets Policy**: No credentials committed to repository
- **PII Protection**: Configurable privacy policies per agent
- **Supply Chain Security**: Dependency scanning and vulnerability management
- **Access Controls**: Role-based permissions and ownership tracking
- **Audit Logging**: Comprehensive logging for compliance and monitoring

## [Unreleased]

### Planned
- **OpenAI/CrewAI Adapter**: Full support for OpenAI Assistants and CrewAI agents
- **Advanced Recipes**: Conditional logic, loops, and human-in-the-loop workflows
- **Agent Registry**: Centralized service for agent discovery and management
- **Monitoring Dashboard**: Real-time metrics and health monitoring
- **Enterprise Features**: SSO integration, advanced RBAC, audit reports

---

## Versioning Strategy

### Agent Specification Versions
- **v1.x.x**: Current specification format
- **v2.x.x**: Breaking changes to schema structure
- **vX.Y.Z**: Y increment for new fields, Z for clarifications/fixes

### Agent Versions
- **1.0.0**: Initial production release
- **1.Y.0**: New capabilities or major improvements
- **1.0.Z**: Bug fixes, prompt improvements, minor enhancements
- **2.0.0**: Breaking changes to agent interface or behavior

### Repository Versions
- **1.0.0**: Production-ready release with core features
- **1.Y.0**: New adapters, major features, significant improvements
- **1.0.Z**: Bug fixes, documentation updates, minor enhancements
- **2.0.0**: Breaking changes to CLI, file structure, or core APIs