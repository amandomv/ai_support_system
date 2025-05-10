-- Create user_response table in user_management schema
CREATE TABLE IF NOT EXISTS user_management.user_response (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES user_management.user(id),
    user_question TEXT NOT NULL,
    question_embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
    response TEXT NOT NULL,
    response_embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_response_user_id ON user_management.user_response(user_id);
CREATE INDEX IF NOT EXISTS idx_user_response_question_embedding ON user_management.user_response USING ivfflat (question_embedding vector_cosine_ops)
    WITH (lists = 100);  -- Adjust lists based on your data size
CREATE INDEX IF NOT EXISTS idx_user_response_response_embedding ON user_management.user_response USING ivfflat (response_embedding vector_cosine_ops)
    WITH (lists = 100);  -- Adjust lists based on your data size

-- Add comments to table and columns
COMMENT ON TABLE user_management.user_response IS 'Stores user questions and AI responses with their vector embeddings';
COMMENT ON COLUMN user_management.user_response.id IS 'Unique identifier for the user response record';
COMMENT ON COLUMN user_management.user_response.user_id IS 'Reference to the user who asked the question';
COMMENT ON COLUMN user_management.user_response.user_question IS 'The question asked by the user';
COMMENT ON COLUMN user_management.user_response.question_embedding IS 'Vector embedding of the user question for semantic search';
COMMENT ON COLUMN user_management.user_response.response IS 'The AI-generated response';
COMMENT ON COLUMN user_management.user_response.response_embedding IS 'Vector embedding of the AI response for semantic search';
COMMENT ON COLUMN user_management.user_response.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN user_management.user_response.updated_at IS 'Timestamp when the record was last updated';

-- Create trigger for updated_at
CREATE TRIGGER update_user_response_updated_at
    BEFORE UPDATE ON user_management.user_response
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
