"""Unified screening tool using LLM to filter papers for aging relevance."""
import json
from typing import Dict, Any, List, Optional
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from src.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL


# Initialize Nebius LLM (OpenAI-compatible)
llm = ChatOpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
    model=NEBIUS_MODEL,
    temperature=0.1  # Low temperature for consistent filtering
)


METADATA_SCREENING_PROMPT = """You are filtering biomedical papers for SEQUENCE→PHENOTYPE links in aging research.

INCLUSION CRITERIA:
- Title suggests specific mutation/variant/domain change in a protein or gene
- Keywords indicate links to longevity, lifespan, survival, stress resistance, centenarians, or age-related phenotypes
- Evidence of experimental or genetic studies (not just computational predictions)
- NOT just speculation or correlation without mechanism

EXCLUSION CRITERIA:
- Review articles or meta-analyses (should already be filtered)
- No specific sequence modifications mentioned
- Only disease focus without aging/longevity context
- Purely computational predictions without validation

PAPER TO SCREEN:
Title: {title}

Keywords/MeSH Terms: {keywords}

Respond ONLY with valid JSON in this exact format:
{{
  "relevant": true or false,
  "score": 0.0 to 1.0,
  "reasoning": "Brief explanation (1-2 sentences)"
}}
"""


ABSTRACT_SCREENING_PROMPT = """You are analyzing biomedical papers to identify SEQUENCE→FUNCTION→AGING causal links.

Your task is to identify papers where:
1. A specific SEQUENCE CHANGE is described (mutation, variant, SNP, domain modification, insertion, deletion, etc.)
2. This sequence change leads to a FUNCTIONAL CHANGE (altered protein activity, stability, binding, localization, etc.)
3. This functional change affects an AGING-RELATED PHENOTYPE (longevity, lifespan, healthspan, stress resistance, age-related disease, cellular senescence, etc.)

PAPER TO ANALYZE:
Title: {title}
Abstract: {abstract}
MeSH Terms: {keywords}

CRITICAL REQUIREMENTS:
- Must have explicit sequence-level changes (not just gene expression changes)
- Must show mechanistic connection between sequence and function
- Must relate to aging/longevity outcomes (not just disease without aging context)
- Experimental validation preferred over purely computational predictions

EXCLUSION CRITERIA:
- Only transcriptional/expression changes without sequence modifications
- Disease studies with no aging/longevity connection
- Pure correlations without mechanistic insight
- Review articles (should already be filtered)

Respond ONLY with valid JSON in this exact format:
{{
  "relevant": true or false,
  "score": 0.0 to 1.0,
  "reasoning": "Brief explanation (1-2 sentences)"
}}

Score calculation guide:
- 1.0: All three criteria met with strong mechanistic evidence (sequence→function→aging link)
- 0.7-0.9: All three criteria met but weaker evidence or partial mechanistic understanding
- 0.4-0.6: Two criteria met (e.g., sequence+function but weak aging link)
- 0.1-0.3: Only one criterion met or very weak evidence
- 0.0: None of the criteria met

Set "relevant" to true if score >= 0.5 (at least two criteria met).
"""


def screen_paper(
    title: str,
    keywords: List[str] = None,
    abstract: Optional[str] = None
) -> Dict[str, Any]:
    """
    Screen a paper for aging/longevity relevance.

    Can perform two types of screening:
    1. Quick screening using only title and keywords (when abstract=None)
    2. Deep screening using title, abstract, and keywords (when abstract is provided)

    Args:
        title: Paper title
        keywords: List of MeSH terms or keywords (optional)
        abstract: Full abstract text (optional). If provided, performs deep screening.

    Returns:
        Dict with keys: relevant (bool), score (float), reasoning (str)
    """
    if not title:
        return {
            "relevant": False,
            "score": 0.0,
            "reasoning": "Missing title"
        }

    # Format keywords as a readable string
    keywords_str = ", ".join(keywords) if keywords else "None"

    try:
        # Choose prompt based on whether abstract is provided
        if abstract:
            # Deep screening with abstract
            if not abstract:
                return {
                    "relevant": False,
                    "score": 0.0,
                    "reasoning": "Abstract screening requested but abstract is empty"
                }
            prompt = ABSTRACT_SCREENING_PROMPT.format(
                title=title,
                abstract=abstract,
                keywords=keywords_str
            )
        else:
            # Quick screening with metadata only
            prompt = METADATA_SCREENING_PROMPT.format(
                title=title,
                keywords=keywords_str
            )

        response = llm.invoke(prompt)

        # Parse JSON from LLM response
        result = json.loads(response.content)

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


# Backward compatibility alias
def screen_paper_by_metadata(title: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Use screen_paper() instead.
    """
    return screen_paper(title=title, keywords=keywords, abstract=None)


def create_screening_tool() -> Tool:
    """Create a LangChain tool for paper screening (supports both metadata and abstract screening)."""
    def screen_paper_json(paper_json: str) -> str:
        """Screen a paper from JSON input. Automatically uses abstract if provided."""
        try:
            paper = json.loads(paper_json)
            result = screen_paper(
                title=paper.get("title", ""),
                keywords=paper.get("mesh_terms", []),
                abstract=paper.get("abstract")  # Will be None if not provided
            )
            # Add PMID to result
            result["pmid"] = paper.get("pmid", "")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    return Tool(
        name="Screen_Paper",
        description=(
            "Screen a paper for aging/longevity relevance. Performs quick screening with title/keywords "
            "or deep screening with abstract (if provided). For deep screening, looks for sequence→function→aging links. "
            "Input should be a JSON object with 'pmid', 'title', 'mesh_terms' (list), and optionally 'abstract'. "
            "Returns JSON with 'relevant' (bool), 'score' (0-1), and 'reasoning' (str)."
        ),
        func=screen_paper_json
    )


# Backward compatibility alias
def create_abstract_screening_tool() -> Tool:
    """Legacy function for backward compatibility. Use create_screening_tool() instead."""
    return create_screening_tool()
