"""
Protein Master Data Extractor and Populator

This script fetches protein master data from multiple sources (UniProt, Ensembl, RefSeq, HGNC)
and populates the protein_master table with the following columns:
- protein_id (same as uniprot_protein_id)
- uniprot_protein_id
- ensembl_protein_id
- refseq_protein_id
- protein_symbol
- protein_symbol_aliases
- protein_name

Usage:
    python utils/protein_master.py
"""

import os
import sys
import csv
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path to import utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.database_operations import connect_to_database, load_database_config, close_connection
    from utils.fetch_data import (
        fetch_hgnc_data, fetch_uniprot_data, fetch_refseq_data, 
        fetch_ensembl_protein_id
    )
except ImportError:
    # Fallback for direct execution
    from database_operations import connect_to_database, load_database_config, close_connection
    from fetch_data import (
        fetch_hgnc_data, fetch_uniprot_data, fetch_refseq_data,
        fetch_ensembl_protein_id
    )


def load_proteins_from_config(config_path: str = "config/config_proteins.yaml") -> List[str]:
    """
    Load protein symbols from config file.
    
    Returns:
        List of protein symbols to process
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        proteins = config.get('proteins', [])
        # Filter out commented lines and return active protein symbols
        active_proteins = [p.strip() for p in proteins if isinstance(p, str) and not p.strip().startswith('#')]
        return active_proteins
        
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found")
        return []
    except Exception as e:
        print(f"Error loading config: {e}")
        return []


def fetch_comprehensive_protein_data(protein_symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive protein data from multiple sources (UniProt, Ensembl, RefSeq, HGNC).
    
    Args:
        protein_symbol: Protein symbol to fetch data for
    
    Returns:
        Dictionary with comprehensive protein data or None if not found
    """
    try:
        print(f"  Fetching data for: {protein_symbol}")
        
        # First get gene data to obtain NCBI Gene ID for RefSeq lookup
        try:
            hgnc_id, ncbi_gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases = fetch_hgnc_data(protein_symbol)
        except Exception as e:
            print(f"    Warning: Could not fetch HGNC data for {protein_symbol}: {e}")
            ncbi_gene_id = None
        
        # Fetch UniProt data (primary source for protein information)
        try:
            uniprot_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases = fetch_uniprot_data(protein_symbol)
        except Exception as e:
            print(f"    ✗ Could not fetch UniProt data for {protein_symbol}: {e}")
            return None
        
        if not uniprot_id or uniprot_id == "N/A":
            print(f"    ✗ No UniProt ID found for {protein_symbol}")
            return None
        
        # Fetch Ensembl protein ID using UniProt cross-references
        ensembl_protein_id = None
        try:
            ensembl_protein_id = fetch_ensembl_protein_id(uniprot_id)
        except Exception as e:
            print(f"    Warning: Could not fetch Ensembl protein ID: {e}")
        
        # Fetch RefSeq protein ID using NCBI Gene ID
        refseq_protein_id = None
        try:
            if ncbi_gene_id and ncbi_gene_id != "N/A":
                refseq_mrna_id, refseq_protein_id = fetch_refseq_data(str(ncbi_gene_id))
                if refseq_protein_id:
                    print(f"    ✓ Found RefSeq protein ID: {refseq_protein_id}")
        except Exception as e:
            print(f"    Warning: Could not fetch RefSeq data: {e}")
        
        # Prepare the comprehensive protein record
        protein_record = {
            'protein_id': uniprot_id,  # Primary key
            'uniprot_protein_id': uniprot_id,
            'ensembl_protein_id': ensembl_protein_id or '',
            'refseq_protein_id': refseq_protein_id or '',
            'protein_symbol': approved_symbol or protein_symbol,
            'protein_symbol_aliases': json.dumps(protein_aliases) if protein_aliases else '[]',
            'protein_name': protein_name
        }
        
        print(f"    ✓ Found: {protein_name}")
        print(f"      UniProt: {uniprot_id}")
        print(f"      Ensembl: {ensembl_protein_id or 'N/A'}")
        print(f"      RefSeq: {refseq_protein_id or 'N/A'}")
        
        return protein_record
        
    except Exception as e:
        print(f"    ✗ Error fetching data for {protein_symbol}: {e}")
        return None


