# seq2func: Sequence-to-Function Longevity Gene Knowledge Base

A knowledge base extraction pipeline for protein modifications linked to longevity.

## Setup

### 1. Prerequisites
- Python 3.12
- [uv](https://github.com/astral-sh/uv) package manager

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure Environment Variables
Copy the example env file and add your API keys:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- `NEBIUS_API_KEY`: Your Nebius AI API key
- `NCBI_EMAIL`: Your email (required by NCBI)
- `NCBI_API_KEY`: (Optional) For higher rate limits

## Testing

Run the test script to verify PubMed tools:
```bash
uv run python test_tools.py
```

This will:
- Search PubMed for "SIRT1 aging" papers (excluding reviews, free full-text only)
- Fetch abstracts for the first 5 papers
- Display metadata (title, abstract, year, journal, MeSH terms)

## Current Features

- PubMed Search Tool: Query PubMed with filters for experimental papers (excludes reviews) with free full-text access
- PubMed Fetch Tool: Retrieve paper metadata (title, abstract, year, journal, MeSH terms) from PMIDs
- Batch Processing: Handles up to 200 PMIDs per fetch request

## Next Steps

- [ ] Add LLM-powered abstract screening tool
- [ ] Build LangChain agent workflow
- [ ] Add database storage (SQLite)
- [ ] Implement data extraction for variants/domains/phenotypes
- [ ] Create export functionality (CSV/JSON)