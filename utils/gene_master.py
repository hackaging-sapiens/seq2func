"""
Gene Master Data Extractor and Populator

This script fetches gene master data from multiple sources (Ensembl, HGNC, NCBI) 
and populates the gene_master table with the following columns:
- gene_id (same as ensembl_gene_id)
- ensembl_gene_id 
- hgnc_gene_id
- ncbi_gene_id
- gene_symbol
- gene_symbol_aliases
- gene_name

Usage:
    python utils/gene_master.py
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
    from utils.fetch_data import fetch_hgnc_data, fetch_ensembl_data, fetch_refseq_data
except ImportError:
    # Fallback for direct execution
    from database_operations import connect_to_database, load_database_config, close_connection
    from fetch_data import fetch_hgnc_data, fetch_ensembl_data, fetch_refseq_data


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


def fetch_comprehensive_gene_data(gene_symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive gene data from multiple sources (HGNC, Ensembl, NCBI).
    
    Args:
        gene_symbol: Gene symbol to fetch data for
    
    Returns:
        Dictionary with comprehensive gene data or None if not found
    """
    try:
        print(f"  Fetching data for: {gene_symbol}")
        
        # Fetch HGNC data (primary source for gene identifiers)
        hgnc_id, ncbi_gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases = fetch_hgnc_data(gene_symbol)
        
        # Skip if no Ensembl ID (required for our primary key)
        if not ensembl_gene_id or ensembl_gene_id == "N/A":
            print(f"    ✗ No Ensembl Gene ID found for {gene_symbol}")
            return None
        
        # Prepare the comprehensive gene record
        gene_record = {
            'gene_id': ensembl_gene_id,  # Primary key
            'ensembl_gene_id': ensembl_gene_id,
            'hgnc_gene_id': hgnc_id,
            'ncbi_gene_id': int(ncbi_gene_id) if ncbi_gene_id and ncbi_gene_id != "N/A" else None,
            'gene_symbol': approved_symbol or gene_symbol,
            'gene_symbol_aliases': json.dumps(gene_aliases) if gene_aliases else '[]',
            'gene_name': gene_name
        }
        
        print(f"    ✓ Found: {approved_symbol} ({gene_name})")
        print(f"      Ensembl: {ensembl_gene_id}")
        print(f"      HGNC: {hgnc_id}")
        print(f"      NCBI: {ncbi_gene_id}")
        
        return gene_record
        
    except Exception as e:
        print(f"    ✗ Error fetching data for {gene_symbol}: {e}")
        return None


