"""Unified screening tool using LLM to filter papers for aging relevance."""
import json
from typing import Dict, Any, List
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from src.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL


ASSOCIATION_PROMPT = """
You are extracting structured information about protein modifications and their longevity effects from biomedical papers.

Your task is to extract TWO specific pieces of information:

1. **MODIFICATION EFFECTS**: Identify sequence-level modifications and their functional impacts
   - Sequence intervals (e.g., "residues 45-67", "C-terminal domain", "position 151")
   - Specific mutations (e.g., "C151S", "deletion 200-250", "K48R substitution")
   - Functional changes resulting from modifications (e.g., "increased transcriptional activity", "enhanced DNA binding", "reduced degradation")

2. **LONGEVITY ASSOCIATION**: Identify aging/longevity outcomes and mechanisms
   - Phenotypic outcome (e.g., "extended lifespan", "delayed senescence", "enhanced stress resistance")
   - Magnitude if specified (e.g., "20% increase", "1.5-fold extension", "significant")
   - Model organism (e.g., "C. elegans", "mice", "human cells", "yeast")
   - Mechanism connecting to aging (e.g., "reduced oxidative stress", "enhanced autophagy", "improved proteostasis")

### OUTPUT FORMAT
Respond ONLY with valid JSON in this exact format:
{{
  "modification_effects": "Concise summary of sequence modifications and functional changes, or 'Not specified' if unclear",
  "longevity_association": "Concise summary of aging/longevity outcomes and mechanisms, or 'Not specified' if unclear"
}}

### EXAMPLES

**Example 1 - Clear modifications and longevity:**
Title: "KEAP1 mutation constitutively activates NRF2 and extends lifespan in birds"
Abstract: "Modern birds carry a KEAP1 mutation that prevents NRF2 degradation, leading to constitutive antioxidant activation. This results in reduced oxidative damage and 30% extended lifespan compared to reptiles..."

Output:
{{
  "modification_effects": "KEAP1 mutation prevents NRF2 degradation; constitutive antioxidant pathway activation",
  "longevity_association": "30% lifespan extension in birds; mechanism: reduced oxidative stress"
}}

**Example 2 - Specific residue mutations:**
Title: "SOX2 C-terminal modifications enhance reprogramming efficiency"
Abstract: "Mutations in SOX2 residues 200-220 increase DNA binding affinity 3-fold. Modified SOX2 improves cellular reprogramming efficiency by 50% in aged fibroblasts..."

Output:
{{
  "modification_effects": "Residues 200-220 mutations; 3-fold increased DNA binding affinity",
  "longevity_association": "50% improved reprogramming efficiency in aged cells; rejuvenation potential"
}}

**Example 3 - Limited information:**
Title: "NRF2 pathway activation promotes stress resistance"
Abstract: "Activation of NRF2 pathway enhances antioxidant response and improves stress resistance in aging cells..."

Output:
{{
  "modification_effects": "Not specified",
  "longevity_association": "Enhanced stress resistance in aging cells; antioxidant pathway activation"
}}

**Example 4 - APOE variants:**
Title: "APOE2 variant protective effect on longevity"
Abstract: "The APOE2 allele, characterized by Cys112/Cys158, shows protective effects with 20% increased survival in centenarians compared to APOE4 carriers..."

Output:
{{
  "modification_effects": "APOE2 variant (Cys112/Cys158); altered lipid binding properties",
  "longevity_association": "20% increased survival in human centenarians; protective against neurodegeneration"
}}

---

### INSTRUCTIONS
- Be **concise** but **specific** - include numerical values and organism names when available
- If information is not mentioned in the paper, write "Not specified"
- Focus on **concrete findings**, not speculation
- Extract only from the provided title, abstract, and keywords

---

PAPER TO ANALYZE:
Title: {title}
Abstract: {abstract}
MeSH Terms: {keywords}
""".strip()

