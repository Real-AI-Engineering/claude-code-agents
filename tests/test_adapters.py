"""Tests for adapter functionality."""

import pytest
from pathlib import Path
import tempfile
import yaml

from adapters.claude import ClaudeAdapter
from adapters.langgraph import LangGraphAdapter


class TestClaudeAdapter:
    """Test Claude Code adapter."""
    
    @pytest.fixture
    def claude_adapter(self):
        """Create Claude adapter with templates."""
        templates_dir = Path(__file__).parent.parent / "templates"
        return ClaudeAdapter(templates_dir)
    
    @pytest.fixture
    def sample_agent_spec(self):
        """Sample agent specification for testing."""
        return {
            "id": "test-agent",
            "name": "Test Agent",
            "summary": "A test agent for adapter testing",
            "role": "You are a test agent.",
            "model": {
                "provider": "anthropic",
                "family": "claude",
                "tier": "sonnet"
            },
            "tools": [
                {
                    "id": "test_tool",
                    "type": "builtin",
                    "description": "A test tool"
                }
            ],
            "constraints": {
                "pii_policy": "mask"
            },
            "evaluation": {
                "acceptance": [
                    "Should work correctly",
                    "Should be helpful"
                ]
            },
            "ownership": {
                "owner": "test@example.com",
                "team": "Test Team"
            },
            "version": "1.0.0"
        }
    
    def test_render_agent(self, claude_adapter, sample_agent_spec):
        """Test rendering agent to markdown."""
        markdown = claude_adapter.render_agent(sample_agent_spec)
        
        # Check that required front-matter is present
        assert "name: test-agent" in markdown
        assert "description: A test agent for adapter testing" in markdown
        assert "model: sonnet" in markdown
        assert "tools: test_tool" in markdown
        
        # Check that role is included
        assert "You are a test agent." in markdown
        
        # Check that additional sections are present
        assert "Privacy Policy" in markdown
        assert "Available Tools" in markdown
        assert "Success Criteria" in markdown
        assert "Generated from test-agent.yaml v1.0.0" in markdown
    
    def test_generate_subagent_file(self, claude_adapter, sample_agent_spec):
        """Test generating subagent file from spec."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create spec file
            spec_path = Path(temp_dir) / "test-agent.yaml"
            with open(spec_path, 'w') as f:
                yaml.dump(sample_agent_spec, f)
            
            # Generate output
            output_dir = Path(temp_dir) / "output"
            output_file = claude_adapter.generate_subagent_file(spec_path, output_dir)
            
            # Check file was created
            assert output_file.exists()
            assert output_file.name == "test-agent.md"
            
            # Check content
            content = output_file.read_text()
            assert "name: test-agent" in content
            assert "You are a test agent." in content


class TestLangGraphAdapter:
    """Test LangGraph adapter."""
    
    @pytest.fixture
    def langgraph_adapter(self):
        """Create LangGraph adapter with templates."""
        templates_dir = Path(__file__).parent.parent / "templates"
        return LangGraphAdapter(templates_dir)
    
    @pytest.fixture
    def sample_agent_spec(self):
        """Sample agent specification for testing."""
        return {
            "id": "test-agent",
            "name": "Test Agent", 
            "summary": "A test agent for adapter testing",
            "role": "You are a test agent.",
            "model": {
                "provider": "anthropic",
                "family": "claude",
                "tier": "sonnet",
                "params": {
                    "temperature": 0.3
                }
            },
            "tools": [
                {
                    "id": "test_tool",
                    "type": "builtin",
                    "description": "A test tool"
                }
            ],
            "constraints": {
                "pii_policy": "mask",
                "max_tokens": 3000
            },
            "ownership": {
                "owner": "test@example.com",
                "team": "Test Team"
            },
            "version": "1.0.0"
        }
    
    def test_render_agent(self, langgraph_adapter, sample_agent_spec):
        """Test rendering agent to Python code."""
        python_code = langgraph_adapter.render_agent(sample_agent_spec)
        
        # Check class definition
        assert "class TestAgentAgent:" in python_code
        
        # Check imports
        assert "from langgraph.prebuilt import create_react_agent" in python_code
        assert "from langchain_anthropic import ChatAnthropic" in python_code
        
        # Check model initialization
        assert "ChatAnthropic" in python_code
        assert "temperature=0.3" in python_code
        
        # Check system prompt
        assert "You are a test agent." in python_code
        
        # Check factory function
        assert "def create_test_agent_agent():" in python_code
        
        # Check that code is syntactically valid Python
        compile(python_code, '<string>', 'exec')
    
    def test_generate_agent_file(self, langgraph_adapter, sample_agent_spec):
        """Test generating agent file from spec."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create spec file
            spec_path = Path(temp_dir) / "test-agent.yaml"
            with open(spec_path, 'w') as f:
                yaml.dump(sample_agent_spec, f)
            
            # Generate output
            output_dir = Path(temp_dir) / "output"
            output_file = langgraph_adapter.generate_agent_file(spec_path, output_dir)
            
            # Check file was created
            assert output_file.exists()
            assert output_file.name == "test_agent_agent.py"
            
            # Check content is valid Python
            content = output_file.read_text()
            compile(content, str(output_file), 'exec')
    
    def test_generate_requirements_file(self, langgraph_adapter):
        """Test generating requirements file."""
        specs = [
            {"model": {"provider": "anthropic"}},
            {"model": {"provider": "openai"}},
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            req_file = langgraph_adapter.generate_requirements_file(specs, output_dir)
            
            # Check file was created
            assert req_file.exists()
            assert req_file.name == "requirements.txt"
            
            # Check content
            content = req_file.read_text()
            assert "langgraph" in content
            assert "langchain-anthropic" in content
            assert "langchain-openai" in content
    
    def test_generate_app_file(self, langgraph_adapter, sample_agent_spec):
        """Test generating app file."""
        specs = [sample_agent_spec]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            app_file = langgraph_adapter.generate_app_file(specs, output_dir)
            
            # Check file was created
            assert app_file.exists()
            assert app_file.name == "app.py"
            
            # Check content
            content = app_file.read_text()
            assert "from test_agent_agent import create_test_agent_agent" in content
            assert "FastAPI" in content
            assert 'agents["test-agent"] = create_test_agent_agent()' in content
            
            # Check that code is syntactically valid Python
            compile(content, str(app_file), 'exec')