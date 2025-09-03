"""LangGraph adapter for generating Python agent nodes from agent specs."""

import os
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import yaml


class LangGraphAdapter:
    """Adapter to generate LangGraph Python agent files from agent specs."""
    
    def __init__(self, templates_dir: Path):
        """Initialize the adapter with templates directory."""
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_agent(self, spec: Dict[str, Any]) -> str:
        """Render an agent specification to LangGraph Python code."""
        template = self.env.get_template('langgraph_agent.py.jinja')
        return template.render(spec=spec)
    
    def generate_agent_file(self, spec_path: Path, output_dir: Path) -> Path:
        """Generate a LangGraph Python agent file from a YAML specification."""
        # Load the agent specification
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        # Render the Python code
        python_content = self.render_agent(spec)
        
        # Generate output filename
        agent_id = spec.get('id', spec_path.stem)
        output_file = output_dir / f"{agent_id.replace('-', '_')}_agent.py"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        return output_file
    
    def generate_requirements_file(self, specs: list, output_dir: Path) -> Path:
        """Generate requirements.txt for LangGraph agents."""
        requirements = set([
            "langgraph>=0.0.60",
            "langchain>=0.1.0",
            "langchain-core>=0.1.0",
        ])
        
        # Add model-specific requirements based on specs
        for spec in specs:
            provider = spec.get('model', {}).get('provider', 'anthropic')
            if provider == 'anthropic':
                requirements.add("langchain-anthropic>=0.1.0")
            elif provider == 'openai':
                requirements.add("langchain-openai>=0.1.0")
        
        requirements_file = output_dir / "requirements.txt"
        
        with open(requirements_file, 'w', encoding='utf-8') as f:
            for req in sorted(requirements):
                f.write(f"{req}\n")
        
        return requirements_file
    
    def generate_app_file(self, specs: list, output_dir: Path) -> Path:
        """Generate a main app.py file to run all agents."""
        app_content = '''"""LangGraph Agents Application

Generated agent collection with FastAPI server.
"""

import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import all generated agents
'''
        
        # Add imports for each agent
        for spec in specs:
            agent_id = spec.get('id', 'unknown')
            class_name = agent_id.replace('-', '_')
            app_content += f"from {class_name}_agent import create_{class_name}_agent\n"
        
        app_content += '''

app = FastAPI(title="LangGraph Agents API", version="1.0.0")

# Agent registry
agents = {}

class AgentRequest(BaseModel):
    message: str
    agent_id: str
    metadata: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    success: bool
    response: str = None
    error: str = None
    agent_id: str
    metadata: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize all agents."""
    global agents
    
'''
        
        # Add agent initialization for each spec
        for spec in specs:
            agent_id = spec.get('id', 'unknown')
            class_name = agent_id.replace('-', '_')
            app_content += f'    agents["{agent_id}"] = create_{class_name}_agent()\n'
        
        app_content += '''
    print(f"Initialized {len(agents)} agents: {list(agents.keys())}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LangGraph Agents API",
        "agents": list(agents.keys()),
        "endpoints": ["/agents", "/agents/{agent_id}/invoke"]
    }

@app.get("/agents")
async def list_agents():
    """List all available agents."""
    return {
        "agents": [
            {
                "id": agent_id,
                "name": agent.name,
                "description": agent.description
            }
            for agent_id, agent in agents.items()
        ]
    }

@app.post("/agents/{agent_id}/invoke", response_model=AgentResponse)
async def invoke_agent(agent_id: str, request: AgentRequest):
    """Invoke a specific agent."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = agents[agent_id]
    result = await agent.ainvoke(request.message)
    
    return AgentResponse(
        success=result["success"],
        response=result.get("response"),
        error=result.get("error"),
        agent_id=agent_id,
        metadata=result.get("metadata", {})
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        app_file = output_dir / "app.py"
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        return app_file


def generate_all_langgraph_agents(agents_dir: Path, templates_dir: Path, output_dir: Path):
    """Generate LangGraph agents for all YAML files in agents directory."""
    adapter = LangGraphAdapter(templates_dir)
    generated_files = []
    specs = []
    
    # Find all YAML files in agents directory
    for yaml_file in agents_dir.rglob('*.yaml'):
        # Skip template files
        if '_templates' in str(yaml_file):
            continue
            
        try:
            # Load spec for requirements generation
            with open(yaml_file, 'r', encoding='utf-8') as f:
                spec = yaml.safe_load(f)
            specs.append(spec)
            
            # Generate agent file
            output_file = adapter.generate_agent_file(yaml_file, output_dir)
            generated_files.append(output_file)
            print(f"✅ Generated {output_file.name} from {yaml_file.relative_to(agents_dir)}")
            
        except Exception as e:
            print(f"❌ Failed to generate {yaml_file.name}: {e}")
    
    # Generate supporting files
    if specs:
        req_file = adapter.generate_requirements_file(specs, output_dir)
        app_file = adapter.generate_app_file(specs, output_dir)
        print(f"✅ Generated {req_file.name}")
        print(f"✅ Generated {app_file.name}")
    
    return generated_files