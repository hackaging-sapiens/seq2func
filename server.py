from fastapi import FastAPI, Query, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
import threading
from src.workflows.gene_search import GeneLiteratureSearch
from src.tasks.task_manager import TaskManager

# Create FastAPI app with metadata for automatic documentation
app = FastAPI(
    title="seq2func API",
    description="Knowledge base extraction pipeline for protein modifications linked to longevity",
    version="0.1.0"
)

# Add middleware to handle OPTIONS requests before route matching
@app.middleware("http")
async def options_handler(request: Request, call_next):
    """Handle OPTIONS requests for CORS preflight before route validation."""
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    return await call_next(request)

# Configure CORS to allow frontend access
# In production, replace with your actual frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local Next.js development server
        "http://127.0.0.1:3000",  # Alternative localhost
        # Add your production frontend URL here when deploying
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Initialize the gene literature search workflow and task manager
workflow = GeneLiteratureSearch()
task_manager = TaskManager()


# Pydantic models for response structure
class PaperResult(BaseModel):
    """Individual paper result from the literature search."""
    gene_id: Optional[int] = Field(None, description="NCBI Gene ID (Entrez ID)")
    gene_symbol: str = Field(..., description="Gene symbol (e.g., 'NRF2', 'SOX2')")
    pmid: str = Field(..., description="PubMed ID")
    title: str = Field(..., description="Paper title")
    year: str = Field(..., description="Publication year")
    journal: str = Field(..., description="Journal name")
    score: float = Field(..., description="Relevance score (0.0-1.0)")
    relevant: bool = Field(..., description="Whether paper meets relevance threshold")
    reasoning: str = Field(..., description="LLM reasoning for relevance score")
    search_date: str = Field(..., description="Date the search was performed")


class SearchResponse(BaseModel):
    """Response from the /agent endpoint."""
    results: List[PaperResult] = Field(..., description="Top-ranked papers")
    count: int = Field(..., description="Number of results returned")


# Pydantic models for async task system
class GeneSearchRequest(BaseModel):
    """Request to start a gene search task."""
    gene_symbol: str = Field(..., description="Gene symbol (e.g., 'NRF2', 'SOX2')")
    gene_id: Optional[int] = Field(None, description="NCBI Gene ID (Entrez ID)")
    max_results: int = Field(200, description="Maximum number of papers to retrieve", ge=1, le=1000)
    top_n: int = Field(20, description="Number of top-ranked papers to return", ge=1, le=100)
    include_reprogramming: bool = Field(False, description="Include reprogramming terms in search")


class TaskStartResponse(BaseModel):
    """Response when starting a task."""
    task_id: str = Field(..., description="Unique task ID")
    status: str = Field(..., description="Task status (pending)")


class ProgressInfo(BaseModel):
    """Progress information for a running task."""
    current_step: str
    step_number: int
    total_steps: int
    papers_screened: Optional[int] = None
    total_papers: Optional[int] = None
    message: str = ""


class TaskStatusResponse(BaseModel):
    """Response for task status query."""
    task_id: str
    status: str
    progress: Optional[ProgressInfo] = None
    result: Optional[SearchResponse] = None
    error: Optional[str] = None


# Helper function to run gene search in background
def run_gene_search_task(
    task_id: str,
    gene_symbol: str,
    gene_id: Optional[int],
    max_results: int,
    top_n: int,
    include_reprogramming: bool
):
    """Run gene search in background thread and update task status."""
    try:
        # Get the cancellation token and progress callback for this task
        task_info = task_manager.get_task(task_id)
        if not task_info:
            return

        # Get cancellation token and create progress callback
        cancellation_token = task_manager.cancellation_tokens.get(task_id)
        from src.tasks.task_manager import ProgressCallback
        progress_callback = ProgressCallback(task_id, task_manager)

        # Run the search
        results = workflow.search_gene(
            gene_symbol=gene_symbol,
            gene_id=gene_id,
            max_results=max_results,
            top_n=top_n,
            include_reprogramming=include_reprogramming,
            progress_callback=progress_callback,
            cancellation_token=cancellation_token
        )

        # Check if cancelled
        if cancellation_token and cancellation_token.is_cancelled():
            task_manager.update_status(task_id, "cancelled")
        else:
            # Set result
            task_manager.set_result(task_id, {
                "results": results,
                "count": len(results)
            })

    except Exception as e:
        # Set error
        task_manager.set_error(task_id, str(e))


