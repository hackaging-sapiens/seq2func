"""PubMed fetch tool for retrieving paper metadata from PMIDs."""
from typing import List, Dict, Any
import json
from langchain.tools import Tool
from Bio import Entrez, Medline
from src.config import NCBI_EMAIL, NCBI_API_KEY


# Configure Entrez
Entrez.email = NCBI_EMAIL
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY


def fetch_abstracts(pmids: str) -> List[Dict[str, Any]]:
    """
    Fetch paper metadata for given PMIDs.

    Args:
        pmids: Newline-separated string of PMIDs (e.g., "12345\\n67890")

    Returns:
        List of dictionaries with paper metadata
    """
    # Parse PMIDs from newline-separated string
    pmid_list = [p.strip() for p in pmids.split('\n') if p.strip()]

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
                    "title": record.get("TI", ""), # Title
                    "abstract": record.get("AB", ""), # Abstract
                    "year": record.get("DP", "").split()[0] if record.get("DP") else None, # Date Published
                    "journal": record.get("TA", ""), # Title Abbreviation (journal)
                    "mesh_terms": record.get("MH", []) # MeSH Headings (keywords)
                }
                papers.append(paper)

            handle.close()

        return papers

    except Exception as e:
        return [{"error": f"Error fetching abstracts: {str(e)}"}]


def create_pubmed_fetch_tool() -> Tool:
    """Create a LangChain tool for fetching PubMed abstracts."""
    return Tool(
        name="PubMed_Fetch_Abstracts",
        description=(
            "Fetch paper metadata (title, abstract, year, journal) from PubMed. "
            "Input should be a newline-separated string of PMIDs from PubMed_Search. "
            "Returns JSON with paper details including abstracts for screening."
        ),
        func=lambda pmids: json.dumps(fetch_abstracts(pmids), indent=2)
    )
