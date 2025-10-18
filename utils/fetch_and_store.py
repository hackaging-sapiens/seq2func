"""
Integration script to fetch gene data from multiple APIs and store in PostgreSQL.

This script orchestrates the complete pipeline:
1. Fetch data from HGNC, Ensembl, UniProt, InterPro, and Open Genes
2. Store all data in PostgreSQL database

Usage:
    python utils/fetch_and_store.py <gene_symbol>
    python utils/fetch_and_store.py NRF2
"""

import sys
from typing import Optional

# Import fetch functions
from .fetch_data import (
    fetch_hgnc_data,
    fetch_ensembl_data,
    fetch_uniprot_data,
    fetch_interpro_data,
    fetch_opengenes_data
)

# Import database functions
from .database_operations import (
    connect_to_database,
    insert_gene_data,
    close_connection
)


def fetch_and_store_gene(gene_symbol: str) -> Optional[int]:
    """
    Fetch complete gene data from APIs and store in database.
    
    Args:
        gene_symbol: Gene symbol (e.g., "NRF2", "TP53")
    
    Returns:
        gene_id: Database gene_id if successful, None if failed
    """
    print("="*80)
    print(f"FETCHING AND STORING DATA FOR: {gene_symbol}")
    print("="*80)
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        print("\n[1/6] Connecting to database...")
        conn, cursor = connect_to_database()
        
        # Fetch HGNC data (required - provides IDs for other APIs)
        print(f"\n[2/6] Fetching HGNC data for '{gene_symbol}'...")
        hgnc_data = fetch_hgnc_data(gene_symbol)
        
        hgnc_id, gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases = hgnc_data
        
        print(f"  ✓ Found: {approved_symbol} ({gene_name})")
        print(f"    HGNC ID: {hgnc_id}")
        print(f"    NCBI Gene ID: {gene_id}")
        print(f"    Ensembl ID: {ensembl_gene_id}")
        if gene_aliases:
            print(f"    Gene Aliases: {gene_aliases}")
        
        # Prepare HGNC data dict for database
        hgnc_dict = {
            'hgnc_id': hgnc_id,
            'gene_id': gene_id,
            'ensembl_gene_id': ensembl_gene_id,
            'approved_symbol': approved_symbol,
            'gene_name': gene_name,
            'gene_aliases': gene_aliases
        }
        
        # Fetch Ensembl data (DNA sequence)
        print(f"\n[3/6] Fetching DNA sequence from Ensembl...")
        dna_sequence = None
        if ensembl_gene_id and ensembl_gene_id != "N/A":
            try:
                dna_sequence = fetch_ensembl_data(ensembl_gene_id)
                print(f"  ✓ DNA sequence retrieved ({len(dna_sequence)} bp)")
            except Exception as e:
                print(f"  ✗ Could not fetch DNA sequence: {e}")
        else:
            print(f"  ⊘ No Ensembl Gene ID available")
        
        # Fetch UniProt data (protein + PTMs)
        print(f"\n[4/6] Fetching protein data from UniProt...")
        protein_data = None
        protein_id = None
        try:
            # Try with approved symbol first, fallback to original
            try:
                uniprot_result = fetch_uniprot_data(approved_symbol)
            except:
                uniprot_result = fetch_uniprot_data(gene_symbol)
            
            protein_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases = uniprot_result
            
            print(f"  ✓ Protein found: {protein_id}")
            print(f"    Name: {protein_name}")
            if protein_aliases:
                print(f"    Aliases: {protein_aliases}")
            print(f"    Sequence length: {len(protein_sequence) if protein_sequence != 'N/A' else 0} aa")
            print(f"    PTMs: {len(ptm_data)} modifications")
            
            protein_data = (protein_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases)
        except Exception as e:
            print(f"  ✗ Could not fetch protein data: {e}")
        
        # Fetch InterPro data (protein domains)
        print(f"\n[5/6] Fetching protein domains from InterPro...")
        domain_data = None
        if protein_id and protein_id != "N/A":
            try:
                domain_data = fetch_interpro_data(protein_id)
                print(f"  ✓ Found {len(domain_data)} protein domains")
            except Exception as e:
                print(f"  ✗ Could not fetch domain data: {e}")
        else:
            print(f"  ⊘ No UniProt ID available")
        
        # Fetch Open Genes data (aging/longevity)
        print(f"\n[6/6] Fetching aging/longevity data from Open Genes...")
        aging_data = None
        try:
            # Try with original symbol first, then approved symbol
            try:
                opengenes_result = fetch_opengenes_data(gene_symbol)
            except ValueError:
                opengenes_result = fetch_opengenes_data(approved_symbol)
            
            aging_data = opengenes_result
            print(f"  ✓ Aging data found")
            print(f"    Expression change: {aging_data.get('expression_change')}")
            print(f"    Confidence: {aging_data.get('confidence_level')}")
            print(f"    Aging mechanisms: {len(aging_data.get('aging_mechanisms', []))}")
        except ValueError:
            print(f"  ⊘ Gene not found in Open Genes (not all genes have aging associations)")
        except Exception as e:
            print(f"  ✗ Error fetching aging data: {e}")
        
        # Store all data in database
        print("\n" + "="*80)
        print("STORING DATA IN DATABASE")
        print("="*80)
        
        db_gene_id = insert_gene_data(
            conn=conn,
            cursor=cursor,
            hgnc_data=hgnc_dict,
            dna_data=dna_sequence,
            protein_data=protein_data,
            domain_data=domain_data,
            aging_data=aging_data
        )
        
        print("\n" + "="*80)
        print(f"✓ SUCCESS! Gene data stored with ID: {db_gene_id}")
        print("="*80)
        
        return db_gene_id
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def fetch_and_store_multiple_genes(gene_symbols: list) -> dict:
    """
    Fetch and store data for multiple genes.
    
    Args:
        gene_symbols: List of gene symbols
    
    Returns:
        Dictionary mapping gene_symbol to gene_id (or None if failed)
    """
    results = {}
    
    print("\n" + "="*80)
    print(f"PROCESSING {len(gene_symbols)} GENES")
    print("="*80)
    
    for i, gene_symbol in enumerate(gene_symbols, 1):
        print(f"\n\n{'='*80}")
        print(f"GENE {i}/{len(gene_symbols)}: {gene_symbol}")
        print("="*80)
        
        gene_id = fetch_and_store_gene(gene_symbol)
        results[gene_symbol] = gene_id
    
    # Summary
    print("\n\n" + "="*80)
    print("PROCESSING COMPLETE - SUMMARY")
    print("="*80)
    
    successful = sum(1 for gid in results.values() if gid is not None)
    failed = len(results) - successful
    
    print(f"\nTotal genes processed: {len(gene_symbols)}")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    
    if successful > 0:
        print("\nSuccessfully stored genes:")
        for symbol, gid in results.items():
            if gid is not None:
                print(f"  - {symbol}: gene_id = {gid}")
    
    if failed > 0:
        print("\nFailed genes:")
        for symbol, gid in results.items():
            if gid is None:
                print(f"  - {symbol}")
    
    return results


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python utils/fetch_and_store.py <gene_symbol> [gene_symbol2 ...]")
        print("\nExamples:")
        print("  python utils/fetch_and_store.py NRF2")
        print("  python utils/fetch_and_store.py TP53 BRCA1 FOXO3")
        sys.exit(1)
    
    gene_symbols = sys.argv[1:]
    
    if len(gene_symbols) == 1:
        # Single gene
        gene_id = fetch_and_store_gene(gene_symbols[0])
        sys.exit(0 if gene_id else 1)
    else:
        # Multiple genes
        results = fetch_and_store_multiple_genes(gene_symbols)
        failed = sum(1 for gid in results.values() if gid is None)
        sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
