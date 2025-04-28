-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the extension is installed
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        RAISE NOTICE 'pgvector extension successfully installed';
    ELSE
        RAISE EXCEPTION 'Failed to install pgvector extension';
    END IF;
END $$; 