def populate_protein_master_table(protein_records: List[Dict[str, Any]]) -> int:
    """
    Insert protein records into the protein_master table.
    
    Args:
        protein_records: List of protein dictionaries to insert
    
    Returns:
        Number of records successfully inserted
    """
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn, cursor = connect_to_database()
        
        # Load database configuration
        db_config = load_database_config()
        tables = db_config.get('tables', {})
        protein_master_table = tables.get('protein_master', 'protein_master')
        
        inserted_count = 0
        
        for protein_record in protein_records:
            try:
                # Insert or update protein record
                insert_query = f"""
                INSERT INTO {protein_master_table} (
                    protein_id, uniprot_protein_id, ensembl_protein_id, refseq_protein_id,
                    protein_symbol, protein_symbol_aliases, protein_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protein_id) DO UPDATE SET
                    uniprot_protein_id = EXCLUDED.uniprot_protein_id,
                    ensembl_protein_id = EXCLUDED.ensembl_protein_id,
                    refseq_protein_id = EXCLUDED.refseq_protein_id,
                    protein_symbol = EXCLUDED.protein_symbol,
                    protein_symbol_aliases = EXCLUDED.protein_symbol_aliases,
                    protein_name = EXCLUDED.protein_name,
                    updated_at = now()
                """
                
                cursor.execute(insert_query, (
                    protein_record['protein_id'],
                    protein_record['uniprot_protein_id'],
                    protein_record['ensembl_protein_id'],
                    protein_record['refseq_protein_id'],
                    protein_record['protein_symbol'],
                    protein_record['protein_symbol_aliases'],
                    protein_record['protein_name']
                ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"    ✗ Error inserting {protein_record.get('protein_symbol', 'Unknown')}: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"✓ Inserted/updated {inserted_count} protein records in protein_master table")
        return inserted_count
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ Error populating protein_master table: {e}")
        raise
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def fetch_protein_master_data_from_db() -> List[Dict[str, Any]]:
    """
    Fetch protein master data from the protein_master table for export.
    
    Returns:
        List of dictionaries containing protein master data
    """
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn, cursor = connect_to_database()
        
        # Load database configuration to get table names
        db_config = load_database_config()
        tables = db_config.get('tables', {})
        protein_master_table = tables.get('protein_master', 'protein_master')
        
        # Query to fetch all protein master data
        query = f"""
        SELECT 
            protein_id,
            uniprot_protein_id,
            ensembl_protein_id,
            refseq_protein_id,
            protein_symbol,
            protein_symbol_aliases,
            protein_name
        FROM {protein_master_table}
        ORDER BY protein_id
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        protein_data = []
        for row in rows:
            protein_record = {
                'protein_id': row[0],
                'uniprot_protein_id': row[1],
                'ensembl_protein_id': row[2] or '',
                'refseq_protein_id': row[3] or '',
                'protein_symbol': row[4],
                'protein_symbol_aliases': row[5] if isinstance(row[5], str) else str(row[5]),
                'protein_name': row[6]
            }
            protein_data.append(protein_record)
        
        print(f"✓ Fetched {len(protein_data)} protein records from protein_master table")
        return protein_data
        
    except Exception as e:
        print(f"✗ Error fetching protein master data: {e}")
        raise
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def export_protein_master_csv(protein_data: List[Dict[str, Any]], output_file: str = "protein_master.csv") -> None:
    """
    Export protein master data to CSV file.
    
    Args:
        protein_data: List of protein dictionaries
        output_file: Output CSV filename
    """
    if not protein_data:
        print("No protein data to export")
        return
    
    # Define column order
    columns = [
        'protein_id',
        'uniprot_protein_id',
        'ensembl_protein_id',
        'refseq_protein_id', 
        'protein_symbol',
        'protein_symbol_aliases',
        'protein_name'
    ]
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for protein in protein_data:
                # Convert protein_symbol_aliases to string if it's JSONB
                if isinstance(protein.get('protein_symbol_aliases'), (list, dict)):
                    protein['protein_symbol_aliases'] = str(protein['protein_symbol_aliases'])
                writer.writerow(protein)
        
        print(f"✓ Exported {len(protein_data)} protein records to {output_file}")
        
    except Exception as e:
        print(f"✗ Error exporting to CSV: {e}")
        raise


def main():
    """Main function to fetch comprehensive protein data and populate protein_master table."""
    print("=" * 60)
    print("Protein Master Data Extractor and Populator")
    print("=" * 60)
    
    try:
        # Load protein symbols from config
        print("\n[1/4] Loading protein symbols from config...")
        protein_symbols = load_proteins_from_config()
        
        if not protein_symbols:
            print("No protein symbols found in config file")
            return
        
        print(f"Found {len(protein_symbols)} protein symbols: {', '.join(protein_symbols)}")
        
        # Fetch comprehensive protein data from external sources
        print(f"\n[2/4] Fetching comprehensive protein data from external sources...")
        print("Sources: UniProt, Ensembl, RefSeq, HGNC")
        
        protein_records = []
        for symbol in protein_symbols:
            protein_record = fetch_comprehensive_protein_data(symbol)
            if protein_record:
                protein_records.append(protein_record)
        
        if not protein_records:
            print("No protein data successfully fetched")
            return
        
        # Populate protein_master table
        print(f"\n[3/4] Populating protein_master table...")
        inserted_count = populate_protein_master_table(protein_records)
        
        # Fetch and export data
        print(f"\n[4/4] Exporting protein master data to CSV...")
        protein_data = fetch_protein_master_data_from_db()
        
        if protein_data:
            output_file = "protein_master.csv"
            export_protein_master_csv(protein_data, output_file)
            
            print(f"\n✓ Protein master data processing completed!")
            print(f"  Processed symbols: {len(protein_symbols)}")
            print(f"  Successfully fetched: {len(protein_records)}")
            print(f"  Database records: {len(protein_data)}")
            print(f"  Output file: {output_file}")
        else:
            print("No protein data found in database for export")
        
    except Exception as e:
        print(f"\n✗ Error in protein master processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
