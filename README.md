# seq2func: Sequence-to-Function Longevity Gene Knowledge Base

A knowledge base extraction pipeline for protein modifications linked to longevity.

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

## Testing

Run the test script to verify PubMed tools:
```bash
uv run python test_tools.py
```

This will:
- Search PubMed for "SIRT1 aging" papers (excluding reviews, free full-text only)
- Fetch abstracts for the first 5 papers
- Display metadata (title, abstract, year, journal, MeSH terms)

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

- PubMed Search Tool: Query PubMed with filters for experimental papers (excludes reviews) with free full-text access
- PubMed Fetch Tool: Retrieve paper metadata (title, abstract, year, journal, MeSH terms) from PMIDs
- Batch Processing: Handles up to 200 PMIDs per fetch request

## Next Steps

- [ ] Add LLM-powered abstract screening tool
- [ ] Build LangChain agent workflow
- [ ] Add database storage (SQLite)
- [ ] Implement data extraction for variants/domains/phenotypes
- [ ] Create export functionality (CSV/JSON)