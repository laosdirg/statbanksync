"""
Configuration

pulls from environment variables (set in docker-compose.yml)
"""

import os

#DB_URL = "postgresql://postgres:@localhost:5432/postgres"
DB_URL = os.environ['DB_URL']
