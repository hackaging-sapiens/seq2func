"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class GeneAliase(BaseModel):
    """Gene alias model."""
    alias: str


class PTMModel(BaseModel):
    """Post-translational modification model."""
    ptm_id: str
    modification_type: str
    position: Optional[int] = None
    description: Optional[str] = None
    evidence: Optional[dict] = None
    psi_mod_id: Optional[str] = None


class ProteinDomain(BaseModel):
    """Protein domain model."""
    domain_id: str
    accession: str
    name: str
    type: str
    start_position: Optional[int] = None
    end_position: Optional[int] = None


class ProteinModel(BaseModel):
    """Protein model."""
    protein_id: str
    uniprot_id: str
    protein_name: str
    sequence_length: Optional[int] = None
    function: Optional[str] = None
    aliases: List[str] = []
    ptms: List[PTMModel] = []
    domains: List[ProteinDomain] = []


class LongevityAssociation(BaseModel):
    """Longevity association model."""
    expression_change: Optional[int] = None
    confidence_level: Optional[str] = None
    functional_clusters: List[str] = []
    aging_mechanisms: List[str] = []
    comment_causes: List[str] = []


class GeneModel(BaseModel):
    """Gene model."""
    gene_id: str
    gene_symbol: str
    approved_symbol: str
    gene_name: str
    hgnc_id: str
    ncbi_gene_id: Optional[int] = None
    aliases: List[str] = []
    dna_sequence_length: Optional[int] = None
    proteins: List[ProteinModel] = []
    longevity_association: Optional[LongevityAssociation] = None


class GeneSummary(BaseModel):
    """Gene summary for list views."""
    gene_id: str
    gene_symbol: str
    approved_symbol: str
    gene_name: str
    protein_count: int = 0
    ptm_count: int = 0
    has_longevity_data: bool = False


class ProteinSummary(BaseModel):
    """Protein summary for list views."""
    protein_id: str
    uniprot_id: str
    protein_name: str
    gene_symbol: str
    sequence_length: int = 0
    ptm_count: int = 0
    domain_count: int = 0


class ProteinWithGeneModel(BaseModel):
    """Protein model with associated gene information."""
    # Protein information
    protein_id: str
    uniprot_id: str
    protein_name: str
    sequence_length: Optional[int] = None
    function: Optional[str] = None
    aliases: List[str] = []
    ptms: List[PTMModel] = []
    domains: List[ProteinDomain] = []
    
    # Gene information
    gene_id: str
    gene_symbol: str
    approved_symbol: str
    gene_name: str
    hgnc_id: str
    ncbi_gene_id: Optional[int] = None
    gene_aliases: List[str] = []
    dna_sequence_length: Optional[int] = None
    longevity_association: Optional[LongevityAssociation] = None


class DatabaseStats(BaseModel):
    """Database statistics model."""
    total_genes: int
    total_proteins: int
    total_ptms: int
    total_domains: int
    genes_with_longevity: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int
