"""Abstract screening tool using LLM to filter papers for aging relevance."""
import json
from typing import Dict, Any, List
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


SCREENING_PROMPT = """You are filtering biomedical papers for SEQUENCE→PHENOTYPE links in aging research.

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


def screen_paper_by_metadata(title: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Screen a paper for aging/longevity relevance using only title and keywords.

    Args:
        title: Paper title
        keywords: List of MeSH terms or keywords

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
        prompt = SCREENING_PROMPT.format(title=title, keywords=keywords_str)
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


def create_abstract_screening_tool() -> Tool:
    """Create a LangChain tool for paper screening using metadata only."""
    def screen_paper_json(paper_json: str) -> str:
        """Screen a paper from JSON input using only title and keywords."""
        try:
            paper = json.loads(paper_json)
            result = screen_paper_by_metadata(
                title=paper.get("title", ""),
                keywords=paper.get("mesh_terms", [])
            )
            # Add PMID to result
            result["pmid"] = paper.get("pmid", "")
            return json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    return Tool(
        name="Screen_Paper_By_Metadata",
        description=(
            "Screen a paper for aging/longevity relevance using ONLY title and keywords (MeSH terms). "
            "This is much more token-efficient than reading full abstracts. "
            "Input should be a JSON object with 'pmid', 'title', and 'mesh_terms' (list) fields. "
            "Returns JSON with 'relevant' (bool), 'score' (0-1), and 'reasoning' (str)."
        ),
        func=screen_paper_json
    )
