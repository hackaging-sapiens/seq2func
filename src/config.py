"""Configuration module for loading environment variables."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Nebius API Configuration
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1/")
NEBIUS_MODEL = os.getenv("NEBIUS_MODEL", "meta-llama/Llama-3.3-70B-Instruct")

# NCBI/PubMed Configuration
NCBI_EMAIL = os.getenv("NCBI_EMAIL")
NCBI_API_KEY = os.getenv("NCBI_API_KEY")

# PostgreSQL Database Configuration
DB_HOST = os.getenv("DB_HOST", "95.217.221.48")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "djrpHA@5432")
DB_SCHEMA = os.getenv("DB_SCHEMA", "seq2fun")

# Validate required configurations
if not NEBIUS_API_KEY:
    raise ValueError("NEBIUS_API_KEY must be set in .env file")
if not NCBI_EMAIL:
    raise ValueError("NCBI_EMAIL must be set in .env file")
