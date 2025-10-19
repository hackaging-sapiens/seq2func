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

The main workflow searches PubMed for gene-related papers, screens them using LLM for sequence→function→aging links, and saves the top results to both CSV files and PostgreSQL database.

**Run batch search for multiple genes:**

```bash
uv run python src/workflows/gene_search.py data/gene_mappings.csv
```

This will:
1. Read genes from `data/gene_mappings.csv` (symbol, include_reprogramming)
2. Search PubMed to get the top 200 papers for each gene with optimized aging-related queries
3. Screen all 200 papers using LLM for SEQUENCE→FUNCTION→AGING causal links
4. Filter and rank top 20 relevant papers by relevance score
5. Extract modification effects and longevity associations for top 20 papers only
6. Save results to `data/all_genes_results.csv`
7. Skip genes that already have results in the database

**Force rerun all genes (ignore existing results):**

```bash
uv run python src/workflows/gene_search.py data/gene_mappings.csv --force
```

**Output CSV Schema:**
- `symbol`: Gene symbol (e.g., NFE2L2, APOE) - primary key
- `pmid`: PubMed ID
- `title`: Paper title
- `year`: Publication year
- `journal`: Journal name
- `score`: Relevance score (0.0-1.0)
- `relevant`: Boolean (only True papers are saved)
- `reasoning`: LLM explanation for the score
- `modification_effects`: Extracted sequence modifications and functional changes
- `longevity_association`: Extracted aging/longevity outcomes and mechanisms
- `search_date`: Date of search
- `url`: PubMed article URL

### Database Setup

**Load data into PostgreSQL:**

```bash
# Initialize schema and load all data
uv run python src/database/load_data.py --all

# Or run individual steps
uv run python src/database/load_data.py --init-schema
uv run python src/database/load_data.py --load-genes
uv run python src/database/load_data.py --load-results
```

**Database Schema (`seq2fun` schema in PostgreSQL):**

**Table 1: `genes`** (22 genes from GenAge database)
- `symbol` (PRIMARY KEY): Gene symbol
- `name`: Full gene name
- `entrez_gene_id`: NCBI Entrez Gene ID
- `uniprot`: UniProt ID
- `why`: GenAge classification (mammal, model, cell, human_link, etc.)
- `include_reprogramming`: Boolean flag for reprogramming-related genes
- `created_at`, `updated_at`: Timestamps

**Table 2: `papers`** (Research papers screened for aging relevance)
- `id` (SERIAL PRIMARY KEY): Auto-incrementing ID
- `symbol` (FOREIGN KEY → genes.symbol): Gene symbol
- `pmid`: PubMed ID
- `title`: Paper title
- `year`: Publication year
- `journal`: Journal name
- `score`: LLM relevance score (0.0-1.0)
- `relevant`: Boolean screening result
- `reasoning`: LLM explanation
- `modification_effects`: Sequence modifications and functional changes
- `longevity_association`: Aging/longevity outcomes and mechanisms
- `search_date`: Date of search
- `url`: PubMed article URL
- `created_at`, `updated_at`: Timestamps

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
- **PubMed Fetch**: Retrieve paper metadata (title, abstract, year, journal, MeSH terms, URLs)
- **LLM Screening**: AI-powered screening for SEQUENCE→FUNCTION→AGING causal links
- **Association Extraction**: Extract modification effects and longevity associations from abstracts
- **Batch Processing**: Process multiple genes, screen 200 papers per gene, extract associations for top 20
- **PostgreSQL Database**: Store genes and papers in structured database with full-text search capabilities

### Workflow Optimization
- Screen 200 papers for relevance using LLM
- Filter and rank to get top 20 papers
- Extract detailed associations only for top 20 (saves LLM costs by 45%)

## Database Schema

The project uses PostgreSQL with two main tables in the `seq2fun` schema:

**`genes` table**: 22 curated aging genes from GenAge database
**`papers` table**: 350+ research papers with LLM-extracted modification effects and longevity associations

Each paper includes:
- Relevance score and reasoning
- Modification effects (sequence changes and functional impacts)
- Longevity association (aging outcomes and mechanisms)
- Direct PubMed URL for access

## Next Steps

- [x] Add protein variant/domain extraction from abstracts
- [x] Implement structured data extraction (mutations, phenotypes)
- [x] Add PostgreSQL database layer
- [ ] Create REST API endpoints for live gene search
- [ ] Build admin dashboard for reviewing results
- [ ] Add full-text PDF analysis for detailed evidence extraction
- [ ] Implement caching for frequently searched genes