# seq2func: Sequence-to-Function Longevity Gene Knowledge Base

A knowledge base extraction pipeline for protein modifications linked to longevity.

Website URL: https://hackaging-sapiens.github.io/seq2func/

## Setup

### 1. Prerequisites
- Python 3.12
- [uv](https://github.com/astral-sh/uv) package manager


### 2. Get Source Code

```
git clone https://github.com/j-silv/seq2func.git
cd seq2func
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Configure Environment Variables
Copy the example env file and add your API keys:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- `NEBIUS_API_KEY`: Your Nebius AI API key
- `NCBI_EMAIL`: Your email (required by NCBI)
- `NCBI_API_KEY`: (Optional) For higher rate limits -> must be commented out if unused

## Usage

### Gene Literature Search Workflow

The main workflow searches PubMed for gene-related papers, screens them using LLM for sequence→function→aging links, and saves the top results to a CSV database.

**Run batch search for multiple genes:**

```bash
uv run python src/workflows/gene_search.py data/gene_mappings.csv
```

This will:
1. Read genes from `data/gene_mappings.csv` (gene_symbol, gene_id, include_reprogramming)
2. Prescreen with PubMed search to get the top 200 papers for each gene with the optimized query
3. Deep screen top 200 using LLM for SEQUENCE→FUNCTION→AGING causal links
4. Save top 20 relevant papers per gene (ranked by LLM rating) to `data/all_genes_results.csv`
5. Skip genes that already have results in the database

**Force rerun all genes (ignore existing results):**

```bash
uv run python src/workflows/gene_search.py data/gene_mappings.csv --force
```

**Output CSV Schema:**
- `gene_id`: NCBI Gene ID (primary key)
- `gene_symbol`: Gene symbol (e.g., NRF2, SOX2)
- `pmid`: PubMed ID
- `title`: Paper title
- `year`: Publication year
- `journal`: Journal name
- `score`: Relevance score (0.0-1.0)
- `relevant`: Boolean (only True papers are saved)
- `reasoning`: LLM explanation for the score
- `search_date`: Date of search

## Web application

The frontend web app uses Next.js (React) with Tailwind CSS.

Install `fnm` to manage Node.js versions

```
sudo apt install curl unzip
curl -fsSL https://fnm.vercel.app/install | bash
fnm install --lts
fnm use lts-latest
```

Install package manager `pnpm`:

```
npm install -g pnpm@latest-10
```

Install packages (make sure you are in repo's root directory)

```
pnpm install
```

Run server

```
pnpm dev
```

## Current Features

### Core Tools
- **PubMed Search**: Query PubMed with aging-related terms (excludes reviews, requires abstracts)
- **PubMed Fetch**: Retrieve paper metadata (title, abstract, year, journal, MeSH terms)
- **LLM Screening**: AI-powered screening for SEQUENCE→FUNCTION→AGING causal links
- **Batch Processing**: Process multiple genes and handle up to 200 papers per search

## Project Structure

```
seq2func/
├── src/
│   ├── tools/           # Individual tools (PubMed, Screening)
│   │   ├── pubmed.py
│   │   └── screening.py
│   ├── workflows/       # End-to-end workflows
│   │   └── gene_search.py
│   └── config.py        # Environment configuration
├── data/
│   ├── gene_mappings.csv           # Input: genes to search
│   └── literature_search/
│       └── all_genes_results.csv   # Output: screened papers
├── notebooks/           # Jupyter notebooks for testing
└── app/                 # Next.js frontend

```

## Next Steps

- [ ] Add protein variant/domain extraction from abstracts
- [ ] Implement structured data extraction (mutations, phenotypes)
- [ ] Add SQLite database layer
- [ ] Create REST API endpoints
- [ ] Build admin dashboard for reviewing results
- [ ] Add full-text PDF analysis for detailed evidence extraction