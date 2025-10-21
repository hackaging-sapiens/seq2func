"""
Process proteins from config file and store in database.

This script reads the protein list from config/config_proteins.yaml
and processes each protein through the complete pipeline.

Usage:
    python process_proteins.py
"""

import yaml
import os
from typing import List

# Import our functions
from utils.fetch_and_store import fetch_and_store_multiple_genes
from utils.gene_master import fetch_comprehensive_gene_data, populate_gene_master_table
from utils.protein_master import fetch_comprehensive_protein_data, populate_protein_master_table


def load_proteins_from_config(config_path: str = "config/config_proteins.yaml") -> List[str]:
    """
    Load protein list from YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file
    
    Returns:
        List of protein symbols
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        proteins = config.get('proteins', [])
        
        # Filter out commented lines (proteins starting with #)
        active_proteins = [p for p in proteins if not str(p).strip().startswith('#')]
        
        print(f"Loaded {len(active_proteins)} active proteins from {config_path}")
        print(f"Total entries in config: {len(proteins)}")
        
        return active_proteins
        
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return []
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return []


def main():
    """Main function to process all proteins from config."""
    print("="*80)
    print("PROCESSING PROTEINS FROM CONFIG FILE")
    print("="*80)
    
    # Load proteins from config
    proteins = load_proteins_from_config()
    
    if not proteins:
        print("\n✗ No active proteins found in configuration file.")
        print("\nTo add proteins, edit config/config_proteins.yaml:")
        print("  - Uncomment proteins by removing the '#'")
        print("  - Add new proteins to the list")
        return
    
    print(f"\nActive proteins to process:")
    for i, protein in enumerate(proteins, 1):
        print(f"  {i:2d}. {protein}")
    
    # Display processing information
    print(f"\nProcessing {len(proteins)} proteins.")
    print("Fetching data from:")
    print("  - HGNC (gene nomenclature)")
    print("  - Ensembl (DNA sequences)")
    print("  - UniProt (protein data + PTMs)")
    print("  - InterPro (protein domains)")
    print("  - Open Genes (aging/longevity associations)")
    
    # Process all proteins
    results = fetch_and_store_multiple_genes(proteins)
    
    # Also populate the master tables with comprehensive data
    print("\n" + "="*80)
    print("POPULATING MASTER TABLES")
    print("="*80)
    
    # Get successfully processed proteins
    successful_proteins = [symbol for symbol, gid in results.items() if gid is not None]
    
    if successful_proteins:
        print(f"\nPopulating gene_master and protein_master tables for {len(successful_proteins)} proteins...")
        
        # Fetch and populate gene master data
        print("\n[1/2] Fetching comprehensive gene data for master table...")
        gene_records = []
        for symbol in successful_proteins:
            gene_record = fetch_comprehensive_gene_data(symbol)
            if gene_record:
                gene_records.append(gene_record)
        
        if gene_records:
            populate_gene_master_table(gene_records)
            print(f"✓ Updated gene_master table with {len(gene_records)} records")
        else:
            print("⚠ No gene records found for master table")
        
        # Fetch and populate protein master data
        print("\n[2/2] Fetching comprehensive protein data for master table...")
        protein_records = []
        for symbol in successful_proteins:
            protein_record = fetch_comprehensive_protein_data(symbol)
            if protein_record:
                protein_records.append(protein_record)
        
        if protein_records:
            populate_protein_master_table(protein_records)
            print(f"✓ Updated protein_master table with {len(protein_records)} records")
        else:
            print("⚠ No protein records found for master table")
    else:
        print("\n⚠ No successfully processed proteins found, skipping master table updates")
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    successful = sum(1 for gid in results.values() if gid is not None)
    failed = len(results) - successful
    
    print(f"\nConfiguration: config/config_proteins.yaml")
    print(f"Proteins in config: {len(proteins)}")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print(f"\n✓ Successfully stored {successful} proteins in database")
        print("✓ Updated gene_master and protein_master tables")
        print("You can now query the database to analyze the data.")
    
    if failed > 0:
        print(f"\n⚠ {failed} proteins failed to process")
        print("Check the error messages above for details.")
        print("Common issues:")
        print("  - Gene symbol not found in databases")
        print("  - Network connectivity issues")
        print("  - Database connection problems")


if __name__ == "__main__":
    main()
