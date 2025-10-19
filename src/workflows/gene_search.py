"""
Workflow for searching and screening gene literature from PubMed.

This workflow:
1. Builds a PubMed search query for a gene
2. Searches PubMed for relevant papers
3. Screens papers using LLM for sequence→function→aging links
4. Returns top N papers ranked by relevance score
5. Saves results to CSV
"""

import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from tqdm import tqdm
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.tools.pubmed import PubMed
from src.tools.screening import Screening

if TYPE_CHECKING:
    from src.tasks.task_manager import ProgressCallback, CancellationToken

class GeneLiteratureSearch:
    """
    Orchestrates PubMed search and LLM screening for gene literature.

    Example:
        workflow = GeneLiteratureSearch()
        results = workflow.search_gene(
            gene_symbol="NRF2",
            gene_id=4780,
            max_results=200,
            top_n=20
        )
        workflow.save_results(results, "data/nrf2_papers.csv")
    """

    def __init__(self):
        """Initialize the workflow with PubMed and Screening tools."""
        self.pubmed = PubMed()
        self.screening = Screening()

    def search_gene(
        self,
        gene_symbol: str,
        gene_id: Optional[int] = None,
        max_results: int = 200,
        top_n: int = 20,
        include_reprogramming: bool = False,
        custom_terms: Optional[List[str]] = None,
        progress_callback: Optional['ProgressCallback'] = None,
        cancellation_token: Optional['CancellationToken'] = None
    ) -> List[Dict[str, Any]]:
        """
        Search and screen papers for a gene.

        Args:
            gene_symbol: Gene symbol (e.g., "NRF2", "SOX2")
            gene_id: NCBI Gene ID (Entrez ID) for unique identification (optional)
            max_results: Maximum number of papers to retrieve from PubMed
            top_n: Number of top-ranked papers to return
            include_reprogramming: Whether to include reprogramming terms in search
            custom_terms: Additional custom search terms
            progress_callback: Optional callback for reporting progress
            cancellation_token: Optional token to check for cancellation

        Returns:
            List of top N papers with metadata and scores
        """
        # Helper to report progress (sends to both callback and stdout for debugging)
        def report_progress(step: str, step_num: int, papers_screened: Optional[int] = None,
                          total_papers: Optional[int] = None, message: str = ""):
            # Always print to stdout for debugging
            if papers_screened is not None and total_papers is not None:
                print(f"[Step {step_num}/4] {message} ({papers_screened}/{total_papers})")
            else:
                print(f"[Step {step_num}/4] {message or step}")

            # Also send to progress callback if available
            if progress_callback:
                progress_callback.update(
                    current_step=step,
                    step_number=step_num,
                    total_steps=4,
                    papers_screened=papers_screened,
                    total_papers=total_papers,
                    message=message
                )

        # Debug: Print header
        print(f"\n{'='*80}")
        print(f"GENE LITERATURE SEARCH: {gene_symbol}")
        if gene_id:
            print(f"Gene ID: {gene_id}")
        print(f"Max Results: {max_results} | Top N: {top_n}")
        print(f"{'='*80}\n")

        # Step 1: Build search query
        report_progress("Building query", 1, message=f"Building PubMed search query for {gene_symbol}")
        query = self.pubmed.build_search_query(
            gene_name=gene_symbol,
            include_reprogramming=include_reprogramming,
            custom_terms=custom_terms
        )
        print(f"Query: {query}")

        # Check cancellation
        if cancellation_token and cancellation_token.is_cancelled():
            return []

        # Step 2: Search PubMed
        report_progress("Searching PubMed", 2, message=f"Searching PubMed (max {max_results} results)")
        pmids = self.pubmed.search(query, max_results=max_results)
        print(f"✓ Found {len(pmids)} papers")

        if not pmids:
            report_progress("Search complete", 4, message="No papers found")
            print("No papers found. Exiting.\n")
            return []

        # Check cancellation
        if cancellation_token and cancellation_token.is_cancelled():
            return []

        # Step 3: Fetch paper metadata
        report_progress("Fetching metadata", 3, message=f"Fetching metadata for {len(pmids)} papers")
        papers = self.pubmed.fetch(pmids)
        print(f"✓ Fetched {len(papers)} papers")

        # Check cancellation
        if cancellation_token and cancellation_token.is_cancelled():
            print("Search cancelled by user.\n")
            return []

        # Step 4: Screen papers with LLM
        report_progress("Screening papers", 4, papers_screened=0, total_papers=len(papers),
                       message="Starting paper screening with AI")
        results = []

        for idx, paper in enumerate(papers, 1):
            # Check cancellation before each paper
            if cancellation_token and cancellation_token.is_cancelled():
                # Return partial results
                break

            # Update progress
            report_progress("Screening papers", 4, papers_screened=idx, total_papers=len(papers),
                          message=f"Screening paper {idx}/{len(papers)}")

            screening_result = self.screening.screen_paper(
                title=paper.get("title", ""),
                abstract=paper.get("abstract", ""),
                keywords=paper.get("mesh_terms", [])
            )

            # Combine paper metadata with screening results
            result = {
                "gene_id": gene_id,
                "gene_symbol": gene_symbol,
                "pmid": paper.get("pmid", ""),
                "title": paper.get("title", ""),
                "year": paper.get("year", ""),
                "journal": paper.get("journal", ""),
                "score": screening_result.get("score", 0.0),
                "relevant": screening_result.get("relevant", False),
                "reasoning": screening_result.get("reasoning", ""),
                "search_date": datetime.now().strftime("%Y-%m-%d")
            }
            results.append(result)

        # Filter for relevant papers only, then sort by score and return top N
        relevant_results = [r for r in results if r["relevant"]]
        results_sorted = sorted(relevant_results, key=lambda x: x["score"], reverse=True)
        top_results = results_sorted[:top_n]

        # Final progress update
        was_cancelled = cancellation_token and cancellation_token.is_cancelled()
        status = "cancelled" if was_cancelled else "completed"
        report_progress(f"Screening {status}", 4, papers_screened=len(results), total_papers=len(papers),
                       message=f"Screened {len(results)} papers, found {len(relevant_results)} relevant")

        # Debug: Print summary
        print(f"\n{'='*80}")
        print(f"SCREENING COMPLETE")
        print(f"{'='*80}")
        print(f"Total papers screened: {len(results)}")
        print(f"Relevant papers (relevant=True): {len(relevant_results)}")
        print(f"Top {len(top_results)} relevant papers selected (requested: {top_n})")
        if was_cancelled:
            print("Note: Search was cancelled by user")
        print(f"{'='*80}\n")

        return top_results

    def save_results(
        self,
        results: List[Dict[str, Any]],
        output_file: str,
        append: bool = False
    ) -> None:
        """
        Save search results to CSV file.

        Args:
            results: List of paper results from search_gene()
            output_file: Path to output CSV file
            append: If True, append to existing file. If False, overwrite.
        """
        if not results:
            print("No results to save.")
            return

        # Create parent directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Define CSV columns
        fieldnames = [
            "gene_id",
            "gene_symbol",
            "pmid",
            "title",
            "year",
            "journal",
            "score",
            "relevant",
            "reasoning",
            "search_date"
        ]

        # Write to CSV
        mode = 'a' if append else 'w'
        write_header = not (append and output_path.exists())

        with open(output_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if write_header:
                writer.writeheader()

            writer.writerows(results)

        print(f"✓ Saved {len(results)} results to {output_file}")

def batch_search_genes(
    genes: List[Dict[str, Any]],
    output_file: str,
    max_results: int = 200,
    top_n: int = 20,
    skip_existing: bool = True
) -> List[Dict[str, Any]]:
    """
    Batch search multiple genes and save all results to a single CSV.

    Args:
        genes: List of gene dicts with keys: gene_symbol, gene_id, include_reprogramming
               Example: [
                   {"gene_symbol": "NRF2", "gene_id": 4780, "include_reprogramming": False},
                   {"gene_symbol": "SOX2", "gene_id": 6657, "include_reprogramming": True}
               ]
        output_file: Path to output CSV file
        max_results: Maximum papers to retrieve per gene
        top_n: Number of top papers to save per gene
        skip_existing: If True, skip genes that already have results in the CSV file

    Returns:
        List of all results across all genes
    """
    workflow = GeneLiteratureSearch()
    all_results = []

    # Check existing genes if skip_existing is True
    existing_genes = set()
    if skip_existing and Path(output_file).exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Track by gene_id if available, otherwise by gene_symbol
                gene_key = row.get("gene_id")
                existing_genes.add(gene_key)

    print(f"\n{'='*80}")
    print(f"BATCH GENE LITERATURE SEARCH")
    print(f"Genes to process: {len(genes)}")
    print(f"Top papers per gene: {top_n}")
    if skip_existing and existing_genes:
        print(f"Genes already in database: {len(existing_genes)}")
        print(f"Skip existing: {skip_existing}")
    print(f"{'='*80}\n")

    processed_count = 0
    skipped_count = 0

    for i, gene in enumerate(genes, 1):
        gene_key = str(gene.get("gene_id"))

        # Skip if gene already exists in CSV
        if skip_existing and gene_key in existing_genes:
            print(f"⊘ Skipping {gene['gene_symbol']} (gene_id: {gene.get('gene_id')}) - already in database")
            skipped_count += 1
            continue

        print(f"\n{'='*80}")
        print(f"Processing gene {i}/{len(genes)}: {gene['gene_symbol']}")
        print(f"{'='*80}\n")

        results = workflow.search_gene(
            gene_symbol=gene["gene_symbol"],
            gene_id=gene.get("gene_id"),
            max_results=max_results,
            top_n=top_n,
            include_reprogramming=gene.get("include_reprogramming", False)
        )

        all_results.extend(results)

        # Append to CSV after each gene (in case of errors/interruption)
        workflow.save_results(results, output_file, append=(processed_count > 0 or len(existing_genes) > 0))
        processed_count += 1

    print(f"\n{'='*80}")
    print(f"BATCH SEARCH COMPLETE")
    print(f"{'='*80}")
    print(f"Total genes in list: {len(genes)}")
    print(f"Genes processed: {processed_count}")
    print(f"Genes skipped: {skipped_count}")
    print(f"Papers saved this run: {len(all_results)}")
    print(f"Output file: {output_file}")
    print(f"{'='*80}\n")

    return all_results


if __name__ == "__main__":
    # Command-line interface for batch processing only
    import sys

    if len(sys.argv) < 2:
        print("Usage: python gene_search.py <gene_mapping_file> [--force]")
        print("\nArguments:")
        print("  gene_mapping_file    CSV file with gene mappings (gene_symbol, gene_id, include_reprogramming)")
        print("  --force              Optional: Rerun genes that already exist in the database")
        print("\nExamples:")
        print("  python gene_search.py data/gene_mappings.csv")
        print("  python gene_search.py data/gene_mappings.csv --force")
        sys.exit(1)

    # Read gene mappings from CSV
    mapping_file = sys.argv[1]

    genes = []
    with open(mapping_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            genes.append({
                "gene_symbol": row["gene_symbol"],
                "gene_id": int(row["gene_id"]) if row.get("gene_id") else None,
                "include_reprogramming": row.get("include_reprogramming", "false").lower() == "true"
            })

    print(f"Loaded {len(genes)} genes from {mapping_file}")
    print(f"Genes: {', '.join(g['gene_symbol'] for g in genes)}\n")

    # Check for --force flag to rerun all genes
    skip_existing = "--force" not in sys.argv

    # Run batch search
    all_results = batch_search_genes(
        genes=genes,
        output_file="data/all_genes_results.csv",
        max_results=200,
        top_n=20,
        skip_existing=skip_existing
    )
