"""
Statistics and health check API endpoints.
"""
from fastapi import APIRouter, HTTPException
from api.models import DatabaseStats
from api.database import DatabaseService

router = APIRouter(prefix="/api/stats", tags=["statistics"])
db_service = DatabaseService()


@router.get("/", response_model=DatabaseStats)
async def get_database_stats():
    """
    Get database statistics including counts of genes, proteins, PTMs, and domains.
    
    Returns:
        Database statistics with various counts.
    """
    try:
        stats = db_service.get_database_stats()
        return DatabaseStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching database stats: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify API and database connectivity.
    
    Returns:
        Basic health status.
    """
    try:
        # Test database connection
        stats = db_service.get_database_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "total_genes": stats.get("total_genes", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
