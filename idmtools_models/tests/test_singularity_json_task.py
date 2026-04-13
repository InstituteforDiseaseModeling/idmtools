"""
Test for generic SingularityJSONConfiguredTask
"""
import allure
import pytest
from idmtools.entities import CommandLine
from idmtools_models.singularity_json_task import SingularityJSONConfiguredTask


@pytest.mark.smoke
@allure.story("Entities")
@allure.story("SingularityJSONConfiguredTask")
@allure.suite("idmtools_models")
class TestSingularityJSONConfiguredTask:
    """Test SingularityJSONConfiguredTask functionality."""

    def test_basic_creation(self):
        """Test that we can create a basic SingularityJSONConfiguredTask."""
        task = SingularityJSONConfiguredTask()
        assert task is not None
        assert task.provided_command is not None
        assert isinstance(task.provided_command, CommandLine)

    def test_provided_command_override(self):
        """Test that we can override the provided command."""
        custom_command = CommandLine("singularity exec container.sif bash script.sh")
        task = SingularityJSONConfiguredTask(provided_command=custom_command)
        assert task.provided_command == custom_command

    def test_parameters(self):
        """Test that we can set parameters."""
        task = SingularityJSONConfiguredTask()
        task.parameters = {"param1": "value1", "param2": 42}
        assert task.parameters["param1"] == "value1"
        assert task.parameters["param2"] == 42

    def test_set_parameter(self):
        """Test the set_parameter method."""
        task = SingularityJSONConfiguredTask()
        task.set_parameter("key1", "value1")
        assert task.parameters["key1"] == "value1"

        task.set_parameter("key2", 123)
        assert task.parameters["key2"] == 123

    def test_config_file_name(self):
        """Test that config file name can be customized."""
        task = SingularityJSONConfiguredTask(config_file_name="custom_config.json")
        assert task.config_file_name == "custom_config.json"

    def test_set_param_partial(self):
        """Test the set_param_partial convenience method."""
        partial_func = SingularityJSONConfiguredTask.set_param_partial("beta")
        assert partial_func is not None
        # The partial function should be callable
        assert callable(partial_func)

    def test_envelope_parameter(self):
        """Test that envelope parameters work."""
        task = SingularityJSONConfiguredTask(
            envelope="config",
            parameters={"config": {"param1": "value1"}}
        )
        assert task.parameters["param1"] == "value1"
