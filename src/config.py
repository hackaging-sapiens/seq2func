"""Configuration module for loading environment variables."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Nebius API Configuration
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1/")

# NCBI/PubMed Configuration
NCBI_EMAIL = os.getenv("NCBI_EMAIL")
NCBI_API_KEY = os.getenv("NCBI_API_KEY") 

# Validate required configurations
if not NEBIUS_API_KEY:
    raise ValueError("NEBIUS_API_KEY must be set in .env file")
if not NCBI_EMAIL:
    raise ValueError("NCBI_EMAIL must be set in .env file")