def populate_gene_master_table(gene_records: List[Dict[str, Any]]) -> int:
    """
    Insert gene records into the gene_master table.
    
    Args:
        gene_records: List of gene dictionaries to insert
    
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
        gene_master_table = tables.get('gene_master', 'gene_master')
        
        inserted_count = 0
        
        for gene_record in gene_records:
            try:
                # Insert or update gene record
                insert_query = f"""
                INSERT INTO {gene_master_table} (
                    gene_id, ensembl_gene_id, hgnc_gene_id, ncbi_gene_id, 
                    gene_symbol, gene_symbol_aliases, gene_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (gene_id) DO UPDATE SET
                    ensembl_gene_id = EXCLUDED.ensembl_gene_id,
                    hgnc_gene_id = EXCLUDED.hgnc_gene_id,
                    ncbi_gene_id = EXCLUDED.ncbi_gene_id,
                    gene_symbol = EXCLUDED.gene_symbol,
                    gene_symbol_aliases = EXCLUDED.gene_symbol_aliases,
                    gene_name = EXCLUDED.gene_name,
                    updated_at = now()
                """
                
                cursor.execute(insert_query, (
                    gene_record['gene_id'],
                    gene_record['ensembl_gene_id'],
                    gene_record['hgnc_gene_id'],
                    gene_record['ncbi_gene_id'],
                    gene_record['gene_symbol'],
                    gene_record['gene_symbol_aliases'],
                    gene_record['gene_name']
                ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"    ✗ Error inserting {gene_record.get('gene_symbol', 'Unknown')}: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"✓ Inserted/updated {inserted_count} gene records in gene_master table")
        return inserted_count
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ Error populating gene_master table: {e}")
        raise
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def fetch_gene_master_data_from_db() -> List[Dict[str, Any]]:
    """
    Fetch gene master data from the gene_master table for export.
    
    Returns:
        List of dictionaries containing gene master data
    """
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn, cursor = connect_to_database()
        
        # Load database configuration to get table names
        db_config = load_database_config()
        tables = db_config.get('tables', {})
        gene_master_table = tables.get('gene_master', 'gene_master')
        
        # Query to fetch all gene master data
        query = f"""
        SELECT 
            gene_id,
            ensembl_gene_id,
            hgnc_gene_id,
            ncbi_gene_id,
            gene_symbol,
            gene_symbol_aliases,
            gene_name
        FROM {gene_master_table}
        ORDER BY gene_id
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        gene_data = []
        for row in rows:
            gene_record = {
                'gene_id': row[0],
                'ensembl_gene_id': row[1],
                'hgnc_gene_id': row[2],
                'ncbi_gene_id': row[3],
                'gene_symbol': row[4],
                'gene_symbol_aliases': row[5] if isinstance(row[5], str) else str(row[5]),
                'gene_name': row[6]
            }
            gene_data.append(gene_record)
        
        print(f"✓ Fetched {len(gene_data)} gene records from gene_master table")
        return gene_data
        
    except Exception as e:
        print(f"✗ Error fetching gene master data: {e}")
        raise
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def export_gene_master_csv(gene_data: List[Dict[str, Any]], output_file: str = "gene_master.csv") -> None:
    """
    Export gene master data to CSV file.
    
    Args:
        gene_data: List of gene dictionaries
        output_file: Output CSV filename
    """
    if not gene_data:
        print("No gene data to export")
        return
    
    # Define column order
    columns = [
        'gene_id',
        'ensembl_gene_id', 
        'hgnc_gene_id',
        'ncbi_gene_id',
        'gene_symbol',
        'gene_symbol_aliases',
        'gene_name'
    ]
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for gene in gene_data:
                # Convert gene_symbol_aliases to string if it's JSONB
                if isinstance(gene.get('gene_symbol_aliases'), (list, dict)):
                    gene['gene_symbol_aliases'] = str(gene['gene_symbol_aliases'])
                writer.writerow(gene)
        
        print(f"✓ Exported {len(gene_data)} gene records to {output_file}")
        
    except Exception as e:
        print(f"✗ Error exporting to CSV: {e}")
        raise


def main():
    """Main function to fetch comprehensive gene data and populate gene_master table."""
    print("=" * 60)
    print("Gene Master Data Extractor and Populator")
    print("=" * 60)
    
    try:
        # Load protein symbols from config
        print("\n[1/4] Loading protein symbols from config...")
        protein_symbols = load_proteins_from_config()
        
        if not protein_symbols:
            print("No protein symbols found in config file")
            return
        
        print(f"Found {len(protein_symbols)} protein symbols: {', '.join(protein_symbols)}")
        
        # Fetch comprehensive gene data from external sources
        print(f"\n[2/4] Fetching comprehensive gene data from external sources...")
        print("Sources: HGNC, Ensembl, NCBI")
        
        gene_records = []
        for symbol in protein_symbols:
            gene_record = fetch_comprehensive_gene_data(symbol)
            if gene_record:
                gene_records.append(gene_record)
        
        if not gene_records:
            print("No gene data successfully fetched")
            return
        
        # Populate gene_master table
        print(f"\n[3/4] Populating gene_master table...")
        inserted_count = populate_gene_master_table(gene_records)
        
        # Fetch and export data
        print(f"\n[4/4] Exporting gene master data to CSV...")
        gene_data = fetch_gene_master_data_from_db()
        
        if gene_data:
            output_file = "gene_master.csv"
            export_gene_master_csv(gene_data, output_file)
            
            print(f"\n✓ Gene master data processing completed!")
            print(f"  Processed symbols: {len(protein_symbols)}")
            print(f"  Successfully fetched: {len(gene_records)}")
            print(f"  Database records: {len(gene_data)}")
            print(f"  Output file: {output_file}")
        else:
            print("No gene data found in database for export")
        
    except Exception as e:
        print(f"\n✗ Error in gene master processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
