-- Create user_management schema
CREATE SCHEMA IF NOT EXISTS user_management;

-- Create user table
CREATE TABLE IF NOT EXISTS user_management.user (
    id int4 GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_email ON user_management.user(email);


-- Add comment to table
COMMENT ON TABLE user_management.user IS 'Stores user account information';

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON user_management.user
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
