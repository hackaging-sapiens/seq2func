"""
Protein-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from api.models import ProteinModel, PTMModel, ProteinDomain, ProteinSummary, ProteinWithGeneModel, LongevityAssociation, ErrorResponse
from api.database import DatabaseService

router = APIRouter(prefix="/api/proteins", tags=["proteins"])
db_service = DatabaseService()


@router.get("/", response_model=List[ProteinSummary])
async def get_all_proteins():
    """
    Get a summary list of all proteins in the database.
    
    Returns:
        List of protein summaries with basic information and counts.
    """
    try:
        proteins_data = db_service.get_all_proteins()
        
        protein_summaries = []
        for protein in proteins_data:
            summary = ProteinSummary(
                protein_id=protein['protein_id'],
                uniprot_id=protein['protein_id'],  # Same as protein_id in our schema
                protein_name=protein['protein_name'],
                gene_symbol=protein.get('gene_symbol', ''),
                sequence_length=protein.get('sequence_length', 0) or 0,
                ptm_count=protein.get('ptm_count', 0),
                domain_count=protein.get('domain_count', 0)
            )
            protein_summaries.append(summary)
        
        return protein_summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching proteins: {str(e)}")


@router.get("/search", response_model=List[ProteinSummary])
async def search_proteins(
    q: str = Query(..., description="Search query for protein name or UniProt ID"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Search for proteins by name or UniProt ID.
    
    Args:
        q: Search query
        limit: Maximum number of results (1-50)
    """
    try:
        if len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        search_results = db_service.search_proteins(q, limit)
        
        protein_summaries = []
        for protein in search_results:
            # For search results, get basic counts too
            protein_detail = db_service.get_protein_by_id(protein['protein_id'])
            if protein_detail:
                summary = ProteinSummary(
                    protein_id=protein['protein_id'],
                    uniprot_id=protein['protein_id'],
                    protein_name=protein['protein_name'],
                    gene_symbol=protein_detail.get('gene_symbol', ''),
                    sequence_length=protein_detail.get('sequence_length', 0),
                    ptm_count=len(protein_detail.get('ptms', [])),
                    domain_count=len(protein_detail.get('domains', []))
                )
                protein_summaries.append(summary)
        
        return protein_summaries
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching proteins: {str(e)}")


@router.get("/{protein_id}", response_model=ProteinModel)
async def get_protein_by_id(protein_id: str = Path(..., description="UniProt Protein ID")):
    """
    Get detailed information for a specific protein by ID.
    
    Args:
        protein_id: UniProt ID (e.g., Q16236)
    """
    try:
        protein_data = db_service.get_protein_by_id(protein_id)
        
        if not protein_data:
            raise HTTPException(status_code=404, detail=f"Protein with ID '{protein_id}' not found")
        
        # Convert database result to Pydantic model
        from api.models import PTMModel, ProteinDomain
        
        # Convert PTMs
        ptms = [PTMModel(**ptm) for ptm in protein_data.get('ptms', [])]
        
        # Convert domains
        domains = [ProteinDomain(**domain) for domain in protein_data.get('domains', [])]
        
        protein = ProteinModel(
            protein_id=protein_data['protein_id'],
            uniprot_id=protein_data['protein_id'],
            protein_name=protein_data['protein_name'],
            sequence_length=protein_data.get('sequence_length'),
            function=protein_data.get('function'),
            aliases=protein_data.get('protein_aliases', []),
            ptms=ptms,
            domains=domains
        )
        
        return protein
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching protein: {str(e)}")


