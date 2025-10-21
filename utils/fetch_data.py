"""
Fetch biological data from multiple genomic and proteomic databases.

Includes functions to fetch data from:
- HGNC (gene nomenclature)
- Ensembl (DNA sequences)
- UniProt (protein data and PTMs)
- InterPro (protein domains)
- Open Genes (aging and longevity associations)
"""

import requests
import json


def fetch_hgnc_data(gene_symbol: str) -> tuple:
    """
    Fetch gene information from HGNC (HUGO Gene Nomenclature Committee).
    Searches by approved symbol first, then by alias/previous symbols if not found.
    
    Args:
        gene_symbol: Gene symbol (e.g., "NRF2" or "NFE2L2")
    
    Returns:
        Tuple of (hgnc_id, gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases)
        where gene_id is the NCBI Gene ID (Entrez ID) and gene_aliases is a list of alternative symbols
    """
    # Set headers to request JSON response
    headers = {"Accept": "application/json"}
    
    # Try searching by approved symbol first
    base_url = "https://rest.genenames.org/fetch/symbol"
    response = requests.get(f"{base_url}/{gene_symbol}", headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    # If not found by symbol, try searching by alias
    if data.get("response", {}).get("numFound", 0) == 0:
        base_url = "https://rest.genenames.org/fetch/alias_symbol"
        response = requests.get(f"{base_url}/{gene_symbol}", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # If still not found, try previous symbols
        if data.get("response", {}).get("numFound", 0) == 0:
            base_url = "https://rest.genenames.org/fetch/prev_symbol"
            response = requests.get(f"{base_url}/{gene_symbol}", headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # If still not found, raise error
            if data.get("response", {}).get("numFound", 0) == 0:
                raise ValueError(f"No gene found in HGNC for symbol: {gene_symbol}")
    
    # Extract the first (best) result
    doc = data["response"]["docs"][0]
    
    # Extract required fields
    hgnc_id = doc.get("hgnc_id", "N/A")
    gene_id = doc.get("entrez_id", "N/A")  # NCBI Gene ID (Entrez ID)
    ensembl_gene_id = doc.get("ensembl_gene_id", "N/A")  # Ensembl Gene ID
    approved_symbol = doc.get("symbol", "N/A")
    gene_name = doc.get("name", "N/A")
    
    # Extract gene aliases (alternative symbols)
    gene_aliases = []
    if "alias_symbol" in doc and doc["alias_symbol"]:
        gene_aliases.extend(doc["alias_symbol"] if isinstance(doc["alias_symbol"], list) else [doc["alias_symbol"]])
    if "prev_symbol" in doc and doc["prev_symbol"]:
        gene_aliases.extend(doc["prev_symbol"] if isinstance(doc["prev_symbol"], list) else [doc["prev_symbol"]])
    
    return hgnc_id, gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases


def fetch_ensembl_data(ensembl_gene_id: str) -> str:
    """
    Fetch DNA sequence from Ensembl given an Ensembl Gene ID.
    
    Args:
        ensembl_gene_id: Ensembl Gene ID (e.g., "ENSG00000116044")
    
    Returns:
        DNA sequence string
    """
    # Ensembl REST API endpoint
    server = "https://rest.ensembl.org"
    endpoint = f"/sequence/id/{ensembl_gene_id}"
    
    # Set headers to request JSON response
    headers = {"Content-Type": "application/json"}
    
    # Make request to Ensembl API
    response = requests.get(f"{server}{endpoint}", headers=headers)
    
    if response.status_code == 404:
        raise ValueError(f"Gene ID not found in Ensembl: {ensembl_gene_id}")
    
    response.raise_for_status()
    
    data = response.json()
    
    # Extract DNA sequence
    dna_sequence = data.get("seq", "N/A")
    
    return dna_sequence


def fetch_interpro_data(uniprot_id: str) -> list:
    """
    Fetch protein domain intervals from InterPro given a UniProt ID.
    
    Args:
        uniprot_id: UniProt accession ID (e.g., "Q16236")
    
    Returns:
        List of dictionaries containing domain information with keys:
        - 'accession': InterPro domain accession
        - 'name': Domain name
        - 'type': Domain type
        - 'start': Start position of the domain
        - 'end': End position of the domain
    """
    # InterPro REST API endpoint
    base_url = "https://www.ebi.ac.uk/interpro/api/entry/interpro/protein/uniprot"
    endpoint = f"{base_url}/{uniprot_id}/"
    
    # Make request to InterPro API
    response = requests.get(endpoint)
    
    if response.status_code == 404:
        raise ValueError(f"Protein not found in InterPro: {uniprot_id}")
    
    response.raise_for_status()
    
    data = response.json()
    
    # Extract domain intervals
    domains = []
    for entry in data.get("results", []):
        metadata = entry.get("metadata", {})
        entry_accession = metadata.get("accession", "N/A")
        entry_name = metadata.get("name", "N/A")
        entry_type = metadata.get("type", "N/A")
        
        # Get all proteins (should only be one for specific UniProt ID)
        for protein in entry.get("proteins", []):
            # Get all locations for this entry
            for location in protein.get("entry_protein_locations", []):
                for fragment in location.get("fragments", []):
                    domains.append({
                        "accession": entry_accession,
                        "name": entry_name,
                        "type": entry_type,
                        "start": fragment.get("start", "N/A"),
                        "end": fragment.get("end", "N/A")
                    })
    
    return domains


def fetch_opengenes_data(gene_symbol: str) -> dict:
    """
    Fetch longevity and aging association data from Open Genes database.
    
    Args:
        gene_symbol: Gene symbol (e.g., "NRF2" or "NFE2L2")
    
    Returns:
        Dictionary containing longevity and aging information with keys:
        - 'symbol': Gene symbol
        - 'name': Gene name
        - 'ncbi_id': NCBI/Entrez Gene ID
        - 'uniprot': UniProt ID
        - 'ensembl': Ensembl Gene ID
        - 'expression_change': Expression change in aging (increase/decrease)
        - 'confidence_level': Confidence level of aging association
        - 'functional_clusters': List of functional clusters
        - 'aging_mechanisms': List of aging mechanisms
        - 'comment_causes': Reasons for aging association
    """
    # Open Genes REST API endpoint
    base_url = "https://open-genes.com/api/gene"
    
    # Try with the gene symbol directly
    response = requests.get(f"{base_url}/{gene_symbol}")
    
    if response.status_code == 404:
        raise ValueError(f"Gene not found in Open Genes: {gene_symbol}")
    
    response.raise_for_status()
    
    data = response.json()
    
    # Extract relevant fields
    gene_data = {
        'symbol': data.get('symbol', 'N/A'),
        'name': data.get('name', 'N/A'),
        'ncbi_id': data.get('ncbiId', 'N/A'),
        'uniprot': data.get('uniprot', 'N/A'),
        'ensembl': data.get('ensembl', 'N/A'),
        'expression_change': data.get('expressionChange', 'N/A'),
        'confidence_level': data.get('confidenceLevel', {}).get('name', 'N/A'),
        'functional_clusters': [fc.get('name', 'N/A') for fc in data.get('functionalClusters', [])],
        'aging_mechanisms': [am.get('name', 'N/A') for am in data.get('agingMechanisms', [])],
        'comment_causes': [cc.get('name', 'N/A') for cc in data.get('commentCause', [])],
    }
    
    return gene_data


def fetch_uniprot_data(protein_symbol: str) -> tuple:
    """
    Fetch protein information from UniProt given a protein symbol.
    Prioritizes reviewed (Swiss-Prot) entries for high-quality annotations.
    
    Args:
        protein_symbol: Gene symbol (e.g., "NRF2")
    
    Returns:
        Tuple of (protein_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases)
        where:
        - ptm_data is a list of dictionaries containing PTM information
        - protein_aliases is a list of alternative protein names/short names
    """
    # UniProt REST API endpoint
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    
    # Search for the protein by gene name
    # IMPORTANT: Prioritize reviewed (Swiss-Prot) entries to get high-quality annotations including PTMs
    params = {
        "query": f"gene:{protein_symbol} AND organism_id:9606 AND reviewed:true",  # 9606 = Homo sapiens, reviewed = Swiss-Prot
        "format": "json",
        "size": 1  # Get the top result
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    if not data.get("results"):
        raise ValueError(f"No protein found for symbol: {protein_symbol}")
    
    # Extract the first (best) result
    entry = data["results"][0]
    
    # Extract required fields
    protein_id = entry.get("primaryAccession", "N/A")
    
    # Protein name (recommended name) and aliases
    protein_name = "N/A"
    protein_aliases = []
    
    if "proteinDescription" in entry:
        desc = entry["proteinDescription"]
        
        # Get recommended name
        if "recommendedName" in desc:
            recommended = desc["recommendedName"]
            protein_name = recommended.get("fullName", {}).get("value", "N/A")
            
            # Get short names from recommended name
            if "shortNames" in recommended:
                for short_name in recommended["shortNames"]:
                    alias = short_name.get("value")
                    if alias and alias not in protein_aliases:
                        protein_aliases.append(alias)
        
        # Get alternative names
        if "alternativeNames" in desc:
            for alt_name in desc["alternativeNames"]:
                if "fullName" in alt_name:
                    alias = alt_name["fullName"].get("value")
                    if alias and alias not in protein_aliases and alias != protein_name:
                        protein_aliases.append(alias)
                # Also check for short names in alternative names
                if "shortNames" in alt_name:
                    for short_name in alt_name["shortNames"]:
                        alias = short_name.get("value")
                        if alias and alias not in protein_aliases:
                            protein_aliases.append(alias)
    
    # Protein sequence
    protein_sequence = entry.get("sequence", {}).get("value", "N/A")
    
    # Protein function (from comments)
    protein_function = "N/A"
    if "comments" in entry:
        for comment in entry["comments"]:
            if comment.get("commentType") == "FUNCTION":
                # Extract function text
                texts = comment.get("texts", [])
                if texts:
                    protein_function = texts[0].get("value", "N/A")
                break
    
    # Extract Post-Translational Modifications (PTMs)
    # Include all PTM-related feature types from UniProt
    PTM_FEATURE_TYPES = [
        "Modified residue",      # Phosphorylation, methylation, acetylation, etc.
        "Glycosylation",         # N-linked, O-linked glycosylation
        "Lipidation",            # Palmitoylation, myristoylation, etc.
        "Cross-link",            # Disulfide bonds, other cross-links
        "Disulfide bond"         # Cysteine bridges
    ]
    
    ptm_data = []
    if "features" in entry:
        for feature in entry["features"]:
            feature_type = feature.get("type")
            if feature_type in PTM_FEATURE_TYPES:
                location = feature.get("location", {})
                position = location.get("start", {}).get("value", "N/A")
                description = feature.get("description", "N/A")
                
                # Extract evidence sources
                evidences = []
                for evidence in feature.get("evidences", []):
                    evidence_code = evidence.get("evidenceCode", "")
                    source = evidence.get("source", "")
                    ref_id = evidence.get("id", "")
                    evidences.append(f"{source}:{ref_id}" if ref_id else source)
                
                ptm_data.append({
                    "type": description.split(";")[0] if ";" in description else description,
                    "position": position,
                    "description": description,
                    "evidence": ", ".join(evidences) if evidences else "N/A"
                })
    
    return protein_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases


def fetch_refseq_data(ncbi_gene_id: str) -> tuple:
    """
    Fetch RefSeq IDs from NCBI using the NCBI Gene ID.
    
    Args:
        ncbi_gene_id: NCBI Gene ID (Entrez ID)
    
    Returns:
        Tuple of (refseq_mrna_id, refseq_protein_id) where both can be None if not found
    """
    if not ncbi_gene_id or ncbi_gene_id == "N/A":
        return None, None
    
    try:
        # NCBI E-utilities API endpoints
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
        # First, get the gene summary to find RefSeq IDs
        esummary_url = f"{base_url}/esummary.fcgi"
        params = {
            "db": "gene",
            "id": ncbi_gene_id,
            "retmode": "json"
        }
        
        response = requests.get(esummary_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "result" not in data or ncbi_gene_id not in data["result"]:
            return None, None
        
        gene_info = data["result"][ncbi_gene_id]
        
        # Extract RefSeq mRNA and protein IDs from the summary
        refseq_mrna_id = None
        refseq_protein_id = None
        
        # Look for RefSeq IDs in various fields
        for field_name, field_value in gene_info.items():
            if isinstance(field_value, str) and "refseq" in field_value.lower():
                # Try to extract RefSeq IDs from the field value
                if "NM_" in field_value:
                    # Extract the first RefSeq mRNA ID
                    import re
                    match = re.search(r'NM_\d+\.\d+', field_value)
                    if match:
                        refseq_mrna_id = match.group()
                if "NP_" in field_value:
                    # Extract the first RefSeq protein ID
                    import re
                    match = re.search(r'NP_\d+\.\d+', field_value)
                    if match:
                        refseq_protein_id = match.group()
        
        return refseq_mrna_id, refseq_protein_id
        
    except Exception as e:
        print(f"Warning: Could not fetch RefSeq data for NCBI Gene ID {ncbi_gene_id}: {e}")
        return None, None


def fetch_ensembl_protein_id(uniprot_id: str) -> str:
    """
    Fetch Ensembl protein ID from UniProt using the UniProt ID.
    
    Args:
        uniprot_id: UniProt accession ID
    
    Returns:
        Ensembl protein ID or None if not found
    """
    if not uniprot_id or uniprot_id == "N/A":
        return None
    
    try:
        # UniProt REST API to get database cross-references - use the full entry
        base_url = "https://rest.uniprot.org/uniprotkb"
        endpoint = f"{base_url}/{uniprot_id}"
        
        params = {
            "format": "json"
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract Ensembl protein ID from cross-references
        if "uniProtKBCrossReferences" in data:
            for xref in data["uniProtKBCrossReferences"]:
                # Check if xref is a dictionary and has the right database
                if isinstance(xref, dict):
                    database_info = xref.get("database")
                    if isinstance(database_info, dict) and database_info.get("id") == "Ensembl":
                        properties = xref.get("properties", [])
                        for prop in properties:
                            if isinstance(prop, dict) and prop.get("key") == "ProteinId":
                                return prop.get("value")
        
        return None
        
    except Exception as e:
        print(f"Warning: Could not fetch Ensembl protein ID for UniProt ID {uniprot_id}: {e}")
        return None


def fetch_ensembl_transcript_data(ensembl_gene_id: str) -> list:
    """
    Fetch transcript information from Ensembl given an Ensembl Gene ID.
    
    Args:
        ensembl_gene_id: Ensembl Gene ID (e.g., "ENSG00000116044")
    
    Returns:
        List of dictionaries containing transcript information with keys:
        - 'transcript_id': Ensembl transcript ID
        - 'translation_id': Ensembl protein ID (if available)
        - 'biotype': Transcript biotype
        - 'is_canonical': Whether this is the canonical transcript
    """
    if not ensembl_gene_id or ensembl_gene_id == "N/A":
        return []
    
    try:
        # Use Ensembl REST API overlap endpoint to get transcripts
        server = "https://rest.ensembl.org"
        endpoint = f"/overlap/id/{ensembl_gene_id}"
        
        params = {
            'feature': 'transcript',
            'format': 'condensed'
        }
        
        headers = {"Accept": "application/json"}
        
        # Make request to Ensembl API
        response = requests.get(f"{server}{endpoint}", headers=headers, params=params)
        
        if response.status_code == 404:
            raise ValueError(f"Gene ID not found in Ensembl: {ensembl_gene_id}")
        
        if response.status_code != 200:
            # If we can't fetch transcript data, return empty list gracefully
            print(f"    Warning: Could not fetch transcript data (status {response.status_code})")
            return []
        
        response.raise_for_status()
        data = response.json()
        
        transcripts = []
        
        # Extract transcript information
        if isinstance(data, list):
            for transcript_data in data:
                if isinstance(transcript_data, dict) and transcript_data.get('id', '').startswith('ENST'):
                    transcript_info = {
                        'transcript_id': transcript_data.get('id'),
                        'translation_id': None,  # Will be fetched separately if needed
                        'biotype': transcript_data.get('biotype', 'unknown'),
                        'is_canonical': transcript_data.get('canonical', False)
                    }
                    
                    # Try to get translation ID if available
                    # This might need an additional API call for each transcript
                    transcripts.append(transcript_info)
        
        return transcripts
        
    except Exception as e:
        print(f"Warning: Could not fetch Ensembl transcript data for {ensembl_gene_id}: {e}")
        return []


def fetch_refseq_transcript_ids(ncbi_gene_id: str) -> list:
    """
    Fetch RefSeq transcript IDs from NCBI using the NCBI Gene ID.
    
    Args:
        ncbi_gene_id: NCBI Gene ID (Entrez ID)
    
    Returns:
        List of RefSeq transcript IDs (NM_ format)
    """
    if not ncbi_gene_id or ncbi_gene_id == "N/A":
        return []
    
    try:
        # NCBI E-utilities API endpoints
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
        # First, get the gene summary to find RefSeq IDs
        esummary_url = f"{base_url}/esummary.fcgi"
        params = {
            "db": "gene",
            "id": ncbi_gene_id,
            "retmode": "json"
        }
        
        response = requests.get(esummary_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if "result" not in data or ncbi_gene_id not in data["result"]:
            return []
        
        gene_info = data["result"][ncbi_gene_id]
        
        # Extract RefSeq transcript IDs from various fields
        refseq_transcript_ids = []
        import re
        
        # Look for RefSeq mRNA IDs in various fields
        for field_name, field_value in gene_info.items():
            if isinstance(field_value, str):
                # Extract all RefSeq transcript IDs (NM_ format)
                matches = re.findall(r'NM_\d+\.\d+', field_value)
                refseq_transcript_ids.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_transcripts = []
        for transcript_id in refseq_transcript_ids:
            if transcript_id not in seen:
                seen.add(transcript_id)
                unique_transcripts.append(transcript_id)
        
        return unique_transcripts
        
    except Exception as e:
        print(f"Warning: Could not fetch RefSeq transcript IDs for NCBI Gene ID {ncbi_gene_id}: {e}")
        return []


def main():
    """Main function to demonstrate usage."""
    gene_symbol = "NRF2"
    
    print(f"Fetching data for gene symbol: {gene_symbol}")
    print("=" * 80)
    
    # Fetch HGNC data
    print("\n1. HGNC Data:")
    print("-" * 80)
    ensembl_gene_id = None
    try:
        hgnc_id, gene_id, ensembl_gene_id, approved_symbol, gene_name, gene_aliases = fetch_hgnc_data(gene_symbol)
        print(f"HGNC ID: {hgnc_id}")
        print(f"Gene ID (NCBI/Entrez): {gene_id}")
        print(f"Ensembl Gene ID: {ensembl_gene_id}")
        print(f"Approved Symbol: {approved_symbol}")
        print(f"Gene Name: {gene_name}")
        if gene_aliases:
            print(f"Gene Aliases: {gene_aliases}")
    except Exception as e:
        print(f"Error fetching HGNC data: {e}")
    
    # Fetch Ensembl data
    print("\n2. Ensembl Data:")
    print("-" * 80)
    if ensembl_gene_id and ensembl_gene_id != "N/A":
        try:
            dna_sequence = fetch_ensembl_data(ensembl_gene_id)
            print(f"DNA Sequence (length: {len(dna_sequence) if dna_sequence != 'N/A' else 0}):")
            print(dna_sequence[:100] + "..." if len(dna_sequence) > 100 else dna_sequence)
        except Exception as e:
            print(f"Error fetching Ensembl data: {e}")
    else:
        print("No Ensembl Gene ID available from HGNC data")
    
    # Fetch UniProt data
    print("\n3. UniProt Data:")
    print("-" * 80)
    protein_id = None
    ptm_data = []
    try:
        protein_id, protein_name, protein_sequence, protein_function, ptm_data, protein_aliases = fetch_uniprot_data(gene_symbol)
        
        print(f"Protein ID: {protein_id}")
        print(f"Protein Name: {protein_name}")
        if protein_aliases:
            print(f"Protein Aliases: {protein_aliases}")
        print(f"\nProtein Sequence (length: {len(protein_sequence) if protein_sequence != 'N/A' else 0}):")
        print(protein_sequence[:100] + "..." if len(protein_sequence) > 100 else protein_sequence)
        print(f"\nProtein Function:")
        print(protein_function[:500] + "..." if len(protein_function) > 500 else protein_function)
        
        # Display PTM data
        if ptm_data:
            print(f"\nPost-Translational Modifications: {len(ptm_data)} found")
        
    except Exception as e:
        print(f"Error fetching UniProt data: {e}")
    
    # Fetch InterPro data
    print("\n4. InterPro Data (Protein Domains):")
    print("-" * 80)
    if protein_id and protein_id != "N/A":
        try:
            domains = fetch_interpro_data(protein_id)
            if domains:
                print(f"Found {len(domains)} domain intervals:")
                for i, domain in enumerate(domains[:10], 1):  # Show first 10 domains
                    print(f"{i}. {domain['name']} ({domain['type']})")
                    print(f"   Accession: {domain['accession']}, Position: {domain['start']}-{domain['end']}")
                if len(domains) > 10:
                    print(f"   ... and {len(domains) - 10} more domains")
            else:
                print("No domain intervals found")
        except Exception as e:
            print(f"Error fetching InterPro data: {e}")
    else:
        print("No UniProt ID available from UniProt data")
    
    # Display Post-Translational Modifications from UniProt
    print("\n5. Post-Translational Modifications (from UniProt):")
    print("-" * 80)
    if ptm_data:
        print(f"Found {len(ptm_data)} modifications:")
        for i, ptm in enumerate(ptm_data[:15], 1):  # Show first 15 modifications
            print(f"{i}. {ptm['type']} at position {ptm['position']}")
            print(f"   Description: {ptm['description']}")
            print(f"   Evidence: {ptm['evidence']}")
        if len(ptm_data) > 15:
            print(f"\n   ... and {len(ptm_data) - 15} more modifications")
    else:
        print("No post-translational modification data found for this protein")
    
    # Fetch Open Genes longevity data
    print("\n6. Open Genes - Aging & Longevity Data:")
    print("-" * 80)
    try:
        # Try with the original gene symbol first, then with approved symbol if available
        try:
            opengenes_data = fetch_opengenes_data(gene_symbol)
        except ValueError:
            # If alias fails, try with approved symbol from HGNC
            if 'approved_symbol' in locals() and approved_symbol != gene_symbol:
                opengenes_data = fetch_opengenes_data(approved_symbol)
            else:
                raise
        
        print(f"Gene Symbol: {opengenes_data['symbol']}")
        print(f"Gene Name: {opengenes_data['name']}")
        print(f"NCBI ID: {opengenes_data['ncbi_id']}")
        print(f"\nExpression Change in Aging: {opengenes_data['expression_change']}")
        print(f"Confidence Level: {opengenes_data['confidence_level']}")
        
        if opengenes_data['functional_clusters']:
            print(f"\nFunctional Clusters:")
            for cluster in opengenes_data['functional_clusters'][:5]:
                print(f"  - {cluster}")
        
        if opengenes_data['aging_mechanisms']:
            print(f"\nAging Mechanisms:")
            for mechanism in opengenes_data['aging_mechanisms'][:5]:
                print(f"  - {mechanism}")
            if len(opengenes_data['aging_mechanisms']) > 5:
                print(f"  ... and {len(opengenes_data['aging_mechanisms']) - 5} more")
        
        if opengenes_data['comment_causes']:
            print(f"\nReasons for Aging Association:")
            for cause in opengenes_data['comment_causes'][:3]:
                print(f"  - {cause}")
    except ValueError as e:
        print(f"Gene not found in Open Genes database.")
        print("Note: Open Genes focuses on genes with established aging/longevity associations.")
    except Exception as e:
        print(f"Error fetching Open Genes data: {e}")


if __name__ == "__main__":
    main()

