"""
File name changed from main.py to db.py to avoid conflict with existing main.py files.
Main application entry point.

This file can run either:
1. The FastAPI web API server for frontend access
2. The protein data fetching script

Usage:
    # Run FastAPI server
    python main.py api
    # or
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

    # Run data fetching
    python main.py fetch
    # or 
    python fetch_protein_gene_info.py
"""

import sys
import subprocess
from pathlib import Path


def run_api_server():
    """Run the FastAPI server."""
    print("Starting Sequence to Function API server...")
    print("API documentation will be available at: http://localhost:8000/docs")
    print("ReDoc documentation at: http://localhost:8000/redoc")
    
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("Error: uvicorn not found. Install with: pip install uvicorn[standard]")
        sys.exit(1)


def run_data_fetching():
    """Run the protein data fetching script."""
    print("Starting protein data fetching...")
    try:
        # Import and run the fetching script
        from fetch_protein_gene_info import main as fetch_main
        fetch_main()
    except ImportError as e:
        print(f"Error importing fetch script: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable commands:")
        print("  api    - Start FastAPI server")
        print("  fetch  - Run protein data fetching")
        return
    
    command = sys.argv[1].lower()
    
    if command == "api":
        run_api_server()
    elif command == "fetch":
        run_data_fetching()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: api, fetch")
        sys.exit(1)


if __name__ == "__main__":
    main()
