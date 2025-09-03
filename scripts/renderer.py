"""Agent renderer for generating artifacts from specifications."""

from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import yaml


class AgentRenderer:
    """Renders agent specifications to various target formats using Jinja2 templates."""
    
    def __init__(self, templates_dir: Path):
        """Initialize renderer with templates directory."""
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def load_agent_spec(self, spec_path: Path) -> Dict[str, Any]:
        """Load agent specification from YAML file."""
        with open(spec_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def render_claude_agent(self, spec_path: Path, output_dir: Path) -> Path:
        """Render agent spec to Claude Code subagent markdown."""
        spec = self.load_agent_spec(spec_path)
        
        template = self.env.get_template('claude_subagent.md.jinja')
        content = template.render(spec=spec)
        
        # Generate output file
        agent_id = spec.get('id', spec_path.stem)
        output_file = output_dir / f"{agent_id}.md"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def render_langgraph_agent(self, spec_path: Path, output_dir: Path) -> Path:
        """Render agent spec to LangGraph Python agent."""
        spec = self.load_agent_spec(spec_path)
        
        template = self.env.get_template('langgraph_agent.py.jinja')
        content = template.render(spec=spec)
        
        # Generate output file
        agent_id = spec.get('id', spec_path.stem)
        output_file = output_dir / f"{agent_id.replace('-', '_')}_agent.py"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def render_assistant_config(self, spec_path: Path, output_dir: Path) -> Path:
        """Render agent spec to OpenAI/CrewAI assistant configuration."""
        spec = self.load_agent_spec(spec_path)
        
        # Basic JSON configuration for OpenAI assistants
        config = {
            "name": spec.get('name'),
            "description": spec.get('summary'),
            "instructions": spec.get('role'),
            "model": self._map_model_to_openai(spec.get('model', {})),
            "tools": self._map_tools_to_openai(spec.get('tools', [])),
            "metadata": {
                "agent_id": spec.get('id'),
                "version": spec.get('version'),
                "owner": spec.get('ownership', {}).get('owner')
            }
        }
        
        # Generate output file
        agent_id = spec.get('id', spec_path.stem)
        output_file = output_dir / f"{agent_id}_assistant.json"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write file
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def _map_model_to_openai(self, model_config: Dict[str, Any]) -> str:
        """Map agent model config to OpenAI model name."""
        provider = model_config.get('provider', 'openai')
        tier = model_config.get('tier', 'gpt-4')
        
        if provider == 'openai':
            tier_mapping = {
                'gpt-3.5': 'gpt-3.5-turbo',
                'gpt-4': 'gpt-4',
                'gpt-4o': 'gpt-4o'
            }
            return tier_mapping.get(tier, 'gpt-4')
        else:
            # For non-OpenAI models, default to GPT-4
            return 'gpt-4'
    
    def _map_tools_to_openai(self, tools: list) -> list:
        """Map agent tools to OpenAI tools format."""
        openai_tools = []
        
        for tool in tools:
            tool_type = tool.get('type')
            
            if tool_type == 'builtin':
                # Map to OpenAI built-in tools
                tool_id = tool.get('id')
                if tool_id in ['code_interpreter', 'file_search']:
                    openai_tools.append({"type": tool_id})
            elif tool_type == 'http':
                # Custom function tool
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.get('id'),
                        "description": tool.get('description', ''),
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                })
        
        return openai_tools