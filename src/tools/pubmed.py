"""PubMed class for searching and fetching paper metadata."""
from typing import List, Dict, Any
import json
from langchain.tools import Tool
from Bio import Entrez, Medline
from src.config import NCBI_EMAIL, NCBI_API_KEY


class PubMed:
    """
    A unified class for interacting with PubMed API.

    Handles searching for papers and fetching their metadata including
    titles, abstracts, publication details, and MeSH terms.

    Example:
        pubmed = PubMed()
        pmids = pubmed.search("IGF1R aging", max_results=10)
        papers = pubmed.fetch(pmids)
    """

    def __init__(self, email: str = None, api_key: str = None):
        """
        Initialize PubMed client.

        Args:
            email: Email for NCBI (defaults to config)
            api_key: API key for NCBI (defaults to config)
        """
        self.email = email or NCBI_EMAIL
        self.api_key = api_key or NCBI_API_KEY

        # Configure Entrez
        Entrez.email = self.email
        if self.api_key:
            Entrez.api_key = self.api_key

    def search(self, query: str, max_results: int = 100, exclude_reviews: bool = True,
               free_full_text_only: bool = True) -> List[str]:
        """
        Search PubMed for papers matching the query.

        Args:
            query: Search query (e.g., "IGF1R aging")
            max_results: Maximum number of PMIDs to return
            exclude_reviews: Whether to exclude review articles
            free_full_text_only: Whether to include only free full-text articles

        Returns:
            List of PMIDs as strings
        """
        try:
            # Build search query with filters
            search_query = f"({query})"

            if exclude_reviews:
                search_query += " NOT Review[Publication Type]"

            if free_full_text_only:
                search_query += " AND free full text[Filter]"

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

    def fetch(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch paper metadata for given PMIDs.

        Args:
            pmids: List of PMIDs (strings or integers)

        Returns:
            List of dictionaries with paper metadata containing:
                - pmid: PubMed ID
                - title: Paper title
                - abstract: Abstract text
                - year: Publication year
                - journal: Journal name
                - mesh_terms: MeSH terms (keywords)
        """
        # Convert to list if needed and filter empty values
        if isinstance(pmids, str):
            pmid_list = [p.strip() for p in pmids.split('\n') if p.strip()]
        else:
            pmid_list = [str(p) for p in pmids if p]

        if not pmid_list:
            return []

        papers = []

        try:
            # Fetch records in batches (Entrez allows up to 200 at once)
            batch_size = 200
            for i in range(0, len(pmid_list), batch_size):
                batch = pmid_list[i:i + batch_size]

                handle = Entrez.efetch(
                    db="pubmed",
                    id=batch,
                    rettype="medline",
                    retmode="text"
                )

                records = Medline.parse(handle)

                for record in records:
                    paper = {
                        "pmid": record.get("PMID", ""),
                        "title": record.get("TI", ""),  # Title
                        "abstract": record.get("AB", ""),  # Abstract
                        "year": record.get("DP", "").split()[0] if record.get("DP") else None,  # Date Published
                        "journal": record.get("TA", ""),  # Title Abbreviation (journal)
                        "mesh_terms": record.get("MH", [])  # MeSH Headings (keywords)
                    }
                    papers.append(paper)

                handle.close()

            return papers

        except Exception as e:
            return [{"error": f"Error fetching abstracts: {str(e)}"}]

    def search_and_fetch(self, query: str, max_results: int = 100,
                        exclude_reviews: bool = True,
                        free_full_text_only: bool = True) -> List[Dict[str, Any]]:
        """
        Convenience method to search and fetch in one call.

        Args:
            query: Search query
            max_results: Maximum number of results
            exclude_reviews: Whether to exclude review articles
            free_full_text_only: Whether to include only free full-text articles

        Returns:
            List of paper metadata dictionaries
        """
        pmids = self.search(query, max_results, exclude_reviews, free_full_text_only)

        # Check for errors
        if pmids and isinstance(pmids[0], str) and pmids[0].startswith("Error"):
            return [{"error": pmids[0]}]

        return self.fetch(pmids)

    def create_search_tool(self) -> Tool:
        """Create a LangChain tool for PubMed search."""
        return Tool(
            name="PubMed_Search",
            description=(
                "Search PubMed for scientific papers. "
                "Input should be a search query string (e.g., 'SIRT1 aging lifespan'). "
                "Returns a list of PMIDs (PubMed IDs) for relevant papers. "
                "Use this to find papers about protein/gene modifications and longevity."
            ),
            func=lambda query: "\n".join(self.search(query))
        )

    def create_fetch_tool(self) -> Tool:
        """Create a LangChain tool for fetching PubMed abstracts."""
        return Tool(
            name="PubMed_Fetch_Abstracts",
            description=(
                "Fetch paper metadata (title, abstract, year, journal) from PubMed. "
                "Input should be a newline-separated string of PMIDs from PubMed_Search. "
                "Returns JSON with paper details including abstracts for screening."
            ),
            func=lambda pmids: json.dumps(self.fetch(pmids), indent=2)
        )
