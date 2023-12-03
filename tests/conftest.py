"""Pytest configuration file for the tests directory.

This configuration file is used by pytest for setting up global fixtures and configurations
that are applicable across multiple test modules in the test suite.

The primary use in this project is to mock certain modules that are not relevant or available
in the testing environment. This ensures that tests do not fail due to these external dependencies
and can run in isolated conditions.

Example usage:

import sys
from unittest.mock import MagicMock

# Mock the databricks.sdk module
sys.modules["databricks"] = MagicMock()
sys.modules["databricks.sdk"] = MagicMock()
sys.modules["databricks.sdk.runtime"] = MagicMock()
sys.modules["databricks.sdk.runtime.dbutils"] = MagicMock()
"""
