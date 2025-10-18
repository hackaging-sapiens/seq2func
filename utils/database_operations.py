"""
Database operations for storing gene and protein data in PostgreSQL.

Functions:
- connect_to_database: Establish connection to PostgreSQL
- create_schema: Create all necessary tables
- insert_gene_data: Insert complete gene data into database
"""

import os
import yaml
import hashlib
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

# Load environment variables
load_dotenv()

# Import PSI-MOD mapping
try:
    from .psi_mod_mapping import get_psi_mod_id
except ImportError:
    try:
        from psi_mod_mapping import get_psi_mod_id
    except ImportError:
        # Fallback if mapping not available
        def get_psi_mod_id(mod_type: str) -> Optional[str]:
            return None


def load_database_config(config_path: str = "config/config_database.yaml") -> Dict:
    """
    Load database configuration from YAML file.
    
    Args:
        config_path: Path to the database configuration file
    
    Returns:
        Dictionary with database configuration
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Handle case where config is None or empty
        if config is None:
            config = {}
        
        db_config = config.get('database', {})
        
        # Set defaults
        default_config = {
            'schema': None,
            'tables': {
                'genes': 'genes',
                'proteins': 'proteins',
                'ptms': 'ptms',
                'dna_sequences': 'dna_sequences',
                'protein_sequences': 'protein_sequences',
                'longevity_association': 'longevity_association',
                'gene_master': 'gene_master',
                'protein_master': 'protein_master',
                'gene_transcript_protein': 'gene_transcript_protein'
            }
        }
        
        # Merge with defaults
        for key, value in default_config.items():
            if key not in db_config:
                db_config[key] = value
            elif key == 'tables':
                # Merge table names
                for table_key, table_value in value.items():
                    if table_key not in db_config[key]:
                        db_config[key][table_key] = table_value
        
        return db_config
        
    except FileNotFoundError:
        print(f"Warning: Database config file not found: {config_path}")
        print("Using default configuration...")
        return {
            'schema': None,
            'tables': {
                'genes': 'genes',
                'proteins': 'proteins',
                'ptms': 'ptms',
                'dna_sequences': 'dna_sequences',
                'protein_sequences': 'protein_sequences',
                'longevity_association': 'longevity_association',
                'gene_master': 'gene_master',
                'protein_master': 'protein_master',
                'gene_transcript_protein': 'gene_transcript_protein'
            }
        }
    except yaml.YAMLError as e:
        print(f"Error parsing database config YAML: {e}")
        raise
    except Exception as e:
        print(f"Error loading database configuration: {e}")
        raise


def connect_to_database() -> Tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
    """
    Connect to PostgreSQL database using credentials from .env file and config from YAML.
    
    Returns:
        Tuple of (connection, cursor)
    
    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        # Load database configuration from YAML
        db_yaml_config = load_database_config()
        
        # Get database credentials from environment (YAML can override)
        connection_config = db_yaml_config.get('connection') or {}
        db_config = {
            'host': connection_config.get('host') or os.getenv('DB_HOST', 'localhost'),
            'port': connection_config.get('port') or os.getenv('DB_PORT', '5432'),
            'database': connection_config.get('database') or os.getenv('DB_NAME'),
            'user': connection_config.get('user') or os.getenv('DB_USER'),
            'password': connection_config.get('password') or os.getenv('DB_PASSWORD'),
        }
        
        # Validate required credentials
        if not all([db_config['database'], db_config['user'], db_config['password']]):
            raise ValueError(
                "Missing required database credentials. "
                "Please set DB_NAME, DB_USER, and DB_PASSWORD in .env file "
                "or config/config_database.yaml"
            )
        
        # Establish connection
        print(f"Connecting to PostgreSQL database '{db_config['database']}' at {db_config['host']}:{db_config['port']}...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ Successfully connected to PostgreSQL")
        print(f"  Version: {version[0].split(',')[0]}")
        
        # Set schema from YAML config
        schema_name = db_yaml_config.get('schema')
        if schema_name and schema_name != 'public':
            cursor.execute(f"SET search_path TO {schema_name}, public;")
            print(f"  Schema: {schema_name}")
        
        return conn, cursor
        
    except psycopg2.Error as e:
        print(f"✗ Database connection error: {e}")
        raise
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def create_schema(conn: psycopg2.extensions.connection, cursor: psycopg2.extensions.cursor) -> None:
    """
    Create database schema (tables) for storing gene and protein data.
    
    Args:
        conn: Database connection
        cursor: Database cursor
    
    Raises:
        psycopg2.Error: If schema creation fails
    """
    try:
        print("\nCreating database schema...")
        
        # Load database configuration from YAML
        db_config = load_database_config()
        schema_name = db_config.get('schema')
        tables = db_config.get('tables', {})
        
        if schema_name and schema_name != 'public':
            # Create schema if it doesn't exist
            create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
            cursor.execute(create_schema_sql)
            print(f"  ✓ Created/verified schema: {schema_name}")
            
            # Set search path to use the schema
            cursor.execute(f"SET search_path TO {schema_name}, public;")
        else:
            print(f"  ✓ Using default schema: public")
        
        # Enable required extensions
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        print("  ✓ Enabled pgcrypto and uuid-ossp extensions")
        
        # Drop existing tables if they exist (for clean setup)
        table_prefix = f"{schema_name}." if schema_name and schema_name != 'public' else ""
        drop_tables = f"""
        DROP TABLE IF EXISTS {table_prefix}{tables['gene_transcript_protein']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['longevity_association']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['protein_sequences']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['dna_sequences']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['ptms']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['protein_master']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['gene_master']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['proteins']} CASCADE;
        DROP TABLE IF EXISTS {table_prefix}{tables['genes']} CASCADE;
        """
        cursor.execute(drop_tables)
        print("  - Dropped existing tables (if any)")
        
        # Create genes table (canonical + canonical DNA sequence)
        # Primary stable key: gene_id (Ensembl)
        create_genes_table = f"""
        CREATE TABLE IF NOT EXISTS {tables['genes']} (
            gene_id TEXT PRIMARY KEY,               -- Ensembl Gene ID, e.g. ENSG00000116044
            gene_symbol TEXT,                       -- human-friendly symbol (may be same as hgnc_symbol)
            gene_aliases JSONB DEFAULT '[]'::jsonb, -- synonyms/alternate symbols, e.g. ["NRF2","Nrf2"]
            gene_name TEXT,                         -- full descriptive gene name
            hgnc_symbol TEXT,                       -- HGNC-approved symbol (explicit)
            hgnc_id TEXT,                           -- HGNC identifier, e.g. "HGNC:7782"
            ncbi_gene_id INTEGER,                   -- NCBI Gene ID
            gene_biotype TEXT,                      -- e.g. "protein_coding"
            -- canonical (hybrid) dna sequence stored on the gene row
            dna_sequence TEXT,                      -- canonical nucleotide sequence (CDS/principal transcript)
            dna_sequence_type TEXT DEFAULT 'cds',   -- 'cds'|'genomic'|'mrna'
            dna_sequence_length INTEGER,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_genes_table)
        print(f"  ✓ Created '{tables['genes']}' table")
        
        # Create proteins table (canonical + canonical protein sequence)
        # Primary stable key: protein_id (UniProt)
        create_proteins_table = f"""
        CREATE TABLE IF NOT EXISTS {tables['proteins']} (
            protein_id TEXT PRIMARY KEY,            -- UniProt accession, e.g. Q16236
            protein_symbol TEXT,                    -- short protein symbol/alias (e.g. NRF2)
            protein_aliases JSONB DEFAULT '[]'::jsonb, -- alternative names/synonyms
            protein_name TEXT,                      -- UniProt recommended full name
            gene_id TEXT NOT NULL REFERENCES {tables['genes']}(gene_id) ON DELETE CASCADE,
            uniprot_entry_name TEXT,                -- e.g. NFE2L2_HUMAN
            protein_function TEXT,                  -- short function description
            length INTEGER,                         -- canonical length (aa)
            protein_sequence TEXT,                  -- canonical amino-acid sequence (single-letter codes)
            protein_sequence_length INTEGER,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_proteins_table)
        print(f"  ✓ Created '{tables['proteins']}' table")
        
        # Create ptms table
        # ptm_uid will be set by trigger on INSERT
        create_ptms_table = f"""
        CREATE TABLE {tables['ptms']} (
            ptm_uid TEXT PRIMARY KEY,               -- deterministic stable internal id (set by trigger)
            protein_id TEXT NOT NULL REFERENCES {tables['proteins']}(protein_id) ON DELETE CASCADE,
            modification_type TEXT NOT NULL,        -- e.g., 'Phosphorylation'
            psi_mod_id TEXT,                        -- e.g., 'MOD:00046' (PSI-MOD term) for type normalization
            position INTEGER,                       -- residue index (1-based) for site-specific PTMs
            start_position INTEGER,                 -- optional region start (for ranges)
            end_position INTEGER,                   -- optional region end (for ranges)
            interval_in_sequence JSONB,             -- flexible intervals [{{"type":"motif","start":x,"end":y}}]
            description TEXT,                       -- textual note
            evidence JSONB,                         -- structured evidence, e.g. {{"pmids":[1234],"source":"PhosphoSitePlus"}}
            modification_effects JSONB,             -- e.g., {{"activity":"increase","localization":"nuclear"}}
            source_site_id TEXT,                    -- optional external site id (e.g., PhosphoSitePlus ID)
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now(),
            UNIQUE (protein_id, modification_type, position)
        );
        """
        cursor.execute(create_ptms_table)
        print(f"  ✓ Created '{tables['ptms']}' table")
        
        # Create dna_sequences table (auxiliary: multiple transcripts / versions)
        create_dna_table = f"""
        CREATE TABLE {tables['dna_sequences']} (
            dna_id BIGSERIAL PRIMARY KEY,
            gene_id TEXT NOT NULL REFERENCES {tables['genes']}(gene_id) ON DELETE CASCADE,
            source TEXT NOT NULL DEFAULT 'Ensembl', -- e.g., 'Ensembl:release_110'
            transcript_id TEXT,                     -- e.g., ENST00000... if applicable
            sequence TEXT NOT NULL,                 -- nucleotide sequence (A/T/G/C)
            sequence_type TEXT DEFAULT 'cds',       -- 'cds' | 'genomic' | 'mrna'
            sequence_length INTEGER,
            checksum TEXT,                          -- optional (md5/sha256) for integrity
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_dna_table)
        print(f"  ✓ Created '{tables['dna_sequences']}' table")
        
        # Create unique index on dna_sequences to prevent duplicates
        create_dna_unique_idx = f"""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_dna_sequences_unique 
        ON {tables['dna_sequences']} (gene_id, source, COALESCE(transcript_id, ''));
        """
        cursor.execute(create_dna_unique_idx)
        print(f"  ✓ Created unique index on dna_sequences")
        
        # Create protein_sequences table (auxiliary: isoforms / versions)
        create_protein_seq_table = f"""
        CREATE TABLE {tables['protein_sequences']} (
            protein_seq_id BIGSERIAL PRIMARY KEY,
            protein_id TEXT NOT NULL REFERENCES {tables['proteins']}(protein_id) ON DELETE CASCADE,
            isoform TEXT,                           -- e.g., 'Isoform 1' or 'Q16236-1'
            source TEXT,                            -- e.g., 'UniProt', 'Ensembl', 'curation'
            sequence TEXT NOT NULL,                 -- amino-acid sequence
            sequence_length INTEGER,
            checksum TEXT,                          -- optional
            interval_in_sequence JSONB,             -- e.g., [{{"type":"domain","name":"bZIP","start":469,"end":559}}]
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now(),
            UNIQUE (protein_id, isoform)
        );
        """
        cursor.execute(create_protein_seq_table)
        print(f"  ✓ Created '{tables['protein_sequences']}' table")
        
        # Create longevity_association table
        create_longevity_table = f"""
        CREATE TABLE {tables['longevity_association']} (
            assoc_id BIGSERIAL PRIMARY KEY,
            gene_id TEXT REFERENCES {tables['genes']}(gene_id) ON DELETE SET NULL,
            protein_id TEXT REFERENCES {tables['proteins']}(protein_id) ON DELETE SET NULL,
            association TEXT,                       -- 'increased_lifespan', etc.
            confidence_level TEXT,                  -- 'high', 'medium', 'low'
            evidence JSONB,                         -- {{"pmids":[12345],"organism":"mouse"}}
            comment TEXT,
            source TEXT,                            -- 'OpenGenes', 'PMID:123456'
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_longevity_table)
        print(f"  ✓ Created '{tables['longevity_association']}' table")
        
        # Create gene_master table
        create_gene_master_table = f"""
        CREATE TABLE {tables['gene_master']} (
            gene_id TEXT PRIMARY KEY,               -- Ensembl Gene ID, same as ensembl_gene_id
            ensembl_gene_id TEXT NOT NULL,          -- Ensembl Gene ID (duplicate of gene_id for clarity)
            hgnc_gene_id TEXT,                      -- HGNC identifier, e.g. "HGNC:7782"
            ncbi_gene_id INTEGER,                   -- NCBI Gene ID
            gene_symbol TEXT,                       -- human-friendly symbol
            gene_symbol_aliases JSONB DEFAULT '[]'::jsonb, -- synonyms/alternate symbols
            gene_name TEXT,                         -- full descriptive gene name
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_gene_master_table)
        print(f"  ✓ Created '{tables['gene_master']}' table")
        
        # Create protein_master table
        create_protein_master_table = f"""
        CREATE TABLE {tables['protein_master']} (
            protein_id TEXT PRIMARY KEY,            -- UniProt accession, same as uniprot_protein_id
            uniprot_protein_id TEXT NOT NULL,       -- UniProt accession (duplicate of protein_id for clarity)
            ensembl_protein_id TEXT,                -- Ensembl Protein ID (when available)
            refseq_protein_id TEXT,                 -- RefSeq Protein ID (when available)
            protein_symbol TEXT,                    -- short protein symbol/alias
            protein_symbol_aliases JSONB DEFAULT '[]'::jsonb, -- alternative names/synonyms
            protein_name TEXT,                      -- UniProt recommended full name
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_protein_master_table)
        print(f"  ✓ Created '{tables['protein_master']}' table")
        
        # Create gene_transcript_protein table
        create_gene_transcript_protein_table = f"""
        CREATE TABLE {tables['gene_transcript_protein']} (
            id BIGSERIAL PRIMARY KEY,
            hgnc_gene_id TEXT,                         -- HGNC identifier, e.g. "HGNC:7782"
            ensembl_gene_id TEXT,                      -- Ensembl Gene ID
            gene_symbol TEXT,                          -- Gene symbol
            ensembl_transcript_id TEXT,                -- Ensembl transcript ID
            refseq_transcript_id TEXT,                 -- RefSeq transcript ID (NM_ format)
            uniprot_protein_id TEXT,                   -- UniProt accession
            ensembl_protein_id TEXT,                   -- Ensembl Protein ID
            protein_symbol TEXT,                       -- Protein symbol
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """
        cursor.execute(create_gene_transcript_protein_table)
        print(f"  ✓ Created '{tables['gene_transcript_protein']}' table")
        
        # Create indexes for faster queries
        indexes = [
            # Gene indexes
            f"CREATE INDEX IF NOT EXISTS idx_genes_gene_symbol ON {tables['genes']}(gene_symbol);",
            f"CREATE INDEX IF NOT EXISTS idx_genes_hgnc_symbol ON {tables['genes']}(hgnc_symbol);",
            f"CREATE INDEX IF NOT EXISTS idx_genes_hgnc_id ON {tables['genes']}(hgnc_id);",
            # Protein indexes
            f"CREATE INDEX IF NOT EXISTS idx_proteins_gene_id ON {tables['proteins']}(gene_id);",
            f"CREATE INDEX IF NOT EXISTS idx_proteins_symbol ON {tables['proteins']}(protein_symbol);",
            f"CREATE INDEX IF NOT EXISTS idx_proteins_entry_name ON {tables['proteins']}(uniprot_entry_name);",
            # PTM indexes
            f"CREATE INDEX IF NOT EXISTS idx_ptms_protein ON {tables['ptms']}(protein_id);",
            f"CREATE INDEX IF NOT EXISTS idx_ptms_type ON {tables['ptms']}(modification_type);",
            f"CREATE INDEX IF NOT EXISTS idx_ptms_position ON {tables['ptms']}(position);",
            # DNA sequences indexes
            f"CREATE INDEX IF NOT EXISTS idx_dna_sequences_gene ON {tables['dna_sequences']}(gene_id);",
            f"CREATE INDEX IF NOT EXISTS idx_dna_sequences_transcript ON {tables['dna_sequences']}(transcript_id);",
            # Protein sequences indexes
            f"CREATE INDEX IF NOT EXISTS idx_protseqs_protein ON {tables['protein_sequences']}(protein_id);",
            f"CREATE INDEX IF NOT EXISTS idx_protseqs_isoform ON {tables['protein_sequences']}(isoform);",
            # Longevity indexes
            f"CREATE INDEX IF NOT EXISTS idx_longevity_gene ON {tables['longevity_association']}(gene_id);",
            f"CREATE INDEX IF NOT EXISTS idx_longevity_protein ON {tables['longevity_association']}(protein_id);",
            # Gene master indexes
            f"CREATE INDEX IF NOT EXISTS idx_gene_master_symbol ON {tables['gene_master']}(gene_symbol);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_master_hgnc_id ON {tables['gene_master']}(hgnc_gene_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_master_ncbi_id ON {tables['gene_master']}(ncbi_gene_id);",
            # Protein master indexes
            f"CREATE INDEX IF NOT EXISTS idx_protein_master_symbol ON {tables['protein_master']}(protein_symbol);",
            f"CREATE INDEX IF NOT EXISTS idx_protein_master_ensembl_id ON {tables['protein_master']}(ensembl_protein_id);",
            f"CREATE INDEX IF NOT EXISTS idx_protein_master_refseq_id ON {tables['protein_master']}(refseq_protein_id);",
            # Gene transcript protein indexes
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_hgnc_id ON {tables['gene_transcript_protein']}(hgnc_gene_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_ensembl_gene_id ON {tables['gene_transcript_protein']}(ensembl_gene_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_gene_symbol ON {tables['gene_transcript_protein']}(gene_symbol);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_ensembl_transcript_id ON {tables['gene_transcript_protein']}(ensembl_transcript_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_refseq_transcript_id ON {tables['gene_transcript_protein']}(refseq_transcript_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_uniprot_id ON {tables['gene_transcript_protein']}(uniprot_protein_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_ensembl_protein_id ON {tables['gene_transcript_protein']}(ensembl_protein_id);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_transcript_protein_protein_symbol ON {tables['gene_transcript_protein']}(protein_symbol);",
        ]
        
        for index in indexes:
            cursor.execute(index)
        print("  ✓ Created B-tree indexes")
        
        # Create GIN indexes for JSONB fields (for efficient containment queries)
        gin_indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_genes_aliases_gin ON {tables['genes']} USING gin (gene_aliases);",
            f"CREATE INDEX IF NOT EXISTS idx_proteins_aliases_gin ON {tables['proteins']} USING gin (protein_aliases);",
            f"CREATE INDEX IF NOT EXISTS idx_gene_master_aliases_gin ON {tables['gene_master']} USING gin (gene_symbol_aliases);",
            f"CREATE INDEX IF NOT EXISTS idx_protein_master_aliases_gin ON {tables['protein_master']} USING gin (protein_symbol_aliases);",
        ]
        
        for index in gin_indexes:
            cursor.execute(index)
        print("  ✓ Created GIN indexes for JSONB fields")
        
        # Create auto-updated trigger function
        trigger_function = """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        cursor.execute(trigger_function)
        print("  ✓ Created set_updated_at() trigger function")
        
        # Create trigger function to set deterministic ptm_uid on INSERT
        ptm_uid_trigger_function = """
        CREATE OR REPLACE FUNCTION set_ptm_uid()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.ptm_uid IS NULL OR NEW.ptm_uid = '' THEN
                NEW.ptm_uid := encode(
                    digest(concat_ws('|', COALESCE(NEW.protein_id,''), COALESCE(NEW.modification_type,''), COALESCE(NEW.position::text,'')), 'sha1'),
                    'hex'
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        cursor.execute(ptm_uid_trigger_function)
        print("  ✓ Created set_ptm_uid() trigger function")
        
        # Drop existing triggers first, then create new ones
        drop_triggers = [
            f"DROP TRIGGER IF EXISTS trg_genes_set_updated ON {tables['genes']};",
            f"DROP TRIGGER IF EXISTS trg_proteins_set_updated ON {tables['proteins']};",
            f"DROP TRIGGER IF EXISTS trg_dna_sequences_updated ON {tables['dna_sequences']};",
            f"DROP TRIGGER IF EXISTS trg_protein_sequences_updated ON {tables['protein_sequences']};",
            f"DROP TRIGGER IF EXISTS trg_ptms_updated ON {tables['ptms']};",
            f"DROP TRIGGER IF EXISTS trg_longevity_updated ON {tables['longevity_association']};",
            f"DROP TRIGGER IF EXISTS trg_gene_master_updated ON {tables['gene_master']};",
            f"DROP TRIGGER IF EXISTS trg_protein_master_updated ON {tables['protein_master']};",
            f"DROP TRIGGER IF EXISTS trg_gene_transcript_protein_updated ON {tables['gene_transcript_protein']};",
            f"DROP TRIGGER IF EXISTS trg_ptms_set_uid ON {tables['ptms']};",
        ]
        
        for drop_trigger in drop_triggers:
            cursor.execute(drop_trigger)
        
        # Create triggers for all tables
        triggers = [
            f"CREATE TRIGGER trg_genes_set_updated BEFORE UPDATE ON {tables['genes']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_proteins_set_updated BEFORE UPDATE ON {tables['proteins']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_dna_sequences_updated BEFORE UPDATE ON {tables['dna_sequences']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_protein_sequences_updated BEFORE UPDATE ON {tables['protein_sequences']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_ptms_updated BEFORE UPDATE ON {tables['ptms']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_longevity_updated BEFORE UPDATE ON {tables['longevity_association']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_gene_master_updated BEFORE UPDATE ON {tables['gene_master']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_protein_master_updated BEFORE UPDATE ON {tables['protein_master']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_gene_transcript_protein_updated BEFORE UPDATE ON {tables['gene_transcript_protein']} FOR EACH ROW EXECUTE FUNCTION set_updated_at();",
            f"CREATE TRIGGER trg_ptms_set_uid BEFORE INSERT ON {tables['ptms']} FOR EACH ROW EXECUTE FUNCTION set_ptm_uid();",
        ]
        
        for trigger in triggers:
            cursor.execute(trigger)
        print("  ✓ Created updated_at and ptm_uid triggers")
        
        # Commit changes
        conn.commit()
        print("\n✓ Database schema created successfully!")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\n✗ Error creating schema: {e}")
        raise


def insert_gene_data(
    conn: psycopg2.extensions.connection,
    cursor: psycopg2.extensions.cursor,
    hgnc_data: Dict,
    dna_data: Optional[str] = None,
    protein_data: Optional[Tuple] = None,
    domain_data: Optional[List[Dict]] = None,
    aging_data: Optional[Dict] = None
) -> str:
    """
    Insert complete gene data into the database with new schema.
    
    Args:
        conn: Database connection
        cursor: Database cursor
        hgnc_data: Dictionary with keys: ensembl_gene_id, hgnc_id, approved_symbol, gene_id (ncbi), gene_name
        dna_data: DNA sequence string (optional)
        protein_data: Tuple of (uniprot_id, protein_name, protein_sequence, protein_function, ptm_data) (optional)
        domain_data: List of domain dictionaries with interval_in_sequence (optional)
        aging_data: Dictionary with aging/longevity data (optional)
    
    Returns:
        gene_id: Ensembl Gene ID (TEXT primary key)
    
    Raises:
        psycopg2.Error: If insertion fails
    """
    try:
        # Load database configuration
        db_config = load_database_config()
        tables = db_config.get('tables', {})
        
        ensembl_gene_id = hgnc_data.get('ensembl_gene_id')
        if not ensembl_gene_id or ensembl_gene_id == 'N/A':
            raise ValueError("Ensembl Gene ID is required as primary key")
        
        print(f"\nInserting data for gene: {hgnc_data.get('approved_symbol', 'Unknown')}")
        
        # 1. Insert gene data with canonical DNA sequence (hybrid design)
        # gene_aliases from HGNC API (alias_symbol + prev_symbol)
        gene_aliases = hgnc_data.get('gene_aliases', [])
        
        insert_gene_query = f"""
        INSERT INTO {tables['genes']} (
            gene_id, gene_symbol, gene_aliases, gene_name, hgnc_symbol, hgnc_id, ncbi_gene_id, gene_biotype,
            dna_sequence, dna_sequence_type, dna_sequence_length
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (gene_id) DO UPDATE SET
            gene_symbol = EXCLUDED.gene_symbol,
            gene_aliases = EXCLUDED.gene_aliases,
            gene_name = EXCLUDED.gene_name,
            hgnc_symbol = EXCLUDED.hgnc_symbol,
            hgnc_id = EXCLUDED.hgnc_id,
            ncbi_gene_id = EXCLUDED.ncbi_gene_id,
            gene_biotype = EXCLUDED.gene_biotype,
            dna_sequence = EXCLUDED.dna_sequence,
            dna_sequence_type = EXCLUDED.dna_sequence_type,
            dna_sequence_length = EXCLUDED.dna_sequence_length,
            updated_at = now()
        RETURNING gene_id;
        """
        
        cursor.execute(insert_gene_query, (
            ensembl_gene_id,                                    # gene_id (PK)
            hgnc_data.get('approved_symbol'),                   # gene_symbol (same as hgnc_symbol)
            Json(gene_aliases),                                 # gene_aliases (JSONB)
            hgnc_data.get('gene_name'),                        # gene_name
            hgnc_data.get('approved_symbol'),                   # hgnc_symbol
            hgnc_data.get('hgnc_id'),                          # hgnc_id
            hgnc_data.get('gene_id'),                          # ncbi_gene_id
            'protein_coding',                                   # gene_biotype (default)
            dna_data if dna_data and dna_data != 'N/A' else None,  # dna_sequence (canonical)
            'genomic' if dna_data and dna_data != 'N/A' else None,  # dna_sequence_type
            len(dna_data) if dna_data and dna_data != 'N/A' else None  # dna_sequence_length
        ))
        
        gene_id = cursor.fetchone()[0]
        if dna_data and dna_data != 'N/A':
            print(f"  ✓ Inserted gene with canonical DNA sequence (ID: {gene_id}, {len(dna_data)} bp)")
            
            # Also insert into dna_sequences auxiliary table
            # Calculate checksum for data integrity
            dna_checksum = hashlib.md5(dna_data.encode()).hexdigest()
            
            # Use DO NOTHING approach or check existence first
            # Since we can't use ON CONFLICT with functional index, check if exists
            check_dna_exists = f"""
            SELECT dna_id FROM {tables['dna_sequences']}
            WHERE gene_id = %s AND source = %s AND COALESCE(transcript_id, '') = %s;
            """
            cursor.execute(check_dna_exists, (gene_id, 'Ensembl', ''))
            existing_dna = cursor.fetchone()
            
            if existing_dna:
                # Update existing
                update_dna_aux_query = f"""
                UPDATE {tables['dna_sequences']}
                SET sequence = %s, sequence_length = %s, checksum = %s, updated_at = now()
                WHERE dna_id = %s;
                """
                cursor.execute(update_dna_aux_query, (
                    dna_data, len(dna_data), dna_checksum, existing_dna[0]
                ))
            else:
                # Insert new
                insert_dna_aux_query = f"""
                INSERT INTO {tables['dna_sequences']} (
                    gene_id, source, transcript_id, sequence, sequence_type, sequence_length, checksum
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_dna_aux_query, (
                    gene_id, 'Ensembl', None, dna_data, 'genomic', len(dna_data), dna_checksum
                ))
            
            print(f"  ✓ Inserted DNA sequence into auxiliary table (checksum: {dna_checksum[:8]}...)")
        else:
            print(f"  ✓ Inserted gene (ID: {gene_id})")
        
        # 2. Insert protein data with canonical protein sequence (hybrid design)
        uniprot_id = None
        if protein_data:
            uniprot_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases = protein_data
            
            # Generate entry name and protein symbol
            protein_symbol = hgnc_data.get('approved_symbol', 'UNKNOWN')
            uniprot_entry_name = f"{protein_symbol}_HUMAN"
            
            insert_protein_query = f"""
            INSERT INTO {tables['proteins']} (
                protein_id, protein_symbol, protein_aliases, protein_name, gene_id, 
                uniprot_entry_name, protein_function, length,
                protein_sequence, protein_sequence_length
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (protein_id) DO UPDATE SET
                protein_symbol = EXCLUDED.protein_symbol,
                protein_aliases = EXCLUDED.protein_aliases,
                protein_name = EXCLUDED.protein_name,
                uniprot_entry_name = EXCLUDED.uniprot_entry_name,
                protein_function = EXCLUDED.protein_function,
                length = EXCLUDED.length,
                protein_sequence = EXCLUDED.protein_sequence,
                protein_sequence_length = EXCLUDED.protein_sequence_length,
                updated_at = now()
            RETURNING protein_id;
            """
            cursor.execute(insert_protein_query, (
                uniprot_id,                                                      # protein_id (PK)
                protein_symbol,                                                  # protein_symbol
                Json(protein_aliases),                                           # protein_aliases (JSONB)
                protein_name,                                                    # protein_name
                gene_id,                                                         # gene_id (FK)
                uniprot_entry_name,                                              # uniprot_entry_name
                protein_function,                                                # protein_function
                len(protein_sequence) if protein_sequence and protein_sequence != 'N/A' else None,  # length
                protein_sequence if protein_sequence and protein_sequence != 'N/A' else None,        # protein_sequence (canonical)
                len(protein_sequence) if protein_sequence and protein_sequence != 'N/A' else None   # protein_sequence_length
            ))
            result_protein_id = cursor.fetchone()[0]
            if protein_sequence and protein_sequence != 'N/A':
                print(f"  ✓ Inserted protein with canonical sequence (ID: {result_protein_id}, {len(protein_sequence)} aa)")
            else:
                print(f"  ✓ Inserted protein (ID: {result_protein_id})")
            
            # Insert protein sequence into auxiliary table if we have domain data
            if protein_sequence and protein_sequence != 'N/A' and domain_data:
                # Convert domain_data to interval_in_sequence JSONB format
                intervals = []
                for domain in domain_data:
                    intervals.append({
                        'type': domain.get('type', 'domain'),
                        'name': domain.get('name'),
                        'accession': domain.get('accession'),
                        'start': domain.get('start'),
                        'end': domain.get('end')
                    })
                
                # Calculate checksum for protein sequence
                protein_checksum = hashlib.md5(protein_sequence.encode()).hexdigest()
                
                insert_protein_seq_query = f"""
                INSERT INTO {tables['protein_sequences']} (
                    protein_id, isoform, source, sequence, sequence_length, checksum, interval_in_sequence
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protein_id, isoform) DO UPDATE SET
                    sequence = EXCLUDED.sequence,
                    sequence_length = EXCLUDED.sequence_length,
                    checksum = EXCLUDED.checksum,
                    interval_in_sequence = EXCLUDED.interval_in_sequence,
                    updated_at = now();
                """
                cursor.execute(insert_protein_seq_query, (
                    uniprot_id,                          # protein_id (FK)
                    None,                                # isoform (NULL for canonical)
                    'UniProt',                           # source
                    protein_sequence,                    # sequence
                    len(protein_sequence),               # sequence_length
                    protein_checksum,                    # checksum (MD5)
                    Json(intervals) if intervals else None  # interval_in_sequence
                ))
                print(f"  ✓ Inserted protein sequence with {len(intervals)} domain intervals (checksum: {protein_checksum[:8]}...)")
            
            # Insert PTMs
            if ptm_data:
                insert_ptm_query = f"""
                INSERT INTO {tables['ptms']} (
                    ptm_uid, protein_id, modification_type, psi_mod_id, position, description, evidence
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (protein_id, modification_type, position) DO UPDATE SET
                    psi_mod_id = EXCLUDED.psi_mod_id,
                    description = EXCLUDED.description,
                    evidence = EXCLUDED.evidence,
                    updated_at = now();
                """
                for ptm in ptm_data:
                    # ptm_uid will be auto-generated by trigger if NULL
                    mod_type = ptm.get('type')
                    psi_mod_id = get_psi_mod_id(mod_type)
                    
                    evidence_json = {
                        'source': 'UniProt',
                        'evidence_code': ptm.get('evidence', '')
                    }
                    
                    cursor.execute(insert_ptm_query, (
                        None,                            # ptm_uid (trigger will generate)
                        uniprot_id,                      # protein_id (FK)
                        mod_type,                        # modification_type
                        psi_mod_id,                      # psi_mod_id
                        ptm.get('position'),             # position
                        ptm.get('description'),          # description
                        Json(evidence_json)              # evidence (JSONB)
                    ))
                
                # Count how many have PSI-MOD IDs
                mapped_count = sum(1 for ptm in ptm_data if get_psi_mod_id(ptm.get('type')))
                print(f"  ✓ Inserted {len(ptm_data)} PTMs ({mapped_count} with PSI-MOD IDs)")
        
        # 3. Insert longevity association if available
        if aging_data:
            evidence_json = {
                'expression_change': aging_data.get('expression_change'),
                'functional_clusters': aging_data.get('functional_clusters', []),
                'aging_mechanisms': aging_data.get('aging_mechanisms', []),
                'comment_causes': aging_data.get('comment_causes', [])
            }
            
            insert_longevity_query = f"""
            INSERT INTO {tables['longevity_association']} (
                gene_id, protein_id, association, confidence_level, evidence, comment, source
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_longevity_query, (
                gene_id,                                             # gene_id (FK)
                uniprot_id if uniprot_id else None,                 # protein_id (FK, optional)
                'longevity_associated',                              # association
                aging_data.get('confidence_level'),                  # confidence_level
                Json(evidence_json),                                 # evidence (JSONB)
                str(aging_data.get('comment_causes', [])),          # comment
                'Open Genes'                                         # source
            ))
            print(f"  ✓ Inserted longevity association")
        
        # Commit transaction
        conn.commit()
        print(f"\n✓ Successfully inserted all data for gene_id: {gene_id}")
        
        return gene_id
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"\n✗ Error inserting data: {e}")
        raise


def close_connection(conn: psycopg2.extensions.connection, cursor: psycopg2.extensions.cursor) -> None:
    """
    Close database connection and cursor.
    
    Args:
        conn: Database connection
        cursor: Database cursor
    """
    try:
        cursor.close()
        conn.close()
        print("\n✓ Database connection closed")
    except Exception as e:
        print(f"✗ Error closing connection: {e}")


def main():
    """Demo: Connect, create schema, and test the database."""
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn, cursor = connect_to_database()
        
        # Create schema
        create_schema(conn, cursor)
        
        print("\n" + "="*80)
        print("Database setup complete! Ready to store gene data.")
        print("="*80)
        
    except Exception as e:
        print(f"\nSetup failed: {e}")
    finally:
        if conn and cursor:
            close_connection(conn, cursor)


if __name__ == "__main__":
    main()