@app.get("/", tags=["Root"])
def root():
    """
    API root endpoint with basic information.

    Returns API metadata and links to documentation.
    """
    return {
        "message": "seq2func API - Protein modification knowledge base extraction",
        "version": "0.1.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        },
        "endpoints": {
            "/agent/start": "Start async gene literature search (POST)",
            "/agent/status/{task_id}": "Check task status (GET)",
            "/agent/cancel/{task_id}": "Cancel running task (POST)",
            "/agent": "Synchronous gene search (deprecated, use /agent/start)"
        }
    }


@app.post("/agent/start", response_model=TaskStartResponse, tags=["Gene Search (Async)"])
def start_gene_search(request: GeneSearchRequest):
    """
    Start an asynchronous gene literature search task.

    This endpoint starts a background task that:
    1. Builds a PubMed search query for the specified gene
    2. Searches PubMed for relevant papers
    3. Screens papers using LLM for sequence→function→aging links
    4. Returns top N papers ranked by relevance score

    Returns immediately with a task_id that can be used to:
    - Poll for progress at GET /agent/status/{task_id}
    - Cancel the task at POST /agent/cancel/{task_id}
    """
    # Create task
    task_id, cancellation_token, progress_callback = task_manager.create_task()

    # Start background thread
    thread = threading.Thread(
        target=run_gene_search_task,
        args=(
            task_id,
            request.gene_symbol,
            request.gene_id,
            request.max_results,
            request.top_n,
            request.include_reprogramming
        ),
        daemon=True
    )
    thread.start()

    return TaskStartResponse(task_id=task_id, status="pending")


@app.get("/agent/status/{task_id}", response_model=TaskStatusResponse, tags=["Gene Search (Async)"])
def get_task_status(task_id: str):
    """
    Get the status of a gene search task.

    Returns the current status, progress information, and results (if complete).

    Status values:
    - pending: Task created but not yet started
    - running: Task is currently executing
    - completed: Task finished successfully (result available)
    - cancelled: Task was cancelled by user
    - failed: Task encountered an error
    """
    task_info = task_manager.get_task(task_id)

    if not task_info:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Convert to response model
    response = TaskStatusResponse(
        task_id=task_info.task_id,
        status=task_info.status,
        progress=ProgressInfo(**task_info.progress.__dict__) if task_info.progress else None,
        result=SearchResponse(**task_info.result) if task_info.result else None,
        error=task_info.error
    )

    return response


@app.post("/agent/cancel/{task_id}", tags=["Gene Search (Async)"])
def cancel_task(task_id: str):
    """
    Cancel a running gene search task.

    The task will stop gracefully at the next checkpoint (typically after
    the current paper finishes screening).

    Returns the updated task status.
    """
    success = task_manager.cancel_task(task_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {"task_id": task_id, "status": "cancelling"}


@app.get("/agent", response_model=SearchResponse, tags=["Gene Search (Deprecated)"], deprecated=True)
def agent(
    gene_symbol: str = Query(
        ...,
        description="Gene symbol (e.g., 'NRF2', 'SOX2')",
        example="NRF2"
    ),
    gene_id: Optional[int] = Query(
        None,
        description="NCBI Gene ID (Entrez ID) for unique identification",
        example=4780
    ),
    max_results: int = Query(
        200,
        description="Maximum number of papers to retrieve from PubMed",
        ge=1,
        le=1000
    ),
    top_n: int = Query(
        20,
        description="Number of top-ranked papers to return",
        ge=1,
        le=100
    ),
    include_reprogramming: bool = Query(
        False,
        description="Whether to include reprogramming terms in search query"
    )
):
    """
    Search and screen gene literature from PubMed.

    This endpoint:
    1. Builds a PubMed search query for the specified gene
    2. Searches PubMed for relevant papers
    3. Screens papers using LLM for sequence→function→aging links
    4. Returns top N papers ranked by relevance score

    The screening uses Llama 3.3 70B to analyze papers for:
    - Sequence changes (mutations, modifications, domains)
    - Functional changes (activity, binding, localization)
    - Aging phenotypes (lifespan, healthspan, age-related markers)

    Papers with score ≥ 0.5 are considered relevant.
    """
    try:
        # Call the search_gene function
        top_results = workflow.search_gene(
            gene_symbol=gene_symbol,
            gene_id=gene_id,
            max_results=max_results,
            top_n=top_n,
            include_reprogramming=include_reprogramming
        )

        # Return results (FastAPI automatically converts to JSON)
        return SearchResponse(
            results=top_results,
            count=len(top_results)
        )

    except Exception as e:
        # Handle any errors during execution
        raise HTTPException(status_code=500, detail=str(e))
