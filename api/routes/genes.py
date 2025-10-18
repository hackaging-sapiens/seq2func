"""
Gene-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from api.models import GeneModel, GeneSummary, ErrorResponse
from api.database import DatabaseService

router = APIRouter(prefix="/api/genes", tags=["genes"])
db_service = DatabaseService()


@router.get("/", response_model=List[GeneSummary])
async def get_all_genes():
    """
    Get a summary list of all genes in the database.
    
    Returns:
        List of gene summaries with basic information and counts.
    """
    try:
        genes_data = db_service.get_all_genes()
        
        gene_summaries = []
        for gene in genes_data:
            summary = GeneSummary(
                gene_id=gene['gene_id'],
                gene_symbol=gene['gene_symbol'],
                approved_symbol=gene['approved_symbol'],
                gene_name=gene['gene_name'],
                protein_count=gene['protein_count'],
                ptm_count=gene['ptm_count'],
                has_longevity_data=gene['has_longevity_data']
            )
            gene_summaries.append(summary)
        
        return gene_summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching genes: {str(e)}")


@router.get("/search", response_model=List[GeneSummary])
async def search_genes(
    q: str = Query(..., description="Search query for gene symbol or name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Search for genes by symbol or name.
    
    Args:
        q: Search query
        limit: Maximum number of results (1-50)
    """
    try:
        if len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        search_results = db_service.search_genes(q, limit)
        
        gene_summaries = []
        for gene in search_results:
            # For search results, get basic counts too
            gene_detail = db_service.get_gene_by_id(gene['gene_id'])
            if gene_detail:
                summary = GeneSummary(
                    gene_id=gene['gene_id'],
                    gene_symbol=gene['gene_symbol'],
                    approved_symbol=gene['approved_symbol'],
                    gene_name=gene['gene_name'],
                    protein_count=len(gene_detail.get('proteins', [])),
                    ptm_count=sum(len(p.get('ptms', [])) for p in gene_detail.get('proteins', [])),
                    has_longevity_data=gene_detail.get('expression_change') is not None
                )
                gene_summaries.append(summary)
        
        return gene_summaries
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching genes: {str(e)}")


@router.get("/{gene_id}", response_model=GeneModel)
async def get_gene_by_id(gene_id: str = Path(..., description="Ensembl Gene ID")):
    """
    Get detailed information for a specific gene by ID.
    
    Args:
        gene_id: Ensembl Gene ID (e.g., ENSG00000116044)
    """
    try:
        gene_data = db_service.get_gene_by_id(gene_id)
        
        if not gene_data:
            raise HTTPException(status_code=404, detail=f"Gene with ID '{gene_id}' not found")
        
        # Convert database result to Pydantic model
        from api.models import PTMModel, ProteinDomain, ProteinModel, LongevityAssociation
        
        proteins = []
        for protein_data in gene_data.get('proteins', []):
            # Convert PTMs
            ptms = [PTMModel(**ptm) for ptm in protein_data.get('ptms', [])]
            
            # Convert domains
            domains = [ProteinDomain(**domain) for domain in protein_data.get('domains', [])]
            
            protein = ProteinModel(
                protein_id=protein_data['protein_id'],
                uniprot_id=protein_data['uniprot_id'],
                protein_name=protein_data['protein_name'],
                sequence_length=protein_data.get('sequence_length'),
                function=protein_data.get('function'),
                aliases=protein_data.get('protein_aliases', []),
                ptms=ptms,
                domains=domains
            )
            proteins.append(protein)
        
        # Convert longevity association
        longevity = None
        if gene_data.get('expression_change') is not None:
            longevity = LongevityAssociation(
                expression_change=gene_data.get('expression_change'),
                confidence_level=gene_data.get('confidence_level'),
                functional_clusters=gene_data.get('functional_clusters', []),
                aging_mechanisms=gene_data.get('aging_mechanisms', []),
                comment_causes=gene_data.get('comment_causes', [])
            )
        
        gene = GeneModel(
            gene_id=gene_data['gene_id'],
            gene_symbol=gene_data['gene_symbol'],
            approved_symbol=gene_data.get('hgnc_symbol', gene_data['gene_symbol']),
            gene_name=gene_data['gene_name'],
            hgnc_id=gene_data.get('hgnc_id', ''),
            ncbi_gene_id=gene_data.get('ncbi_gene_id'),
            aliases=gene_data.get('gene_aliases', []),
            dna_sequence_length=gene_data.get('dna_sequence_length'),
            proteins=proteins,
            longevity_association=longevity
        )
        
        return gene
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching gene: {str(e)}")


@router.get("/symbol/{symbol}", response_model=GeneModel)
async def get_gene_by_symbol(symbol: str = Path(..., description="Gene symbol")):
    """
    Get detailed information for a gene by symbol.
    
    Args:
        symbol: Gene symbol (e.g., NRF2, APOE)
    """
    try:
        gene_data = db_service.get_gene_by_symbol(symbol)
        
        if not gene_data:
            raise HTTPException(status_code=404, detail=f"Gene with symbol '{symbol}' not found")
        
        # Reuse the same conversion logic as get_gene_by_id
        return await get_gene_by_id(gene_data['gene_id'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching gene by symbol: {str(e)}")
