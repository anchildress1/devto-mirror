#!/usr/bin/env python3
"""
Unit tests for the validate_site_generation module.
Tests the site generation validation functionality.
"""

import os
import subprocess  # nosec - needed for testing subprocess functionality
import unittest
from unittest.mock import MagicMock, patch

# Import the function we need to test
from scripts.validate_site_generation import validate_site_generation


class TestValidateSiteGeneration(unittest.TestCase):
    """Test cases for site generation validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment to restore later
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def _setup_path_mocks(self, mock_path, mock_temp_dir):
        """Helper to set up common path mocking."""
        # Mock temporary directory
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/test_dir"  # nosec - test path

        # Mock Path operations
        mock_temp_path = MagicMock()
        mock_assets_dir = MagicMock()
        mock_temp_path.__truediv__.return_value = mock_assets_dir
        mock_path.return_value = mock_temp_path

        # Mock file existence checks
        mock_workspace_root = MagicMock()
        mock_script_dir = MagicMock()
        mock_script_dir.parent = mock_workspace_root
        mock_path.return_value.parent = mock_script_dir
        mock_workspace_root.__truediv__.return_value.exists.return_value = False

    @patch("builtins.print")
    @patch("scripts.validate_site_generation.load_dotenv")
    @patch("scripts.validate_site_generation.subprocess.run")
    @patch("scripts.validate_site_generation.shutil.copy2")
    @patch("scripts.validate_site_generation.tempfile.TemporaryDirectory")
    @patch("scripts.validate_site_generation.Path")
    def test_validate_site_generation_success(
        self, mock_path, mock_temp_dir, mock_copy, mock_subprocess, mock_load_dotenv, mock_print
    ):
        """Test successful site generation validation."""
        self._setup_path_mocks(mock_path, mock_temp_dir)

        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = validate_site_generation()

        self.assertTrue(result)

        # Check that validation passed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("validation passed" in call for call in print_calls))

    @patch("builtins.print")
    @patch("scripts.validate_site_generation.load_dotenv")
    @patch("scripts.validate_site_generation.subprocess.run")
    @patch("scripts.validate_site_generation.shutil.copy2")
    @patch("scripts.validate_site_generation.tempfile.TemporaryDirectory")
    @patch("scripts.validate_site_generation.Path")
    def test_validate_site_generation_failure(
        self, mock_path, mock_temp_dir, mock_copy, mock_subprocess, mock_load_dotenv, mock_print
    ):
        """Test failed site generation validation."""
        self._setup_path_mocks(mock_path, mock_temp_dir)

        # Mock failed subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Test stdout output"
        mock_result.stderr = "Test error output"
        mock_subprocess.return_value = mock_result

        result = validate_site_generation()

        self.assertFalse(result)

        # Check that failure was reported
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("validation failed" in call for call in print_calls))
        self.assertTrue(any("Test stdout output" in call for call in print_calls))
        self.assertTrue(any("Test error output" in call for call in print_calls))

    @patch("builtins.print")
    @patch("scripts.validate_site_generation.load_dotenv")
    @patch("scripts.validate_site_generation.subprocess.run")
    @patch("scripts.validate_site_generation.shutil.copy2")
    @patch("scripts.validate_site_generation.tempfile.TemporaryDirectory")
    @patch("scripts.validate_site_generation.Path")
    def test_validate_site_generation_timeout(
        self, mock_path, mock_temp_dir, mock_copy, mock_subprocess, mock_load_dotenv, mock_print
    ):
        """Test site generation validation timeout."""
        self._setup_path_mocks(mock_path, mock_temp_dir)

        # Mock timeout exception
        mock_subprocess.side_effect = subprocess.TimeoutExpired("python", 60)

        result = validate_site_generation()

        self.assertFalse(result)

        # Check that timeout was reported
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("timed out" in call for call in print_calls))

    @patch("builtins.print")
    @patch("scripts.validate_site_generation.load_dotenv")
    @patch("scripts.validate_site_generation.subprocess.run")
    @patch("scripts.validate_site_generation.shutil.copy2")
    @patch("scripts.validate_site_generation.tempfile.TemporaryDirectory")
    @patch("scripts.validate_site_generation.Path")
    def test_validate_site_generation_exception(
        self, mock_path, mock_temp_dir, mock_copy, mock_subprocess, mock_load_dotenv, mock_print
    ):
        """Test site generation validation with unexpected exception."""
        self._setup_path_mocks(mock_path, mock_temp_dir)

        # Mock unexpected exception
        mock_subprocess.side_effect = Exception("Unexpected error")

        result = validate_site_generation()

        self.assertFalse(result)

        # Check that error was reported
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Unexpected error" in call for call in print_calls))

    @patch("scripts.validate_site_generation.validate_site_generation")
    def test_main_function_success(self, mock_validate):
        """Test main function with successful validation."""
        mock_validate.return_value = True

        with patch("builtins.print") as mock_print:
            # Import and run main to avoid sys.exit in test
            from scripts.validate_site_generation import main

            try:
                main()
            except SystemExit as e:
                # Should not exit with error code
                self.fail(f"main() should not exit with error, got: {e}")

        # Check success message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("All site generation validations passed" in call for call in print_calls))

    @patch("scripts.validate_site_generation.validate_site_generation")
    @patch("sys.exit")
    def test_main_function_failure(self, mock_exit, mock_validate):
        """Test main function with failed validation."""
        mock_validate.return_value = False

        from scripts.validate_site_generation import main

        main()

        # Should exit with error code 1
        mock_exit.assert_called_once_with(1)

    @patch("builtins.print")
    @patch("scripts.validate_site_generation.load_dotenv")
    @patch("scripts.validate_site_generation.subprocess.run")
    @patch("scripts.validate_site_generation.shutil.copy2")
    @patch("scripts.validate_site_generation.tempfile.TemporaryDirectory")
    @patch("scripts.validate_site_generation.Path")
    def test_file_copying_logic(
        self, mock_path, mock_temp_dir, mock_copy, mock_subprocess, mock_load_dotenv, mock_print
    ):
        """Test that necessary files are copied to temp directory."""
        self._setup_path_mocks(mock_path, mock_temp_dir)

        # Mock file existence checks to return True for optional files
        mock_workspace_root = MagicMock()
        mock_script_dir = MagicMock()
        mock_script_dir.parent = mock_workspace_root
        mock_path.return_value.parent = mock_script_dir

        # Mock that optional files exist
        def mock_exists_side_effect():
            return True  # Simplify - just return True for all existence checks

        mock_workspace_root.__truediv__.return_value.exists.side_effect = mock_exists_side_effect

        # Mock successful subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        validate_site_generation()

        # Check that copy2 was called (files were copied)
        self.assertTrue(mock_copy.called)

        # Check that subprocess was called
        mock_subprocess.assert_called_once()

    @patch("builtins.print")
    @patch("scripts.validate_site_generation.load_dotenv")
    @patch("scripts.validate_site_generation.subprocess.run")
    @patch("scripts.validate_site_generation.shutil.copy2")
    @patch("scripts.validate_site_generation.tempfile.TemporaryDirectory")
    @patch("scripts.validate_site_generation.Path")
    def test_environment_variable_setup(
        self, mock_path, mock_temp_dir, mock_copy, mock_subprocess, mock_load_dotenv, mock_print
    ):
        """Test that environment variables are properly set for subprocess."""
        self._setup_path_mocks(mock_path, mock_temp_dir)

        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        # Mock environment variables to return test values
        with patch.dict(os.environ, {"DEVTO_USERNAME": "testuser", "PAGES_REPO": "testuser/devto-mirror"}, clear=False):
            validate_site_generation()

        # Check that subprocess was called with correct environment
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args

        # Check default validation values were passed
        env = call_args[1]["env"]
        self.assertEqual(env["DEVTO_USERNAME"], "testuser")
        self.assertEqual(env["PAGES_REPO"], "testuser/devto-mirror")
        self.assertEqual(env["VALIDATION_MODE"], "true")

        # Check other subprocess parameters
        self.assertEqual(call_args[1]["timeout"], 60)
        self.assertTrue(call_args[1]["capture_output"])
        self.assertTrue(call_args[1]["text"])


if __name__ == "__main__":
    unittest.main()
