"""Default test. Should always pass."""
import unittest


class DefaultTest(unittest.TestCase):
    """Default test class."""

    def test(self: "DefaultTest") -> None:
        """Default test."""
        assert True
