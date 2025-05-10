-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create platform_information schema
CREATE SCHEMA IF NOT EXISTS platform_information;

-- Create category enum type
CREATE TYPE platform_information.faq_category AS ENUM (
    'general',
    'technical',
    'billing',
    'account',
    'platform_overview',
    'payments',
    'freelancers',
    'clients',
    'platform_features',
    'support',
    'best_practices'
);

-- Create faq_documents table
CREATE TABLE IF NOT EXISTS platform_information.faq_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    link VARCHAR(512) NOT NULL,
    text TEXT NOT NULL,
    llm_summary TEXT,
    category platform_information.faq_category NOT NULL,
    embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_faq_documents_title ON platform_information.faq_documents(title);
CREATE INDEX IF NOT EXISTS idx_faq_documents_category ON platform_information.faq_documents(category);
CREATE INDEX IF NOT EXISTS idx_faq_documents_embedding ON platform_information.faq_documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);  -- Adjust lists based on your data size

-- Add comments to table and columns
COMMENT ON SCHEMA platform_information IS 'Schema for storing platform-related information and documentation';
COMMENT ON TABLE platform_information.faq_documents IS 'Stores FAQ documents with their vector embeddings for semantic search';
COMMENT ON COLUMN platform_information.faq_documents.id IS 'Unique identifier for the FAQ document';
COMMENT ON COLUMN platform_information.faq_documents.title IS 'Title of the FAQ document';
COMMENT ON COLUMN platform_information.faq_documents.link IS 'URL or reference link to the original document';
COMMENT ON COLUMN platform_information.faq_documents.text IS 'Full text content of the FAQ document';
COMMENT ON COLUMN platform_information.faq_documents.llm_summary IS 'AI-generated summary of the document content';
COMMENT ON COLUMN platform_information.faq_documents.category IS 'Category of the FAQ document';
COMMENT ON COLUMN platform_information.faq_documents.embedding IS 'Vector embedding for semantic search';
COMMENT ON COLUMN platform_information.faq_documents.created_at IS 'Timestamp when the document was created';
COMMENT ON COLUMN platform_information.faq_documents.updated_at IS 'Timestamp when the document was last updated';

-- Create trigger for updated_at
CREATE TRIGGER update_faq_documents_updated_at
    BEFORE UPDATE ON platform_information.faq_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