SCREENING_PROMPT = """
You are analyzing biomedical papers to identify SEQUENCE → FUNCTION → AGING causal links.

Your task is to determine whether the paper provides **experimental or mechanistic evidence** that:
1. A specific **SEQUENCE CHANGE** occurs (mutation, variant, SNP, domain modification, insertion, deletion, or PTM site change).
2. This sequence change leads to a **FUNCTIONAL CHANGE** (altered protein activity, stability, localization, or pathway behavior).
3. This functional change produces a measurable **AGING-RELATED PHENOTYPIC EFFECT** (e.g., lifespan extension/reduction, stress resistance, rejuvenation, senescence delay, or altered reprogramming efficiency).

### PRIORITIZATION RULES
- Phenotypic effects (e.g., lifespan, healthspan, stress resistance, rejuvenation, reprogramming) are **most valuable**.
- Molecular-level changes (binding, promoter interaction, transcriptional regulation) may count **only if clearly linked** to a phenotypic outcome.
- Prefer **experimental or evolutionary evidence** over purely computational predictions.

### CRITICAL REQUIREMENTS
- Must include an explicit **sequence-level modification** (not just expression or pathway activation).
- Must demonstrate a **causal chain**: sequence change → functional alteration → phenotype related to aging or longevity.
- Must have **phenotypic relevance** (aging, lifespan, healthspan, senescence, reprogramming, stress resistance, or evolutionarily conserved traits).

### EXCLUSION CRITERIA
- Studies showing only expression changes without sequence modifications.
- Purely disease-focused or cancer-only papers with no aging or longevity connection.
- Correlative studies lacking mechanistic explanation.
- Molecular binding or promoter studies without clear phenotypic consequences.

---

### EXAMPLES OF RELEVANT STUDIES (CONCEPTUAL GUIDANCE)
These examples illustrate what kinds of studies are considered **relevant** or **not relevant** for this task:

**Relevant Example 1 – NRF2 / KEAP1 (Sequence → Function → Phenotype):**
A paper showing that Neoaves (modern birds) have a KEAP1 mutation that constitutively activates NRF2, leading to reduced oxidative stress and increased lifespan.
→ Relevant because it describes a specific sequence change (KEAP1 mutation), a functional mechanism (NRF2 activation), and a phenotypic outcome (longer lifespan).

**Relevant Example 2 – SKN-1 / NRF2 Ortholog:**
A study where activation of SKN-1 (nematode ortholog of NRF2) extends lifespan and increases stress resistance in C. elegans.
→ Relevant because it connects function to an aging phenotype, even across species.

**Relevant Example 3 – SOX2 (SuperSOX):**
A paper describing a modified SOX2 protein with sequence alterations that enhance reprogramming efficiency.
→ Relevant because sequence modifications lead to improved cellular rejuvenation — a phenotype linked to aging reversal.

**Relevant Example 4 – APOE Variants:**
Studies describing APOE variants and their effects on longevity:
- APOE2 — protective, associated with longer lifespan
- APOE3 — neutral, common variant
- APOE4 — risk variant, linked to reduced longevity and Alzheimer's risk
→ Relevant because these are well-defined genetic variants directly linked to aging outcomes.

**Relevant Example 5 – OCT4 / OCT6 Conversion:**
A study showing that changing POU dimerization preferences converts OCT6 into a pluripotency inducer (a reprogramming factor).
→ Relevant because it describes sequence modification leading to functional and phenotypic change (enhanced reprogramming efficiency).

**Not Relevant Example – Expression-Only NRF2 Study:**
A paper showing NRF2 overexpression in cancer progression without mutations or aging relevance.
→ Not relevant because it lacks sequence-level change and aging phenotype.

These examples should guide your judgment of what counts as meaningful **sequence → function → aging** evidence.

---

### OUTPUT FORMAT
Respond ONLY with valid JSON in this exact format:
{{
  "relevant": true or false,
  "score": 0.0 to 1.0,
  "reasoning": "Brief explanation (1–2 sentences)"
}}

### SCORING GUIDE
- **1.0**: Strong evidence for all three links (sequence → function → phenotype) with validated or quantitative outcomes.
- **0.7–0.9**: All three links present but partial or indirect mechanistic details.
- **0.4–0.6**: Two links clearly established (e.g., sequence→function or function→phenotype).
- **0.1–0.3**: Only one weak link or speculative evidence.
- **0.0**: No relevant sequence-level, functional, or aging/phenotypic information.

Set `"relevant": true` if **score ≥ 0.5** (at least two criteria clearly met).

---

PAPER TO ANALYZE:
Title: {title}
Abstract: {abstract}
MeSH Terms: {keywords}
""".strip()


