"""
PSI-MOD (Protein Modifications) ontology ID mapping.

Maps modification type descriptions to standardized PSI-MOD identifiers.
Reference: https://www.ebi.ac.uk/ols/ontologies/mod
"""

# Common PTM type to PSI-MOD ID mapping
PSI_MOD_MAPPING = {
    # Phosphorylation
    'Phosphoserine': 'MOD:00046',
    'Phosphothreonine': 'MOD:00047',
    'Phosphotyrosine': 'MOD:00048',
    'Phosphohistidine': 'MOD:00049',
    
    # Acetylation
    'N6-acetyllysine': 'MOD:00064',
    'N-acetylalanine': 'MOD:00058',
    'N-acetylserine': 'MOD:00060',
    'N-acetylthreonine': 'MOD:00061',
    'N-acetylmethionine': 'MOD:00058',
    
    # Methylation
    'N6-methyllysine': 'MOD:00085',
    'N6,N6-dimethyllysine': 'MOD:00084',
    'N6,N6,N6-trimethyllysine': 'MOD:00083',
    'Omega-N-methylarginine': 'MOD:00078',
    'N,N-dimethylarginine': 'MOD:00076',
    'Asymmetric dimethylarginine': 'MOD:00076',
    'N,N,N-trimethylarginine': 'MOD:00232',
    'S-methylcysteine': 'MOD:00239',
    
    # Ubiquitination
    'N6-ubiquitinyllysine': 'MOD:01148',
    'Glycyl lysine isopeptide (Lys-Gly) (interchain with G-Cter in ubiquitin)': 'MOD:01148',
    
    # SUMOylation
    'N6-sumoyllysine': 'MOD:01149',
    'Glycyl lysine isopeptide (Lys-Gly) (interchain with G-Cter in SUMO1)': 'MOD:01149',
    'Glycyl lysine isopeptide (Lys-Gly) (interchain with G-Cter in SUMO2)': 'MOD:01150',
    
    # Glycosylation
    'N-linked (GlcNAc...) asparagine': 'MOD:00006',
    'O-linked (GalNAc...) serine': 'MOD:00005',
    'O-linked (GalNAc...) threonine': 'MOD:00005',
    'N-linked (Glc) (glycation) lysine': 'MOD:00693',
    'N-linked (Glc) (glycation) arginine': 'MOD:00694',
    'O-linked (Man...) serine': 'MOD:00008',
    'O-linked (Man...) threonine': 'MOD:00008',
    'C-linked (Man) tryptophan': 'MOD:00013',
    
    # Hydroxylation
    'Hydroxyproline': 'MOD:00039',
    '4-hydroxyproline': 'MOD:00039',
    '3-hydroxyproline': 'MOD:00038',
    'Hydroxylysine': 'MOD:00040',
    
    # Oxidation
    'Methionine sulfoxide': 'MOD:00719',
    'Cysteine sulfinic acid': 'MOD:00210',
    'Cysteine sulfonic acid': 'MOD:00211',
    
    # Lipidation
    'N-palmitoylcysteine': 'MOD:00111',
    'S-palmitoylcysteine': 'MOD:00112',
    'N-myristoylglycine': 'MOD:00068',
    'S-geranylgeranylcysteine': 'MOD:00114',
    'S-farnesylcysteine': 'MOD:00113',
    
    # Nitrosylation
    'S-nitrosocysteine': 'MOD:00219',
    
    # Deamidation
    'Deamidated asparagine': 'MOD:00400',
    'Deamidated glutamine': 'MOD:00401',
    
    # Citrullination
    'Citrulline': 'MOD:00219',
    
    # ADP-ribosylation
    'ADP-ribosylarginine': 'MOD:00752',
    'ADP-ribosylcysteine': 'MOD:00753',
}


def get_psi_mod_id(modification_type: str) -> str:
    """
    Get PSI-MOD ID for a given modification type.
    
    Args:
        modification_type: PTM type description (e.g., "Phosphoserine")
    
    Returns:
        PSI-MOD ID (e.g., "MOD:00046") or None if not found
    """
    # Try exact match first
    if modification_type in PSI_MOD_MAPPING:
        return PSI_MOD_MAPPING[modification_type]
    
    # Try case-insensitive match
    for key, value in PSI_MOD_MAPPING.items():
        if key.lower() == modification_type.lower():
            return value
    
    # Try partial match (for variations)
    modification_lower = modification_type.lower()
    for key, value in PSI_MOD_MAPPING.items():
        if key.lower() in modification_lower or modification_lower in key.lower():
            return value
    
    return None


def get_all_mappings() -> dict:
    """
    Get all PSI-MOD mappings.
    
    Returns:
        Dictionary of modification_type -> PSI-MOD ID
    """
    return PSI_MOD_MAPPING.copy()


if __name__ == "__main__":
    # Test the mapping
    test_cases = [
        "Phosphoserine",
        "N6-acetyllysine",
        "O-linked (GalNAc...) threonine",
        "Methionine sulfoxide",
        "Unknown modification"
    ]
    
    print("PSI-MOD Mapping Test:")
    print("=" * 60)
    for test in test_cases:
        psi_id = get_psi_mod_id(test)
        print(f"{test:40s} -> {psi_id if psi_id else 'Not found'}")

