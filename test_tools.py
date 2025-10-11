"""Test script for PubMed tools."""
import json
from src.tools.pubmed_search import search_pubmed
from src.tools.pubmed_fetch import fetch_abstracts


def test_pubmed_tools():
    """Test PubMed search and fetch tools."""

    # Test 1: Search PubMed
    print("=" * 50)
    print("TEST 1: Searching PubMed for 'SIRT1 aging'")
    print("=" * 50)

    pmids = search_pubmed("SIRT1 aging", max_results=20)
    print(f"\nFound {len(pmids)} PMIDs:")
    print(pmids[:5])  # Show first 5

    if not pmids or pmids[0].startswith("Error"):
        print("\n❌ Search failed!")
        return

    print("\n✓ Search successful!")

    # Test 2: Fetch abstracts
    print("\n" + "=" * 50)
    print("TEST 2: Fetching abstracts for first 5 PMIDs")
    print("=" * 50)

    # Convert list to newline-separated string (mimicking tool output)
    pmid_string = "\n".join(pmids[:5])

    papers = fetch_abstracts(pmid_string)

    if papers and "error" in papers[0]:
        print("\n❌ Fetch failed!")
        print(papers[0]["error"])
        return

    print(f"\n✓ Fetched {len(papers)} papers")

    # Display first paper
    if papers:
        print("\n" + "-" * 50)
        print("First paper:")
        print("-" * 50)
        paper = papers[0]
        print(f"PMID: {paper['pmid']}")
        print(f"Title: {paper['title']}")
        print(f"Year: {paper['year']}")
        print(f"Journal: {paper['journal']}")
        print(f"Abstract (first 200 chars): {paper['abstract'][:200]}...")
        print(f"MeSH terms: {paper['mesh_terms'][:3] if paper['mesh_terms'] else 'None'}")

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    test_pubmed_tools()
