"""Tests for agent and recipe validation."""

import pytest
from pathlib import Path
import tempfile
import yaml

from scripts.validator import AgentValidator, RecipeValidator


class TestAgentValidator:
    """Test agent specification validation."""
    
    @pytest.fixture
    def agent_validator(self):
        """Create agent validator with schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "agent-spec-v1.json"
        return AgentValidator(schema_path)
    
    @pytest.fixture
    def valid_agent_data(self):
        """Valid agent data for testing."""
        return {
            "id": "test-agent",
            "name": "Test Agent",
            "summary": "A test agent for validation testing purposes",
            "role": "You are a test agent designed to validate the agent specification schema.",
            "model": {
                "provider": "anthropic",
                "family": "claude", 
                "tier": "sonnet"
            },
            "ownership": {
                "owner": "test@example.com"
            },
            "version": "1.0.0"
        }
    
    def test_validate_valid_agent(self, agent_validator, valid_agent_data):
        """Test validation of valid agent data."""
        is_valid, errors = agent_validator.validate_data(valid_agent_data)
        assert is_valid, f"Valid agent should pass validation. Errors: {errors}"
    
    def test_validate_missing_required_fields(self, agent_validator):
        """Test validation fails for missing required fields."""
        invalid_data = {
            "name": "Test Agent"
            # Missing required fields
        }
        
        is_valid, errors = agent_validator.validate_data(invalid_data)
        assert not is_valid
        assert len(errors) > 0
        assert any("required" in error.lower() for error in errors)
    
    def test_validate_invalid_id_format(self, agent_validator, valid_agent_data):
        """Test validation fails for invalid ID format."""
        valid_agent_data["id"] = "Invalid_ID_Format!"
        
        is_valid, errors = agent_validator.validate_data(valid_agent_data)
        assert not is_valid
        assert any("pattern" in error.lower() for error in errors)
    
    def test_validate_invalid_model_provider(self, agent_validator, valid_agent_data):
        """Test validation fails for invalid model provider."""
        valid_agent_data["model"]["provider"] = "invalid_provider"
        
        is_valid, errors = agent_validator.validate_data(valid_agent_data)
        assert not is_valid
    
    def test_validate_yaml_file(self, agent_validator, valid_agent_data):
        """Test validation of YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_agent_data, f)
            temp_path = Path(f.name)
        
        try:
            is_valid, errors = agent_validator.validate_file(temp_path)
            assert is_valid, f"Valid YAML file should pass validation. Errors: {errors}"
        finally:
            temp_path.unlink()
    
    def test_validate_invalid_yaml(self, agent_validator):
        """Test validation fails for invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            temp_path = Path(f.name)
        
        try:
            is_valid, errors = agent_validator.validate_file(temp_path)
            assert not is_valid
            assert any("yaml" in error.lower() for error in errors)
        finally:
            temp_path.unlink()


class TestRecipeValidator:
    """Test recipe specification validation."""
    
    @pytest.fixture
    def recipe_validator(self):
        """Create recipe validator with schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "recipe-spec-v1.json"
        return RecipeValidator(schema_path)
    
    @pytest.fixture
    def valid_recipe_data(self):
        """Valid recipe data for testing."""
        return {
            "id": "test-recipe",
            "name": "Test Recipe",
            "summary": "A test recipe for validation testing purposes",
            "graph": [
                {
                    "stage": "test_stage",
                    "sequence": [
                        {
                            "agent": "test-agent"
                        }
                    ]
                }
            ],
            "version": "1.0.0"
        }
    
    def test_validate_valid_recipe(self, recipe_validator, valid_recipe_data):
        """Test validation of valid recipe data."""
        is_valid, errors = recipe_validator.validate_data(valid_recipe_data)
        assert is_valid, f"Valid recipe should pass validation. Errors: {errors}"
    
    def test_validate_missing_graph(self, recipe_validator):
        """Test validation fails for missing graph."""
        invalid_data = {
            "id": "test-recipe",
            "name": "Test Recipe",
            "summary": "Test",
            "version": "1.0.0"
            # Missing graph
        }
        
        is_valid, errors = recipe_validator.validate_data(invalid_data)
        assert not is_valid
        assert any("graph" in error.lower() for error in errors)
    
    def test_validate_stage_without_parallel_or_sequence(self, recipe_validator, valid_recipe_data):
        """Test validation fails for stage without parallel or sequence."""
        valid_recipe_data["graph"] = [
            {
                "stage": "invalid_stage"
                # Missing parallel or sequence
            }
        ]
        
        # This should be caught by semantic validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_recipe_data, f)
            temp_path = Path(f.name)
        
        try:
            is_valid, errors = recipe_validator.validate_file(temp_path)
            assert not is_valid
            assert any("parallel" in error or "sequence" in error for error in errors)
        finally:
            temp_path.unlink()
    
    def test_validate_duplicate_stage_names(self, recipe_validator, valid_recipe_data):
        """Test validation fails for duplicate stage names."""
        valid_recipe_data["graph"] = [
            {
                "stage": "duplicate_stage",
                "sequence": [{"agent": "agent1"}]
            },
            {
                "stage": "duplicate_stage", 
                "sequence": [{"agent": "agent2"}]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_recipe_data, f)
            temp_path = Path(f.name)
        
        try:
            is_valid, errors = recipe_validator.validate_file(temp_path)
            assert not is_valid
            assert any("duplicate" in error.lower() for error in errors)
        finally:
            temp_path.unlink()


class TestValidationIntegration:
    """Integration tests for validation."""
    
    def test_validate_existing_agents(self):
        """Test that existing agent files are valid."""
        agents_dir = Path(__file__).parent.parent / "agents"
        schema_path = Path(__file__).parent.parent / "schemas" / "agent-spec-v1.json"
        
        if not agents_dir.exists() or not schema_path.exists():
            pytest.skip("Agent files or schema not found")
        
        validator = AgentValidator(schema_path)
        
        for yaml_file in agents_dir.rglob("*.yaml"):
            if "_templates" in str(yaml_file):
                continue
                
            is_valid, errors = validator.validate_file(yaml_file)
            assert is_valid, f"Agent {yaml_file.name} should be valid. Errors: {errors}"
    
    def test_validate_existing_recipes(self):
        """Test that existing recipe files are valid."""
        recipes_dir = Path(__file__).parent.parent / "recipes"
        schema_path = Path(__file__).parent.parent / "schemas" / "recipe-spec-v1.json"
        
        if not recipes_dir.exists() or not schema_path.exists():
            pytest.skip("Recipe files or schema not found")
        
        validator = RecipeValidator(schema_path)
        
        for yaml_file in recipes_dir.rglob("*.yaml"):
            if "_templates" in str(yaml_file):
                continue
                
            is_valid, errors = validator.validate_file(yaml_file)
            assert is_valid, f"Recipe {yaml_file.name} should be valid. Errors: {errors}"