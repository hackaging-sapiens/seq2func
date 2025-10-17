"""Unified screening tool using LLM to filter papers for aging relevance."""
import json
from typing import Dict, Any, List
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from src.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL


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
