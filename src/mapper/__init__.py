"""
Module de configuration des positions pour Rank Tracker.
"""

from .gui import MappingGUI
from .capture import capture_window, get_window_list
from .config_writer import save_mapping, load_mapping, validate_mapping

__version__ = "1.0.0"

__all__ = [
    'MappingGUI',
    'capture_window',
    'get_window_list',
    'save_mapping',
    'load_mapping',
    'validate_mapping'
] 