class Screening:
    """
    A class for screening biomedical papers for aging/longevity relevance using LLM.

    Analyzes papers to identify SEQUENCE→FUNCTION→AGING causal links using
    title, abstract, and MeSH terms.

    Example:
        screening = Screening()
        result = screening.screen_paper(
            title="APOE variants and longevity",
            abstract="APOE2 is associated with increased lifespan...",
            keywords=["Aging", "Longevity", "APOE"]
        )
        print(result["score"], result["reasoning"])
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize Screening client.

        Args:
            api_key: API key for LLM provider (defaults to config)
            base_url: Base URL for LLM API (defaults to config)
            model: Model name (defaults to config)
        """
        self.api_key = api_key or NEBIUS_API_KEY
        self.base_url = base_url or NEBIUS_BASE_URL
        self.model = model or NEBIUS_MODEL

        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            temperature=0.1  # Low temperature for consistent filtering
        )

    def screen_paper(
        self,
        title: str,
        abstract: str,
        keywords: List[str] = None
    ) -> Dict[str, Any]:
        """
        Screen a paper for aging/longevity relevance using title, abstract, and MeSH terms.

        Analyzes papers to identify SEQUENCE→FUNCTION→AGING causal links.

        Args:
            title: Paper title
            abstract: Full abstract text (required)
            keywords: List of MeSH terms or keywords (optional)

        Returns:
            Dict with keys: relevant (bool), score (float), reasoning (str)
        """
        if not title:
            return {
                "relevant": False,
                "score": 0.0,
                "reasoning": "Missing title"
            }

        if not abstract:
            return {
                "relevant": False,
                "score": 0.0,
                "reasoning": "Missing abstract"
            }

        # Format keywords as a readable string
        keywords_str = ", ".join(keywords) if keywords else "None"

        try:
            prompt = SCREENING_PROMPT.format(
                title=title,
                abstract=abstract,
                keywords=keywords_str
            )

            response = self.llm.invoke(prompt)

            # Parse JSON from LLM response
            # Strip markdown code blocks if present (```json ... ```)
            content = response.content.strip()

            if content.startswith("```"):
                # Remove markdown code block markers
                lines = content.split("\n")
                # Remove first line (```json or ```)
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            result = json.loads(content)

            # Ensure all required fields exist
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided"
            if "score" not in result:
                result["score"] = 0.0
            if "relevant" not in result:
                result["relevant"] = False

            return result

        except json.JSONDecodeError as e:
            # Log the raw response for debugging
            raw_response = response.content if 'response' in locals() else "No response"
            return {
                "relevant": False,
                "score": 0.0,
                "reasoning": f"LLM response parsing error: {str(e)}. Raw: {raw_response[:200]}"
            }
        except Exception as e:
            return {
                "relevant": False,
                "score": 0.0,
                "reasoning": f"Screening error: {str(e)}"
            }

    def screen_association(
        self,
        title: str,
        abstract: str,
        keywords: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract modification effects and longevity associations from a paper.

        Analyzes papers to extract structured information about:
        1. Modification effects (sequence changes and functional impacts)
        2. Longevity association (aging/longevity outcomes and mechanisms)

        Args:
            title: Paper title
            abstract: Full abstract text (required)
            keywords: List of MeSH terms or keywords (optional)

        Returns:
            Dict with keys: modification_effects (str), longevity_association (str)
        """
        if not title:
            return {
                "modification_effects": "Not specified",
                "longevity_association": "Not specified"
            }

        if not abstract:
            return {
                "modification_effects": "Not specified",
                "longevity_association": "Not specified"
            }

        # Format keywords as a readable string
        keywords_str = ", ".join(keywords) if keywords else "None"

        try:
            prompt = ASSOCIATION_PROMPT.format(
                title=title,
                abstract=abstract,
                keywords=keywords_str
            )

            response = self.llm.invoke(prompt)

            # Parse JSON from LLM response
            # Strip markdown code blocks if present (```json ... ```)
            content = response.content.strip()

            if content.startswith("```"):
                # Remove markdown code block markers
                lines = content.split("\n")
                # Remove first line (```json or ```)
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            result = json.loads(content)

            # Ensure all required fields exist
            if "modification_effects" not in result:
                result["modification_effects"] = "Not specified"
            if "longevity_association" not in result:
                result["longevity_association"] = "Not specified"

            return result

        except json.JSONDecodeError as e:
            # Log the raw response for debugging
            raw_response = response.content if 'response' in locals() else "No response"
            return {
                "modification_effects": f"Parsing error: {str(e)}",
                "longevity_association": "Not specified"
            }
        except Exception as e:
            return {
                "modification_effects": f"Extraction error: {str(e)}",
                "longevity_association": "Not specified"
            }