@router.get("/uniprot/{uniprot_id}", response_model=ProteinModel)
async def get_protein_by_uniprot_id(uniprot_id: str = Path(..., description="UniProt accession ID")):
    """
    Get detailed information for a protein by UniProt ID.
    
    Args:
        uniprot_id: UniProt accession ID (e.g., Q16236)
    """
    try:
        protein_data = db_service.get_protein_by_id(uniprot_id)
        
        if not protein_data:
            raise HTTPException(status_code=404, detail=f"Protein with UniProt ID '{uniprot_id}' not found")
        
        # Reuse the same conversion logic as get_protein_by_id
        return await get_protein_by_id(uniprot_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching protein by UniProt ID: {str(e)}")


@router.get("/symbol/{symbol}", response_model=ProteinWithGeneModel)
async def get_protein_by_gene_symbol(symbol: str = Path(..., description="Gene symbol")):
    """
    Get detailed information for a protein by gene symbol.
    Returns comprehensive protein and gene information.
    
    Args:
        symbol: Gene symbol (e.g., NRF2, APOE)
    """
    try:
        protein_data = db_service.get_protein_by_gene_symbol(symbol)
        
        if not protein_data:
            raise HTTPException(status_code=404, detail=f"Protein not found for gene symbol '{symbol}'")
        
        # Convert PTMs
        ptms = [PTMModel(**ptm) for ptm in protein_data.get('ptms', [])]
        
        # Convert domains
        domains = [ProteinDomain(**domain) for domain in protein_data.get('domains', [])]
        
        # Convert longevity association
        longevity = None
        if protein_data.get('expression_change') is not None:
            longevity = LongevityAssociation(
                expression_change=protein_data.get('expression_change'),
                confidence_level=protein_data.get('confidence_level'),
                functional_clusters=protein_data.get('functional_clusters', []),
                aging_mechanisms=protein_data.get('aging_mechanisms', []),
                comment_causes=protein_data.get('comment_causes', [])
            )
        
        protein_with_gene = ProteinWithGeneModel(
            # Protein information
            protein_id=protein_data['protein_id'],
            uniprot_id=protein_data['protein_id'],
            protein_name=protein_data['protein_name'],
            sequence_length=protein_data.get('sequence_length'),
            function=protein_data.get('function'),
            aliases=protein_data.get('protein_aliases', []),
            ptms=ptms,
            domains=domains,
            # Gene information
            gene_id=protein_data['gene_id'],
            gene_symbol=protein_data['gene_symbol'],
            approved_symbol=protein_data.get('approved_symbol', protein_data['gene_symbol']),
            gene_name=protein_data['gene_name'],
            hgnc_id=protein_data.get('hgnc_id', ''),
            ncbi_gene_id=protein_data.get('ncbi_gene_id'),
            gene_aliases=protein_data.get('gene_aliases', []),
            dna_sequence_length=protein_data.get('dna_sequence_length'),
            longevity_association=longevity
        )
        
        return protein_with_gene
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching protein by gene symbol: {str(e)}")


@router.get("/gene/{gene_id}/proteins", response_model=List[ProteinModel])
async def get_proteins_by_gene_id(gene_id: str = Path(..., description="Ensembl Gene ID")):
    """
    Get all proteins for a specific gene.
    
    Args:
        gene_id: Ensembl Gene ID (e.g., ENSG00000116044)
    """
    try:
        proteins_data = db_service.get_proteins_by_gene_id(gene_id)
        
        if not proteins_data:
            raise HTTPException(status_code=404, detail=f"No proteins found for gene ID '{gene_id}'")
        
        protein_models = []
        for protein_data in proteins_data:
            # Convert PTMs
            ptms = [PTMModel(**ptm) for ptm in protein_data.get('ptms', [])]
            
            # Convert domains
            domains = [ProteinDomain(**domain) for domain in protein_data.get('domains', [])]
            
            protein = ProteinModel(
                protein_id=protein_data['protein_id'],
                uniprot_id=protein_data['protein_id'],
                protein_name=protein_data['protein_name'],
                sequence_length=protein_data.get('sequence_length'),
                function=protein_data.get('function'),
                aliases=protein_data.get('protein_aliases', []),
                ptms=ptms,
                domains=domains
            )
            protein_models.append(protein)
        
        return protein_models
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching proteins for gene: {str(e)}")
