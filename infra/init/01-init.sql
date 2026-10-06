-- Runs once, on first container start, against an empty database.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Two schemas, two owners. Neither service writes to the other's tables.
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS app;

CREATE ROLE rag_user WITH LOGIN PASSWORD 'dev';
CREATE ROLE app_user WITH LOGIN PASSWORD 'dev';

-- Python owns rag, and has no rights at all on app.
GRANT USAGE, CREATE ON SCHEMA rag TO rag_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rag_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag
    GRANT USAGE, SELECT ON SEQUENCES TO rag_user;

-- Java owns app, and has no rights at all on rag.
GRANT USAGE, CREATE ON SCHEMA app TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA app
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA app
    GRANT USAGE, SELECT ON SEQUENCES TO app_user;

GRANT CONNECT ON DATABASE platform TO rag_user, app_user;

-- rag_user's default search path
ALTER ROLE rag_user SET search_path TO rag, public;
ALTER ROLE app_user SET search_path TO app, public;
