"""
Database service layer for API operations.
"""
import os
import yaml
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_database_config(config_path: str = "config/config_database.yaml") -> Dict:
    """Load database configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
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
                'longevity_association': 'longevity_association'
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
    except Exception as e:
        print(f"Error loading database config: {e}")
        return {'schema': 'seq2func', 'tables': {}}


def get_db_connection():
    """Get database connection using same pattern as utils/database_operations.py."""
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
        conn = psycopg2.connect(**db_config)
        
        # Set schema from YAML config
        schema_name = db_yaml_config.get('schema')
        if schema_name and schema_name != 'public':
            with conn.cursor() as cursor:
                cursor.execute(f"SET search_path TO {schema_name}, public;")
        
        return conn
    except Exception as e:
        raise Exception(f"Database connection failed: {e}")


class DatabaseService:
    """Database service for API operations."""
    
    def __init__(self):
        config = load_database_config()
        self.schema = config.get('schema', 'seq2func')
        self.tables = config.get('tables', {})
    
    def get_all_genes(self) -> List[Dict[str, Any]]:
        """Get summary of all genes."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT 
                    g.gene_id,
                    g.gene_symbol,
                    g.hgnc_symbol as approved_symbol,
                    g.gene_name,
                    COALESCE(jsonb_array_length(g.gene_aliases), 0) as alias_count,
                    g.dna_sequence_length,
                    COUNT(DISTINCT p.protein_id) as protein_count,
                    COUNT(DISTINCT pt.ptm_uid) as ptm_count,
                    CASE WHEN la.gene_id IS NOT NULL THEN true ELSE false END as has_longevity_data
                FROM genes g
                LEFT JOIN proteins p ON g.gene_id = p.gene_id
                LEFT JOIN ptms pt ON p.protein_id = pt.protein_id
                LEFT JOIN longevity_association la ON g.gene_id = la.gene_id
                GROUP BY g.gene_id, g.gene_symbol, g.hgnc_symbol, g.gene_name, g.gene_aliases, g.dna_sequence_length, la.gene_id
                ORDER BY g.gene_symbol
                """
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
    
    def get_gene_by_id(self, gene_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed gene information by ID."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get gene basic info
                gene_query = """
                SELECT 
                    g.*,
                    la.confidence_level,
                    la.evidence,
                    la.comment
                FROM genes g
                LEFT JOIN longevity_association la ON g.gene_id = la.gene_id
                WHERE g.gene_id = %s
                """
                cursor.execute(gene_query, (gene_id,))
                gene_row = cursor.fetchone()
                
                if not gene_row:
                    return None
                
                gene_data = dict(gene_row)
                
                # Extract longevity data from evidence JSONB field
                if gene_data.get('evidence') and isinstance(gene_data['evidence'], dict):
                    evidence = gene_data['evidence']
                    gene_data['expression_change'] = evidence.get('expression_change')
                    gene_data['functional_clusters'] = evidence.get('functional_clusters', [])
                    gene_data['aging_mechanisms'] = evidence.get('aging_mechanisms', [])
                    gene_data['comment_causes'] = evidence.get('comment_causes', [])
                
                # Get proteins for this gene
                proteins_query = """
                SELECT 
                    p.protein_id,
                    p.protein_id as uniprot_id,
                    p.protein_name,
                    p.length as sequence_length,
                    p.protein_function as function,
                    p.protein_aliases
                FROM proteins p
                WHERE p.gene_id = %s
                """
                cursor.execute(proteins_query, (gene_id,))
                proteins = []
                
                for protein_row in cursor.fetchall():
                    protein_data = dict(protein_row)
                    protein_id = protein_data['protein_id']
                    
                    # Get PTMs for this protein
                    ptm_query = """
                    SELECT ptm_uid as ptm_id, modification_type, position, description, evidence, psi_mod_id
                    FROM ptms
                    WHERE protein_id = %s
                    ORDER BY position
                    """
                    cursor.execute(ptm_query, (protein_id,))
                    protein_data['ptms'] = [dict(row) for row in cursor.fetchall()]
                    
                    # Get domains for this protein (from protein_sequences table)
                    domain_query = """
                    SELECT interval_in_sequence 
                    FROM protein_sequences
                    WHERE protein_id = %s AND interval_in_sequence IS NOT NULL
                    """
                    cursor.execute(domain_query, (protein_id,))
                    domains = []
                    for row in cursor.fetchall():
                        intervals = row['interval_in_sequence']
                        if intervals and isinstance(intervals, list):
                            for i, interval in enumerate(intervals):
                                domains.append({
                                    'domain_id': f"{protein_id}_domain_{i}",
                                    'accession': interval.get('accession', ''),
                                    'name': interval.get('name', ''),
                                    'type': interval.get('type', ''),
                                    'start_position': interval.get('start'),
                                    'end_position': interval.get('end')
                                })
                    protein_data['domains'] = domains
                    
                    proteins.append(protein_data)
                
                gene_data['proteins'] = proteins
                return gene_data
    
    def get_gene_by_symbol(self, gene_symbol: str) -> Optional[Dict[str, Any]]:
        """Get gene by symbol (case-insensitive search)."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT gene_id FROM genes 
                WHERE LOWER(gene_symbol) = LOWER(%s) 
                   OR LOWER(hgnc_symbol) = LOWER(%s)
                   OR %s = ANY(SELECT LOWER(jsonb_array_elements_text(gene_aliases)))
                LIMIT 1
                """
                cursor.execute(query, (gene_symbol, gene_symbol, gene_symbol))
                result = cursor.fetchone()
                
                if result:
                    return self.get_gene_by_id(result['gene_id'])
                return None
    
    def search_genes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search genes by symbol or name."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                search_query = """
                SELECT DISTINCT ON (g.gene_id)
                    g.gene_id,
                    g.gene_symbol,
                    g.hgnc_symbol as approved_symbol,
                    g.gene_name
                FROM genes g
                WHERE 
                    LOWER(g.gene_symbol) LIKE LOWER(%s)
                    OR LOWER(g.hgnc_symbol) LIKE LOWER(%s)
                    OR LOWER(g.gene_name) LIKE LOWER(%s)
                    OR %s = ANY(SELECT LOWER(jsonb_array_elements_text(g.gene_aliases)))
                ORDER BY g.gene_id, g.gene_symbol
                LIMIT %s
                """
                search_term = f"%{query}%"
                cursor.execute(search_query, (search_term, search_term, search_term, query, limit))
                return [dict(row) for row in cursor.fetchall()]
    
    def get_all_proteins(self) -> List[Dict[str, Any]]:
        """Get summary of all proteins."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT 
                    p.protein_id,
                    p.protein_name,
                    g.gene_symbol,
                    p.length as sequence_length,
                    COUNT(DISTINCT pt.ptm_uid) as ptm_count,
                    COUNT(DISTINCT ps.protein_seq_id) as domain_count
                FROM proteins p
                LEFT JOIN genes g ON p.gene_id = g.gene_id
                LEFT JOIN ptms pt ON p.protein_id = pt.protein_id
                LEFT JOIN protein_sequences ps ON p.protein_id = ps.protein_id AND ps.interval_in_sequence IS NOT NULL
                GROUP BY p.protein_id, p.protein_name, g.gene_symbol, p.length
                ORDER BY p.protein_name
                """
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
    
    def get_protein_by_id(self, protein_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed protein information by ID."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get protein basic info
                protein_query = """
                SELECT 
                    p.*,
                    g.gene_symbol
                FROM proteins p
                LEFT JOIN genes g ON p.gene_id = g.gene_id
                WHERE p.protein_id = %s
                """
                cursor.execute(protein_query, (protein_id,))
                protein_row = cursor.fetchone()
                
                if not protein_row:
                    return None
                
                protein_data = dict(protein_row)
                
                # Get PTMs for this protein
                ptm_query = """
                SELECT ptm_uid as ptm_id, modification_type, position, description, evidence, psi_mod_id
                FROM ptms
                WHERE protein_id = %s
                ORDER BY position
                """
                cursor.execute(ptm_query, (protein_id,))
                protein_data['ptms'] = [dict(row) for row in cursor.fetchall()]
                
                # Get domains for this protein (from protein_sequences table)
                domain_query = """
                SELECT interval_in_sequence 
                FROM protein_sequences
                WHERE protein_id = %s AND interval_in_sequence IS NOT NULL
                """
                cursor.execute(domain_query, (protein_id,))
                domains = []
                for row in cursor.fetchall():
                    intervals = row['interval_in_sequence']
                    if intervals and isinstance(intervals, list):
                        for i, interval in enumerate(intervals):
                            domains.append({
                                'domain_id': f"{protein_id}_domain_{i}",
                                'accession': interval.get('accession', ''),
                                'name': interval.get('name', ''),
                                'type': interval.get('type', ''),
                                'start_position': interval.get('start'),
                                'end_position': interval.get('end')
                            })
                protein_data['domains'] = domains
                
                return protein_data
    
    def search_proteins(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search proteins by name or UniProt ID."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                search_query = """
                SELECT DISTINCT ON (p.protein_id)
                    p.protein_id,
                    p.protein_name,
                    g.gene_symbol
                FROM proteins p
                LEFT JOIN genes g ON p.gene_id = g.gene_id
                WHERE 
                    p.protein_id ILIKE %s
                    OR p.protein_name ILIKE %s
                    OR %s = ANY(SELECT jsonb_array_elements_text(p.protein_aliases))
                ORDER BY p.protein_id, p.protein_name
                LIMIT %s
                """
                search_term = f"%{query}%"
                cursor.execute(search_query, (search_term, search_term, query, limit))
                return [dict(row) for row in cursor.fetchall()]
    
    def get_proteins_by_gene_id(self, gene_id: str) -> List[Dict[str, Any]]:
        """Get all proteins for a specific gene."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get proteins for this gene
                proteins_query = """
                SELECT 
                    p.protein_id,
                    p.protein_id as uniprot_id,
                    p.protein_name,
                    p.length as sequence_length,
                    p.protein_function as function,
                    p.protein_aliases,
                    g.gene_symbol
                FROM proteins p
                LEFT JOIN genes g ON p.gene_id = g.gene_id
                WHERE p.gene_id = %s
                """
                cursor.execute(proteins_query, (gene_id,))
                proteins = []
                
                for protein_row in cursor.fetchall():
                    protein_data = dict(protein_row)
                    protein_id = protein_data['protein_id']
                    
                    # Get PTMs for this protein
                    ptm_query = """
                    SELECT ptm_uid as ptm_id, modification_type, position, description, evidence, psi_mod_id
                    FROM ptms
                    WHERE protein_id = %s
                    ORDER BY position
                    """
                    cursor.execute(ptm_query, (protein_id,))
                    protein_data['ptms'] = [dict(row) for row in cursor.fetchall()]
                    
                    # Get domains for this protein (from protein_sequences table)
                    domain_query = """
                    SELECT interval_in_sequence 
                    FROM protein_sequences
                    WHERE protein_id = %s AND interval_in_sequence IS NOT NULL
                    """
                    cursor.execute(domain_query, (protein_id,))
                    domains = []
                    for row in cursor.fetchall():
                        intervals = row['interval_in_sequence']
                        if intervals and isinstance(intervals, list):
                            for i, interval in enumerate(intervals):
                                domains.append({
                                    'domain_id': f"{protein_id}_domain_{i}",
                                    'accession': interval.get('accession', ''),
                                    'name': interval.get('name', ''),
                                    'type': interval.get('type', ''),
                                    'start_position': interval.get('start'),
                                    'end_position': interval.get('end')
                                })
                    protein_data['domains'] = domains
                    
                    proteins.append(protein_data)
                
                return proteins
    
    def get_protein_by_gene_symbol(self, gene_symbol: str) -> Optional[Dict[str, Any]]:
        """Get protein by gene symbol with associated gene information."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # First, find the gene by symbol
                gene_query = """
                SELECT gene_id FROM genes 
                WHERE LOWER(gene_symbol) = LOWER(%s) 
                   OR LOWER(hgnc_symbol) = LOWER(%s)
                   OR %s = ANY(SELECT LOWER(jsonb_array_elements_text(gene_aliases)))
                LIMIT 1
                """
                cursor.execute(gene_query, (gene_symbol, gene_symbol, gene_symbol))
                gene_result = cursor.fetchone()
                
                if not gene_result:
                    return None
                
                gene_id = gene_result['gene_id']
                
                # Get the first protein for this gene
                protein_query = """
                SELECT 
                    p.protein_id,
                    p.protein_id as uniprot_id,
                    p.protein_name,
                    p.length as sequence_length,
                    p.protein_function as function,
                    p.protein_aliases,
                    g.gene_symbol,
                    g.gene_id,
                    g.hgnc_symbol as approved_symbol,
                    g.gene_name,
                    g.hgnc_id,
                    g.ncbi_gene_id,
                    g.gene_aliases,
                    g.dna_sequence_length
                FROM proteins p
                LEFT JOIN genes g ON p.gene_id = g.gene_id
                WHERE p.gene_id = %s
                LIMIT 1
                """
                cursor.execute(protein_query, (gene_id,))
                protein_row = cursor.fetchone()
                
                if not protein_row:
                    return None
                
                protein_data = dict(protein_row)
                protein_id = protein_data['protein_id']
                
                # Get PTMs for this protein
                ptm_query = """
                SELECT ptm_uid as ptm_id, modification_type, position, description, evidence, psi_mod_id
                FROM ptms
                WHERE protein_id = %s
                ORDER BY position
                """
                cursor.execute(ptm_query, (protein_id,))
                protein_data['ptms'] = [dict(row) for row in cursor.fetchall()]
                
                # Get domains for this protein (from protein_sequences table)
                domain_query = """
                SELECT interval_in_sequence 
                FROM protein_sequences
                WHERE protein_id = %s AND interval_in_sequence IS NOT NULL
                """
                cursor.execute(domain_query, (protein_id,))
                domains = []
                for row in cursor.fetchall():
                    intervals = row['interval_in_sequence']
                    if intervals and isinstance(intervals, list):
                        for i, interval in enumerate(intervals):
                            domains.append({
                                'domain_id': f"{protein_id}_domain_{i}",
                                'accession': interval.get('accession', ''),
                                'name': interval.get('name', ''),
                                'type': interval.get('type', ''),
                                'start_position': interval.get('start'),
                                'end_position': interval.get('end')
                            })
                protein_data['domains'] = domains
                
                # Get longevity association data for the gene
                longevity_query = """
                SELECT 
                    la.confidence_level,
                    la.evidence,
                    la.comment
                FROM longevity_association la
                WHERE la.gene_id = %s
                """
                cursor.execute(longevity_query, (gene_id,))
                longevity_row = cursor.fetchone()
                
                if longevity_row:
                    longevity_data = dict(longevity_row)
                    # Extract longevity data from evidence JSONB field
                    if longevity_data.get('evidence') and isinstance(longevity_data['evidence'], dict):
                        evidence = longevity_data['evidence']
                        protein_data['expression_change'] = evidence.get('expression_change')
                        protein_data['functional_clusters'] = evidence.get('functional_clusters', [])
                        protein_data['aging_mechanisms'] = evidence.get('aging_mechanisms', [])
                        protein_data['comment_causes'] = evidence.get('comment_causes', [])
                    protein_data['confidence_level'] = longevity_data.get('confidence_level')
                
                return protein_data
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                stats_query = """
                SELECT 
                    (SELECT COUNT(*) FROM genes) as total_genes,
                    (SELECT COUNT(*) FROM proteins) as total_proteins,
                    (SELECT COUNT(*) FROM ptms) as total_ptms,
                    (SELECT COUNT(*) FROM protein_sequences WHERE interval_in_sequence IS NOT NULL) as total_domains,
                    (SELECT COUNT(*) FROM longevity_association) as genes_with_longevity
                """
                cursor.execute(stats_query)
                return dict(cursor.fetchone())
