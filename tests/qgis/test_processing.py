#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash

    # for whole tests
    python -m unittest tests.qgis.test_plg_processing
    # for specific test
    python -m unittest tests.qgis.test_plg_processing.TestPlgprocessing.test_plg_processing_structure
"""

# PyQGIS
from qgis.core import QgsApplication
from qgis.testing import start_app, unittest

from qchat.processing.provider import (
    QChatProvider,
)

provider = None


class TestProcessing(unittest.TestCase):
    """Tests for processing algorithms."""

    def setUp(self) -> None:
        """Set up the processing tests."""
        if not QgsApplication.processingRegistry().providers():
            self.provider = QChatProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)
        self.maxDiff = None

        # Start App needed to run processing on unittest
        start_app()

    def test_processing_provider(self):
        """Sample test."""
        print(f"Processing provider name : {self.provider.name()}")
