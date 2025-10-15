export interface Protein {
  id: string;
  name: string;
  fullName: string;
  description: string;
  sequence: string;
  intervals: string[];
  function: string;
}

export const proteins: Protein[] = [
  {
    id: 'SIRT1',
    name: 'SIRT1',
    fullName: 'Sirtuin 1',
    description: 'NAD-dependent deacetylase involved in longevity, metabolism, and stress resistance',
    sequence: 'MADEANLPSTIFVESGKIVQKVTQIDGQLIKENNGIKGLDLYDYENLKQIYFEKVTKEPQK',
    intervals: ['Domain: 244-511 (Sirtuin core)', 'Active site: H363, N346'],
    function: 'Regulates cellular metabolism, DNA repair, and stress responses through protein deacetylation. Extends lifespan in model organisms through caloric restriction pathways.'
  },
  {
    id: 'APOE',
    name: 'APOE',
    fullName: 'Apolipoprotein E',
    description: 'Lipid transport protein with variants linked to Alzheimer\'s disease and longevity',
    sequence: 'MKVLWAALLVTFLAGCQAKVEQAVETEPEPELRQQTEWQSGQRWELALGRFWDYLRWVQT',
    intervals: ['Variant: C112R (ε4 allele)', 'Variant: R158C (ε2 allele)', 'Domain: 1-191 (Receptor binding)'],
    function: 'Mediates cholesterol metabolism and transport. ε2 variant associated with longevity and reduced Alzheimer\'s risk; ε4 variant increases disease risk and reduces lifespan.'
  },
  {
    id: 'TP53',
    name: 'TP53',
    fullName: 'Tumor Protein p53',
    description: 'Tumor suppressor and cellular stress response regulator',
    sequence: 'MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP',
    intervals: ['Domain: 102-292 (DNA binding)', 'Mutation: R175H (hotspot)', 'Domain: 319-358 (Tetramerization)'],
    function: 'Guards genome integrity and cellular senescence. Enhanced p53 activity linked to cancer resistance but may accelerate aging. Balances tumor suppression with aging phenotypes.'
  },
  {
    id: 'FOXO3',
    name: 'FOXO3',
    fullName: 'Forkhead Box O3',
    description: 'Transcription factor strongly associated with human longevity',
    sequence: 'MPPPPPPPPPPPGPRLSAPGGFPVRKGRPRTTFQQMQTLEKAQQQQQQQQQQQQHFPGKA',
    intervals: ['Domain: 129-214 (Forkhead DNA binding)', 'SNP: rs2802292 (longevity variant)', 'Phosphorylation sites: T32, S253, S315'],
    function: 'Regulates genes involved in stress resistance, metabolism, and apoptosis. Polymorphisms associated with exceptional longevity in multiple human populations.'
  },
  {
    id: 'IGF1R',
    name: 'IGF1R',
    fullName: 'Insulin-like Growth Factor 1 Receptor',
    description: 'Growth factor receptor with reduced signaling linked to longevity',
    sequence: 'MKLLLQPLVLLWVSGSQADVCELIPQEEDDYTKFPQGNEFYSGKLSSPYLRTTTGPLDRT',
    intervals: ['Domain: 906-1229 (Tyrosine kinase)', 'Variant: G1013A (longevity-associated)', 'Domain: 30-902 (Extracellular)'],
    function: 'Mediates growth and metabolic signaling. Reduced IGF1R activity associated with extended lifespan in model organisms and human centenarians.'
  },
  {
    id: 'MTOR',
    name: 'MTOR',
    fullName: 'Mechanistic Target of Rapamycin',
    description: 'Nutrient-sensing kinase that regulates growth and aging',
    sequence: 'MLGTAAAVGRSLSRTQGRQVAVQMVREKLELVQCESGHHHSRQAQSDTFQSQHLAHLAAQ',
    intervals: ['Domain: 1362-1982 (Kinase)', 'Domain: 2100-2549 (FATC)', 'Inhibitor binding: rapamycin-FKBP12'],
    function: 'Integrates nutrient and growth signals to regulate protein synthesis, autophagy, and metabolism. mTOR inhibition extends lifespan across species.'
  },
  {
    id: 'KLOTHO',
    name: 'KLOTHO',
    fullName: 'Klotho',
    description: 'Anti-aging protein that regulates mineral metabolism and oxidative stress',
    sequence: 'MAMMFLLLTEVHFLVALLGLVQYSSFDAPSSPPMGPPRGASRARVVAESMTLDPEATRGF',
    intervals: ['Domain: 35-506 (KL1 domain)', 'Domain: 515-982 (KL2 domain)', 'Variant: KL-VS (F352V, C370S)'],
    function: 'Functions as co-receptor for FGF23 and regulates phosphate homeostasis. Overexpression extends lifespan; deficiency causes premature aging phenotypes.'
  },
  {
    id: 'TERT',
    name: 'TERT',
    fullName: 'Telomerase Reverse Transcriptase',
    description: 'Catalytic subunit of telomerase maintaining chromosome ends',
    sequence: 'MPRAPRCRAVRSLLRSHYREVLPLATFVRRLGPQGWRLVQRGDPAAFRALVAQCLVCVPW',
    intervals: ['Domain: 350-934 (Reverse transcriptase)', 'Mutation: V791I (promoter region)', 'Domain: 945-1132 (C-terminal)'],
    function: 'Maintains telomere length by adding TTAGGG repeats. Telomere shortening limits replicative lifespan; TERT activity essential for cellular immortalization.'
  },
  {
    id: 'NRF2',
    name: 'NRF2',
    fullName: 'Nuclear Factor Erythroid 2-Related Factor 2',
    description: 'Master regulator of antioxidant response and cellular defense',
    sequence: 'MDLENSQEKDPQKQLLEEAVEKFDEPRSAVRTSQPQSLTPGTDENPPAALPLRPQATSSD',
    intervals: ['Domain: 1-93 (Neh2, KEAP1 binding)', 'Domain: 434-589 (Neh1, DNA binding)', 'Motif: ETGE, DLG (degradation signals)'],
    function: 'Activates antioxidant and detoxification genes in response to oxidative stress. Enhanced NRF2 activity promotes stress resistance and extends healthspan.'
  },
  {
    id: 'AMPK',
    name: 'AMPK',
    fullName: 'AMP-Activated Protein Kinase Alpha',
    description: 'Energy sensor that regulates metabolism and autophagy',
    sequence: 'MAAAPGARGGPGARSHLGAGGRPWGMGSQSPVAPALPPASRAPSPEGAGAAAPPEQLLQA',
    intervals: ['Domain: 1-312 (Kinase)', 'Activation loop: T172 (phosphorylation)', 'Domain: 313-550 (Autoinhibitory)'],
    function: 'Activates during energy stress to restore ATP levels. Promotes autophagy, mitochondrial biogenesis, and metabolic health. AMPK activation extends lifespan in multiple organisms.'
  },
  {
    id: 'SIRT6',
    name: 'SIRT6',
    fullName: 'Sirtuin 6',
    description: 'NAD-dependent deacetylase regulating DNA repair and genome stability',
    sequence: 'MAEVEDGTVKAAVRGLVGLNTIPLFVQKVTPNPPNPPVAPDFEGLKIPEEVFWEEPGSVL',
    intervals: ['Domain: 35-275 (Sirtuin core)', 'Active site: H133', 'Domain: 1-34 (Nuclear localization)'],
    function: 'Regulates chromatin structure, DNA repair, and glucose metabolism. SIRT6 deficiency causes premature aging; overexpression extends lifespan in male mice.'
  },
  {
    id: 'LMNA',
    name: 'LMNA',
    fullName: 'Lamin A/C',
    description: 'Nuclear envelope protein with mutations causing premature aging',
    sequence: 'MSTGGGGGSRRSRRSGGGSSRARGGLGGGGRRGGRGRGGGRGGFSSGSAGITRGGLDPAA',
    intervals: ['Mutation: G608G (Progeria, cryptic splice site)', 'Domain: 1-386 (Coiled-coil)', 'Domain: 411-566 (Ig-like fold)'],
    function: 'Maintains nuclear structure and chromatin organization. LMNA mutations cause Hutchinson-Gilford Progeria Syndrome, characterized by accelerated aging.'
  }
];
