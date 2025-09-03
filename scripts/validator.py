"""Validation utilities for agent and recipe specifications."""

import json
from pathlib import Path
from typing import Tuple, List, Dict, Any
import yaml
from jsonschema import validate, ValidationError, Draft202012Validator


class AgentValidator:
    """Validates agent YAML files against the Agent Spec v1 schema."""
    
    def __init__(self, schema_path: Path):
        """Initialize validator with schema file."""
        self.schema_path = schema_path
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        # Create validator instance
        self.validator = Draft202012Validator(self.schema)
    
    def validate_file(self, yaml_path: Path) -> Tuple[bool, List[str]]:
        """Validate a YAML file against the agent schema.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            # Load YAML file
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate against schema
            errors = []
            for error in self.validator.iter_errors(data):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)
            
            return len(errors) == 0, errors
            
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {yaml_path}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """Format a JSON Schema validation error for display."""
        if error.absolute_path:
            path = ".".join(str(p) for p in error.absolute_path)
            return f"Field '{path}': {error.message}"
        else:
            return error.message
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data dictionary against schema."""
        try:
            errors = []
            for error in self.validator.iter_errors(data):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Validation error: {e}"]


class RecipeValidator:
    """Validates recipe YAML files against the Recipe Spec v1 schema."""
    
    def __init__(self, schema_path: Path):
        """Initialize validator with schema file."""
        self.schema_path = schema_path
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        # Create validator instance
        self.validator = Draft202012Validator(self.schema)
    
    def validate_file(self, yaml_path: Path) -> Tuple[bool, List[str]]:
        """Validate a YAML file against the recipe schema.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            # Load YAML file
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate against schema
            errors = []
            for error in self.validator.iter_errors(data):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)
            
            # Additional semantic validation
            semantic_errors = self._validate_recipe_semantics(data)
            errors.extend(semantic_errors)
            
            return len(errors) == 0, errors
            
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {yaml_path}"]
        except Exception as e:
            return False, [f"Validation error: {e}"]
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """Format a JSON Schema validation error for display."""
        if error.absolute_path:
            path = ".".join(str(p) for p in error.absolute_path)
            return f"Field '{path}': {error.message}"
        else:
            return error.message
    
    def _validate_recipe_semantics(self, data: Dict[str, Any]) -> List[str]:
        """Perform additional semantic validation for recipes."""
        errors = []
        
        graph = data.get('graph', [])
        
        # Check for duplicate stage names
        stage_names = [stage.get('stage') for stage in graph if 'stage' in stage]
        duplicate_stages = set([name for name in stage_names if stage_names.count(name) > 1])
        if duplicate_stages:
            errors.append(f"Duplicate stage names found: {', '.join(duplicate_stages)}")
        
        # Check that each stage has either parallel or sequence
        for i, stage in enumerate(graph):
            has_parallel = 'parallel' in stage
            has_sequence = 'sequence' in stage
            
            if not has_parallel and not has_sequence:
                stage_name = stage.get('stage', f'stage_{i}')
                errors.append(f"Stage '{stage_name}' must have either 'parallel' or 'sequence' field")
            
            if has_parallel and has_sequence:
                stage_name = stage.get('stage', f'stage_{i}')
                errors.append(f"Stage '{stage_name}' cannot have both 'parallel' and 'sequence' fields")
        
        return errors


def validate_all_files(agents_dir: Path, recipes_dir: Path, schemas_dir: Path) -> Dict[str, Any]:
    """Validate all agent and recipe files."""
    
    agent_validator = AgentValidator(schemas_dir / "agent-spec-v1.json")
    recipe_validator = RecipeValidator(schemas_dir / "recipe-spec-v1.json")
    
    results = {
        'agents': {'valid': [], 'invalid': []},
        'recipes': {'valid': [], 'invalid': []},
        'summary': {'total_files': 0, 'valid_files': 0, 'invalid_files': 0}
    }
    
    # Validate agents
    for yaml_file in agents_dir.rglob("*.yaml"):
        if "_templates" in str(yaml_file):
            continue
        
        results['summary']['total_files'] += 1
        is_valid, errors = agent_validator.validate_file(yaml_file)
        
        if is_valid:
            results['agents']['valid'].append(str(yaml_file))
            results['summary']['valid_files'] += 1
        else:
            results['agents']['invalid'].append({
                'file': str(yaml_file),
                'errors': errors
            })
            results['summary']['invalid_files'] += 1
    
    # Validate recipes
    for yaml_file in recipes_dir.rglob("*.yaml"):
        if "_templates" in str(yaml_file):
            continue
        
        results['summary']['total_files'] += 1
        is_valid, errors = recipe_validator.validate_file(yaml_file)
        
        if is_valid:
            results['recipes']['valid'].append(str(yaml_file))
            results['summary']['valid_files'] += 1
        else:
            results['recipes']['invalid'].append({
                'file': str(yaml_file),
                'errors': errors
            })
            results['summary']['invalid_files'] += 1
    
    return results