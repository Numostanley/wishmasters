"""
Initialize settings environment.
"""

import os
from .base import ENVIRONMENT


def get_settings_environment():
    # detect environment to load settings configuration
    if ENVIRONMENT == 'prod':
        ENV_SETTINGS = 'core.settings.prod'
    else:
        ENV_SETTINGS = 'core.settings.dev'
    return ENV_SETTINGS

