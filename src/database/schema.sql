-- Database schema for seq2fun project
-- Creates tables for genes and research papers in the seq2fun schema

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS seq2fun;

-- Set search path to seq2fun schema
SET search_path TO seq2fun;

-- Drop existing tables (use with caution in production!)
DROP TABLE IF EXISTS papers CASCADE;
DROP TABLE IF EXISTS genes CASCADE;

-- Table 1: Genes from gene_mappings.csv
CREATE TABLE genes (
    symbol VARCHAR(50) PRIMARY KEY,
    name TEXT NOT NULL,
    entrez_gene_id INTEGER,
    uniprot VARCHAR(50),
    why VARCHAR(100),
    include_reprogramming BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Research papers from all_genes_results.csv
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL REFERENCES genes(symbol) ON DELETE CASCADE,
    pmid VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    year INTEGER,
    journal TEXT,
    score FLOAT,
    relevant BOOLEAN DEFAULT FALSE,
    reasoning TEXT,
    modification_effects TEXT,
    longevity_association TEXT,
    search_date DATE,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pmid, symbol)
);

-- Create indexes for better query performance
CREATE INDEX idx_papers_symbol ON papers(symbol);
CREATE INDEX idx_papers_pmid ON papers(pmid);
CREATE INDEX idx_papers_score ON papers(score DESC);
CREATE INDEX idx_papers_relevant ON papers(relevant);
CREATE INDEX idx_papers_search_date ON papers(search_date);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to auto-update updated_at
CREATE TRIGGER update_genes_updated_at BEFORE UPDATE ON genes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_papers_updated_at BEFORE UPDATE ON papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments to tables
COMMENT ON TABLE genes IS 'Gene information from GenAge database';
COMMENT ON TABLE papers IS 'Research papers screened for sequence→function→aging links';

COMMENT ON COLUMN papers.score IS 'Relevance score from LLM screening (0.0 to 1.0)';
COMMENT ON COLUMN papers.relevant IS 'Whether paper meets sequence→function→aging criteria';
COMMENT ON COLUMN papers.modification_effects IS 'Extracted sequence modifications and functional changes';
COMMENT ON COLUMN papers.longevity_association IS 'Extracted aging/longevity outcomes and mechanisms';
