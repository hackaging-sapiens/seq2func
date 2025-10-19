"""
Load CSV data into PostgreSQL database.

This script:
1. Creates database schema (genes and papers tables)
2. Loads gene_mappings.csv into genes table
3. Loads all_genes_results.csv into papers table

Usage:
    python src/database/load_data.py --all
    python src/database/load_data.py --init-schema
    python src/database/load_data.py --load-genes
    python src/database/load_data.py --load-results
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SCHEMA


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)


def init_schema():
    """Initialize database schema from SQL file."""
    print("="*80)
    print("INITIALIZING DATABASE SCHEMA")
    print("="*80)

    schema_file = Path(__file__).parent / "schema.sql"

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Read and execute schema SQL
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()

        print(f"✓ Schema created successfully in '{DB_SCHEMA}' schema")
        print(f"  - Created table: {DB_SCHEMA}.genes")
        print(f"  - Created table: {DB_SCHEMA}.papers")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False


def load_genes(csv_file="data/gene_mappings.csv"):
    """Load genes from CSV into database."""
    print("\n" + "="*80)
    print("LOADING GENES FROM CSV")
    print("="*80)

    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False

    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} genes from {csv_file}")

        # Validate columns
        required_cols = ['symbol', 'name', 'entrez gene id', 'uniprot', 'why', 'include_reprogramming']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            return False

        # Clean data
        df['include_reprogramming'] = df['include_reprogramming'].map({'True': True, 'False': False, True: True, False: False})

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare data for insertion
        insert_query = f"""
            INSERT INTO {DB_SCHEMA}.genes (symbol, name, entrez_gene_id, uniprot, why, include_reprogramming)
            VALUES %s
            ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                entrez_gene_id = EXCLUDED.entrez_gene_id,
                uniprot = EXCLUDED.uniprot,
                why = EXCLUDED.why,
                include_reprogramming = EXCLUDED.include_reprogramming,
                updated_at = CURRENT_TIMESTAMP
        """

        # Convert DataFrame to list of tuples
        data = [
            (
                row['symbol'],
                row['name'],
                int(row['entrez gene id']) if pd.notna(row['entrez gene id']) else None,
                row['uniprot'] if pd.notna(row['uniprot']) else None,
                row['why'] if pd.notna(row['why']) else None,
                row['include_reprogramming']
            )
            for _, row in df.iterrows()
        ]

        # Execute bulk insert
        execute_values(cursor, insert_query, data)
        conn.commit()

        print(f"✓ Inserted/Updated {len(data)} genes in {DB_SCHEMA}.genes table")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error loading genes: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_results(csv_file="data/all_genes_results.csv"):
    """Load research papers from CSV into database."""
    print("\n" + "="*80)
    print("LOADING RESEARCH PAPERS FROM CSV")
    print("="*80)

    csv_path = Path(csv_file)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False

    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} papers from {csv_file}")

        # Validate columns
        required_cols = ['symbol', 'pmid', 'title', 'score', 'relevant']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            return False

        # Clean data
        df['relevant'] = df['relevant'].map({'True': True, 'False': False, True: True, False: False})

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare data for insertion
        insert_query = f"""
            INSERT INTO {DB_SCHEMA}.papers
            (symbol, pmid, title, year, journal, score, relevant, reasoning,
             modification_effects, longevity_association, search_date, url)
            VALUES %s
            ON CONFLICT (pmid, symbol) DO UPDATE SET
                title = EXCLUDED.title,
                year = EXCLUDED.year,
                journal = EXCLUDED.journal,
                score = EXCLUDED.score,
                relevant = EXCLUDED.relevant,
                reasoning = EXCLUDED.reasoning,
                modification_effects = EXCLUDED.modification_effects,
                longevity_association = EXCLUDED.longevity_association,
                search_date = EXCLUDED.search_date,
                url = EXCLUDED.url,
                updated_at = CURRENT_TIMESTAMP
        """

        # Convert DataFrame to list of tuples
        data = [
            (
                row['symbol'],
                str(row['pmid']),
                row['title'],
                int(row['year']) if pd.notna(row['year']) else None,
                row.get('journal', None),
                float(row['score']) if pd.notna(row['score']) else 0.0,
                row['relevant'],
                row.get('reasoning', None),
                row.get('modification_effects', 'Not specified'),
                row.get('longevity_association', 'Not specified'),
                pd.to_datetime(row['search_date']).date() if pd.notna(row.get('search_date')) else None,
                row.get('url', None)
            )
            for _, row in df.iterrows()
        ]

        # Execute bulk insert
        execute_values(cursor, insert_query, data)
        conn.commit()

        print(f"✓ Inserted/Updated {len(data)} papers in {DB_SCHEMA}.papers table")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error loading papers: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load CSV data into PostgreSQL database")
    parser.add_argument('--all', action='store_true', help='Initialize schema and load all data')
    parser.add_argument('--init-schema', action='store_true', help='Initialize database schema')
    parser.add_argument('--load-genes', action='store_true', help='Load genes from CSV')
    parser.add_argument('--load-results', action='store_true', help='Load research papers from CSV')
    parser.add_argument('--genes-file', default='data/gene_mappings.csv', help='Path to gene mappings CSV')
    parser.add_argument('--results-file', default='data/all_genes_results.csv', help='Path to results CSV')

    args = parser.parse_args()

    # If no arguments, show help
    if not any([args.all, args.init_schema, args.load_genes, args.load_results]):
        parser.print_help()
        return

    print(f"\n🔗 Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"📁 Schema: {DB_SCHEMA}\n")

    success = True

    if args.all or args.init_schema:
        if not init_schema():
            success = False

    if args.all or args.load_genes:
        if not load_genes(args.genes_file):
            success = False

    if args.all or args.load_results:
        if not load_results(args.results_file):
            success = False

    if success:
        print("\n" + "="*80)
        print("✅ ALL OPERATIONS COMPLETED SUCCESSFULLY")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ SOME OPERATIONS FAILED")
        print("="*80)


if __name__ == "__main__":
    main()
