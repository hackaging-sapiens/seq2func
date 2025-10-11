"""PubMed search tool for retrieving PMIDs based on query."""
from typing import List
from langchain.tools import Tool
from Bio import Entrez
from src.config import NCBI_EMAIL, NCBI_API_KEY


# Configure Entrez
Entrez.email = NCBI_EMAIL
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY


def search_pubmed(query: str, max_results: int = 100) -> List[str]:
    """
    Search PubMed for papers matching the query.

    Args:
        query: Search query (e.g., "IGF1R aging")
        max_results: Maximum number of PMIDs to return

    Returns:
        List of PMIDs as strings
    """
    try:
        # Exclude reviews and include only free full-text articles
        search_query = f"({query}) NOT Review[Publication Type] AND free full text[Filter]"

        handle = Entrez.esearch(
            db="pubmed",
            term=search_query,
            retmax=max_results,
            sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()

        pmids = record.get("IdList", [])
        return pmids
    except Exception as e:
        return [f"Error searching PubMed: {str(e)}"]


def create_pubmed_search_tool() -> Tool:
    """Create a LangChain tool for PubMed search."""
    return Tool(
        name="PubMed_Search",
        description=(
            "Search PubMed for scientific papers. "
            "Input should be a search query string (e.g., 'SIRT1 aging lifespan'). "
            "Returns a list of PMIDs (PubMed IDs) for relevant papers. "
            "Use this to find papers about protein/gene modifications and longevity."
        ),
        func=lambda query: "\n".join(search_pubmed(query))
    )
