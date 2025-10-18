"""
Gene Transcript Protein Data Extractor and Populator

This script fetches comprehensive gene-transcript-protein mapping data from multiple sources:
- Ensembl (gene and transcript IDs)
- HGNC (gene nomenclature)
- RefSeq (transcript IDs)
- UniProt (protein IDs and symbols)

Creates a mapping table with the following columns:
- hgnc_gene_id, ensembl_gene_id, gene_symbol
- ensembl_transcript_id, refseq_transcript_id
- uniprot_protein_id, ensembl_protein_id, protein_symbol

Usage:
    python utils/gene_transcript_protein.py
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path to import utils
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.database_operations import connect_to_database, load_database_config, close_connection
    from utils.fetch_data import (
        fetch_hgnc_data, fetch_uniprot_data, fetch_ensembl_protein_id,
        fetch_ensembl_transcript_data, fetch_refseq_transcript_ids
    )
except ImportError:
    # Fallback for direct execution
    from database_operations import connect_to_database, load_database_config, close_connection
    from fetch_data import (
        fetch_hgnc_data, fetch_uniprot_data, fetch_ensembl_protein_id,
        fetch_ensembl_transcript_data, fetch_refseq_transcript_ids
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


def fetch_comprehensive_gene_transcript_protein_data(gene_symbol: str) -> List[Dict[str, Any]]:
    """
    Fetch comprehensive gene-transcript-protein mapping data from multiple sources.
    
    Args:
        gene_symbol: Gene symbol to fetch data for
    
    Returns:
        List of dictionaries with gene-transcript-protein mapping data
    """
    try:
        print(f"  Fetching comprehensive mapping data for: {gene_symbol}")
        
        # 1. Fetch HGNC data (primary source for gene identifiers)
        try:
            hgnc_id, ncbi_gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases = fetch_hgnc_data(gene_symbol)
        except Exception as e:
            print(f"    ✗ Error fetching HGNC data for {gene_symbol}: {e}")
            return []
        
        if not ensembl_gene_id or ensembl_gene_id == "N/A":
            print(f"    ✗ No Ensembl Gene ID found for {gene_symbol}")
            return []
        
        print(f"    ✓ Found gene: {approved_symbol} ({ensembl_gene_id})")
        
        # 2. Fetch Ensembl transcript data
        ensembl_transcripts = []
        try:
            ensembl_transcripts = fetch_ensembl_transcript_data(ensembl_gene_id)
            print(f"    ✓ Found {len(ensembl_transcripts)} Ensembl transcripts")
        except Exception as e:
            print(f"    ⚠ Could not fetch Ensembl transcript data: {e}")
        
        # 3. Fetch RefSeq transcript IDs
        refseq_transcripts = []
        try:
            if ncbi_gene_id and ncbi_gene_id != "N/A":
                refseq_transcripts = fetch_refseq_transcript_ids(str(ncbi_gene_id))
                print(f"    ✓ Found {len(refseq_transcripts)} RefSeq transcripts")
            else:
                print(f"    ⚠ No NCBI Gene ID available for RefSeq lookup")
        except Exception as e:
            print(f"    ⚠ Could not fetch RefSeq transcript data: {e}")
        
        # 4. Fetch UniProt data (protein information)
        uniprot_protein_id = None
        protein_symbol = None
        try:
            uniprot_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases = fetch_uniprot_data(gene_symbol)
            if uniprot_id and uniprot_id != "N/A":
                uniprot_protein_id = uniprot_id
                protein_symbol = gene_symbol  # Use the input symbol as protein symbol
                print(f"    ✓ Found UniProt protein: {uniprot_id}")
        except Exception as e:
            print(f"    ⚠ Could not fetch UniProt data: {e}")
        
        # 5. Fetch Ensembl protein ID if we have UniProt ID
        ensembl_protein_id = None
        if uniprot_protein_id:
            try:
                ensembl_protein_id = fetch_ensembl_protein_id(uniprot_protein_id)
                if ensembl_protein_id:
                    print(f"    ✓ Found Ensembl protein ID: {ensembl_protein_id}")
            except Exception as e:
                print(f"    ⚠ Could not fetch Ensembl protein ID: {e}")
        
        # 6. Create mapping records
        mapping_records = []
        
        # If we have Ensembl transcripts, create records for each
        if ensembl_transcripts:
            for transcript in ensembl_transcripts:
                # Try to get the corresponding Ensembl protein ID from transcript
                transcript_protein_id = transcript.get('translation_id')
                if not transcript_protein_id:
                    # Fallback to the general Ensembl protein ID we found
                    transcript_protein_id = ensembl_protein_id
                
                # Find matching RefSeq transcript (if any)
                refseq_transcript_id = None
                if refseq_transcripts:
                    # For now, just use the first RefSeq transcript
                    # In a more sophisticated implementation, we could try to match by sequence
                    refseq_transcript_id = refseq_transcripts[0] if refseq_transcripts else None
                
                record = {
                    'hgnc_gene_id': hgnc_id,
                    'ensembl_gene_id': ensembl_gene_id,
                    'gene_symbol': approved_symbol or gene_symbol,
                    'ensembl_transcript_id': transcript.get('transcript_id'),
                    'refseq_transcript_id': refseq_transcript_id,
                    'uniprot_protein_id': uniprot_protein_id,
                    'ensembl_protein_id': transcript_protein_id,
                    'protein_symbol': protein_symbol
                }
                mapping_records.append(record)
        else:
            # If no Ensembl transcripts found, create a record with just the gene data
            record = {
                'hgnc_gene_id': hgnc_id,
                'ensembl_gene_id': ensembl_gene_id,
                'gene_symbol': approved_symbol or gene_symbol,
                'ensembl_transcript_id': None,
                'refseq_transcript_id': refseq_transcripts[0] if refseq_transcripts else None,
                'uniprot_protein_id': uniprot_protein_id,
                'ensembl_protein_id': ensembl_protein_id,
                'protein_symbol': protein_symbol
            }
            mapping_records.append(record)
        
        print(f"    ✓ Created {len(mapping_records)} mapping records")
        return mapping_records
        
    except Exception as e:
        print(f"    ✗ Error fetching data for {gene_symbol}: {e}")
        return []


def populate_gene_transcript_protein_table(mapping_records: List[Dict[str, Any]]) -> int:
    """
    Insert gene-transcript-protein mapping records into the database table.
    
    Args:
        mapping_records: List of mapping dictionaries to insert
    
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
        gene_transcript_protein_table = tables.get('gene_transcript_protein', 'gene_transcript_protein')
        
        inserted_count = 0
        
        for record in mapping_records:
            try:
                # Insert mapping record
                insert_query = f"""
                INSERT INTO {gene_transcript_protein_table} (
                    hgnc_gene_id, ensembl_gene_id, gene_symbol, ensembl_transcript_id,
                    refseq_transcript_id, uniprot_protein_id, ensembl_protein_id, protein_symbol
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """
                
                cursor.execute(insert_query, (
                    record.get('hgnc_gene_id'),
                    record.get('ensembl_gene_id'),
                    record.get('gene_symbol'),
                    record.get('ensembl_transcript_id'),
                    record.get('refseq_transcript_id'),
                    record.get('uniprot_protein_id'),
                    record.get('ensembl_protein_id'),
                    record.get('protein_symbol')
                ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"    ✗ Error inserting record for {record.get('gene_symbol', 'Unknown')}: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"✓ Inserted/updated {inserted_count} mapping records in gene_transcript_protein table")
        return inserted_count
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ Error populating gene_transcript_protein table: {e}")
        raise
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def fetch_gene_transcript_protein_data_from_db() -> List[Dict[str, Any]]:
    """
    Fetch gene-transcript-protein mapping data from the database.
    
    Returns:
        List of dictionaries containing mapping data
    """
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn, cursor = connect_to_database()
        
        # Load database configuration to get table names
        db_config = load_database_config()
        tables = db_config.get('tables', {})
        gene_transcript_protein_table = tables.get('gene_transcript_protein', 'gene_transcript_protein')
        
        # Query to fetch all mapping data
        query = f"""
        SELECT 
            id,
            hgnc_gene_id,
            ensembl_gene_id,
            gene_symbol,
            ensembl_transcript_id,
            refseq_transcript_id,
            uniprot_protein_id,
            ensembl_protein_id,
            protein_symbol,
            created_at
        FROM {gene_transcript_protein_table}
        ORDER BY gene_symbol, ensembl_transcript_id
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        mapping_data = []
        for row in rows:
            record = {
                'id': row[0],
                'hgnc_gene_id': row[1],
                'ensembl_gene_id': row[2],
                'gene_symbol': row[3],
                'ensembl_transcript_id': row[4],
                'refseq_transcript_id': row[5],
                'uniprot_protein_id': row[6],
                'ensembl_protein_id': row[7],
                'protein_symbol': row[8],
                'created_at': row[9]
            }
            mapping_data.append(record)
        
        print(f"✓ Fetched {len(mapping_data)} mapping records from gene_transcript_protein table")
        return mapping_data
        
    except Exception as e:
        print(f"✗ Error fetching mapping data: {e}")
        raise
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


def main():
    """Main function to fetch comprehensive gene-transcript-protein mapping data and populate the table."""
    print("=" * 80)
    print("Gene Transcript Protein Mapping Data Extractor and Populator")
    print("=" * 80)
    
    try:
        # Load protein symbols from config
        print("\n[1/4] Loading protein symbols from config...")
        protein_symbols = load_proteins_from_config()
        
        if not protein_symbols:
            print("No protein symbols found in config file")
            return
        
        print(f"Found {len(protein_symbols)} protein symbols: {', '.join(protein_symbols[:10])}{'...' if len(protein_symbols) > 10 else ''}")
        
        # Fetch comprehensive mapping data from external sources
        print(f"\n[2/4] Fetching comprehensive mapping data from external sources...")
        print("Sources: Ensembl, HGNC, RefSeq, UniProt")
        
        all_mapping_records = []
        for symbol in protein_symbols:
            mapping_records = fetch_comprehensive_gene_transcript_protein_data(symbol)
            all_mapping_records.extend(mapping_records)
        
        if not all_mapping_records:
            print("No mapping data successfully fetched")
            return
        
        print(f"\nTotal mapping records created: {len(all_mapping_records)}")
        
        # Populate gene_transcript_protein table
        print(f"\n[3/4] Populating gene_transcript_protein table...")
        inserted_count = populate_gene_transcript_protein_table(all_mapping_records)
        
        # Fetch and display summary
        print(f"\n[4/4] Fetching summary from database...")
        mapping_data = fetch_gene_transcript_protein_data_from_db()
        
        if mapping_data:
            print(f"\n✓ Gene-transcript-protein mapping processing completed!")
            print(f"  Processed symbols: {len(protein_symbols)}")
            print(f"  Mapping records created: {len(all_mapping_records)}")
            print(f"  Database records inserted: {inserted_count}")
            print(f"  Total records in database: {len(mapping_data)}")
            
            # Show sample of the data
            print(f"\nSample mapping records:")
            for i, record in enumerate(mapping_data[:5]):
                print(f"  {i+1}. {record['gene_symbol']} -> {record['ensembl_transcript_id']} -> {record['uniprot_protein_id']}")
        else:
            print("No mapping data found in database")
        
    except Exception as e:
        print(f"\n✗ Error in gene-transcript-protein mapping processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
