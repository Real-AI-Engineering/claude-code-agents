"""Claude Code adapter for generating subagent markdown files."""

import os
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import yaml


class ClaudeAdapter:
    """Adapter to generate Claude Code subagent markdown files from agent specs."""
    
    def __init__(self, templates_dir: Path):
        """Initialize the adapter with templates directory."""
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_agent(self, spec: Dict[str, Any]) -> str:
        """Render an agent specification to Claude subagent markdown."""
        template = self.env.get_template('claude_subagent.md.jinja')
        return template.render(spec=spec)
    
    def generate_subagent_file(self, spec_path: Path, output_dir: Path) -> Path:
        """Generate a Claude subagent markdown file from a YAML specification."""
        # Load the agent specification
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        # Render the markdown
        markdown_content = self.render_agent(spec)
        
        # Generate output filename
        agent_id = spec.get('id', spec_path.stem)
        output_file = output_dir / f"{agent_id}.md"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_file
    
    def install_to_claude_agents(self, output_file: Path) -> bool:
        """Install generated subagent to ~/.claude/agents directory."""
        claude_agents_dir = Path.home() / '.claude' / 'agents'
        
        try:
            # Create directory if it doesn't exist
            claude_agents_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file to Claude agents directory
            import shutil
            destination = claude_agents_dir / output_file.name
            shutil.copy2(output_file, destination)
            
            print(f"✅ Installed {output_file.name} to ~/.claude/agents/")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install to ~/.claude/agents/: {e}")
            return False


def generate_all_claude_agents(agents_dir: Path, templates_dir: Path, output_dir: Path, install: bool = False):
    """Generate Claude subagents for all YAML files in agents directory."""
    adapter = ClaudeAdapter(templates_dir)
    generated_files = []
    
    # Find all YAML files in agents directory
    for yaml_file in agents_dir.rglob('*.yaml'):
        # Skip template files
        if '_templates' in str(yaml_file):
            continue
            
        try:
            output_file = adapter.generate_subagent_file(yaml_file, output_dir)
            generated_files.append(output_file)
            print(f"✅ Generated {output_file.name} from {yaml_file.relative_to(agents_dir)}")
            
            # Install to Claude agents directory if requested
            if install:
                adapter.install_to_claude_agents(output_file)
                
        except Exception as e:
            print(f"❌ Failed to generate {yaml_file.name}: {e}")
    
    return generated_files