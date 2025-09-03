"""
CLI for the Claude Agents Repository System
"""

import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.validator import AgentValidator, RecipeValidator
from scripts.renderer import AgentRenderer
from adapters.claude import generate_all_claude_agents
from adapters.langgraph import generate_all_langgraph_agents

app = typer.Typer(name="agents", help="Multi-runtime agent template system")
console = Console()

# Default paths
AGENTS_DIR = project_root / "agents"
RECIPES_DIR = project_root / "recipes"
SCHEMAS_DIR = project_root / "schemas"
TEMPLATES_DIR = project_root / "templates"
ADAPTERS_DIR = project_root / "adapters"


@app.command()
def validate(
    path: Optional[Path] = typer.Argument(None, help="Path to YAML file or directory to validate"),
    agent_schema: Path = typer.Option(SCHEMAS_DIR / "agent-spec-v1.json", help="Agent schema file"),
    recipe_schema: Path = typer.Option(SCHEMAS_DIR / "recipe-spec-v1.json", help="Recipe schema file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Validate agent and recipe YAML files against their schemas."""
    
    if path is None:
        # Validate all files
        paths_to_validate = [AGENTS_DIR, RECIPES_DIR]
    else:
        paths_to_validate = [path]
    
    agent_validator = AgentValidator(agent_schema)
    recipe_validator = RecipeValidator(recipe_schema)
    
    total_files = 0
    valid_files = 0
    errors = []
    
    for validate_path in paths_to_validate:
        if not validate_path.exists():
            console.print(f"[red]Path does not exist: {validate_path}[/red]")
            continue
        
        # Find YAML files
        if validate_path.is_file():
            yaml_files = [validate_path]
        else:
            yaml_files = list(validate_path.rglob("*.yaml")) + list(validate_path.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            # Skip template files
            if "_templates" in str(yaml_file):
                continue
            
            total_files += 1
            
            # Determine validator based on directory structure
            if "agents" in str(yaml_file):
                validator = agent_validator
                file_type = "agent"
            elif "recipes" in str(yaml_file):
                validator = recipe_validator  
                file_type = "recipe"
            else:
                # Try to determine from content
                try:
                    import yaml
                    with open(yaml_file, 'r') as f:
                        content = yaml.safe_load(f)
                    
                    if 'graph' in content:
                        validator = recipe_validator
                        file_type = "recipe"
                    else:
                        validator = agent_validator
                        file_type = "agent"
                except:
                    console.print(f"[yellow]Could not determine type for {yaml_file}, skipping[/yellow]")
                    continue
            
            # Validate file
            is_valid, validation_errors = validator.validate_file(yaml_file)
            
            if is_valid:
                valid_files += 1
                if verbose:
                    console.print(f"[green]✅ {yaml_file.name} ({file_type})[/green]")
            else:
                errors.extend([(yaml_file, file_type, err) for err in validation_errors])
                console.print(f"[red]❌ {yaml_file.name} ({file_type})[/red]")
                if verbose:
                    for error in validation_errors:
                        console.print(f"   [red]• {error}[/red]")
    
    # Summary
    console.print(f"\n[bold]Validation Summary[/bold]")
    console.print(f"Total files: {total_files}")
    console.print(f"Valid files: [green]{valid_files}[/green]")
    console.print(f"Invalid files: [red]{total_files - valid_files}[/red]")
    
    if errors and not verbose:
        console.print(f"\n[bold red]Errors found:[/bold red]")
        for file_path, file_type, error in errors:
            console.print(f"[red]❌ {file_path.name} ({file_type}): {error}[/red]")
    
    # Exit with error code if validation failed
    if total_files - valid_files > 0:
        raise typer.Exit(code=1)


@app.command()
def render(
    target: str = typer.Argument(..., help="Target adapter (claude, langgraph, assistants)"),
    agent_id: Optional[str] = typer.Option(None, help="Specific agent ID to render"),
    output_dir: Optional[Path] = typer.Option(None, help="Output directory"),
    install: bool = typer.Option(False, help="Install to local runtime (Claude only)")
):
    """Render agent specifications to target runtime artifacts."""
    
    if output_dir is None:
        output_dir = ADAPTERS_DIR / target
    
    renderer = AgentRenderer(TEMPLATES_DIR)
    
    if target == "claude":
        if agent_id:
            # Render specific agent
            agent_file = None
            for yaml_file in AGENTS_DIR.rglob("*.yaml"):
                if yaml_file.stem == agent_id:
                    agent_file = yaml_file
                    break
            
            if not agent_file:
                console.print(f"[red]Agent '{agent_id}' not found[/red]")
                raise typer.Exit(code=1)
            
            output_file = renderer.render_claude_agent(agent_file, output_dir)
            console.print(f"[green]✅ Generated {output_file.name}[/green]")
            
            if install:
                from adapters.claude import ClaudeAdapter
                adapter = ClaudeAdapter(TEMPLATES_DIR)
                adapter.install_to_claude_agents(output_file)
        else:
            # Render all agents
            generated_files = generate_all_claude_agents(AGENTS_DIR, TEMPLATES_DIR, output_dir, install)
            console.print(f"[green]✅ Generated {len(generated_files)} Claude subagents[/green]")
    
    elif target == "langgraph":
        generated_files = generate_all_langgraph_agents(AGENTS_DIR, TEMPLATES_DIR, output_dir)
        console.print(f"[green]✅ Generated {len(generated_files)} LangGraph agents[/green]")
        
        # Print usage instructions
        console.print(f"\n[bold]Usage Instructions:[/bold]")
        console.print(f"1. Install dependencies: pip install -r {output_dir}/requirements.txt")
        console.print(f"2. Run the API server: python {output_dir}/app.py")
        console.print(f"3. Open http://localhost:8000/docs for API documentation")
    
    elif target == "assistants":
        console.print("[yellow]OpenAI/CrewAI adapter not yet implemented[/yellow]")
        raise typer.Exit(code=1)
    
    else:
        console.print(f"[red]Unknown target: {target}[/red]")
        console.print("Available targets: claude, langgraph, assistants")
        raise typer.Exit(code=1)


@app.command()
def list_agents(
    domain: Optional[str] = typer.Option(None, help="Filter by domain (engineering, data, ops, product)"),
    tag: Optional[str] = typer.Option(None, help="Filter by tag")
):
    """List all available agents."""
    
    import yaml
    
    agents = []
    
    for yaml_file in AGENTS_DIR.rglob("*.yaml"):
        if "_templates" in str(yaml_file):
            continue
            
        try:
            with open(yaml_file, 'r') as f:
                spec = yaml.safe_load(f)
            
            # Apply filters
            if domain:
                file_domain = yaml_file.parent.name
                if file_domain != domain:
                    continue
            
            if tag:
                agent_tags = spec.get('tags', [])
                if tag not in agent_tags:
                    continue
            
            agents.append({
                'id': spec.get('id', yaml_file.stem),
                'name': spec.get('name', 'Unknown'),
                'domain': yaml_file.parent.name,
                'summary': spec.get('summary', '')[:80] + '...' if len(spec.get('summary', '')) > 80 else spec.get('summary', ''),
                'version': spec.get('version', '0.0.0'),
                'tags': spec.get('tags', [])
            })
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {yaml_file.name}: {e}[/yellow]")
    
    if not agents:
        console.print("[yellow]No agents found matching criteria[/yellow]")
        return
    
    # Create table
    table = Table(title=f"Available Agents ({len(agents)} found)")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Domain", style="green")
    table.add_column("Summary", style="white")
    table.add_column("Version", style="yellow")
    table.add_column("Tags", style="blue")
    
    for agent in sorted(agents, key=lambda x: (x['domain'], x['id'])):
        table.add_row(
            agent['id'],
            agent['name'],
            agent['domain'],
            agent['summary'],
            agent['version'],
            ', '.join(agent['tags'][:3]) + ('...' if len(agent['tags']) > 3 else '')
        )
    
    console.print(table)


@app.command()
def init_agent(
    agent_id: str = typer.Argument(..., help="Agent ID (kebab-case)"),
    domain: str = typer.Option("custom", help="Domain (engineering, data, ops, product, custom)"),
    name: Optional[str] = typer.Option(None, help="Agent name"),
    owner: str = typer.Option("team@company.com", help="Owner email")
):
    """Initialize a new agent from template."""
    
    if not name:
        name = agent_id.replace('-', ' ').title()
    
    # Ensure domain directory exists
    domain_dir = AGENTS_DIR / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    # Create agent file
    agent_file = domain_dir / f"{agent_id}.yaml"
    
    if agent_file.exists():
        console.print(f"[red]Agent {agent_id} already exists at {agent_file}[/red]")
        raise typer.Exit(code=1)
    
    # Load template
    template_file = AGENTS_DIR / "_templates" / "agent-template.yaml"
    
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Replace placeholders
    agent_content = template_content.replace("my-agent-id", agent_id)
    agent_content = agent_content.replace("My Agent Name", name)
    agent_content = agent_content.replace("team@company.com", owner)
    
    # Write agent file
    with open(agent_file, 'w') as f:
        f.write(agent_content)
    
    console.print(f"[green]✅ Created agent {agent_id} at {agent_file}[/green]")
    console.print(f"[yellow]📝 Please edit {agent_file} to customize the agent[/yellow]")


if __name__ == "__main__":
    app()