CREATE TABLE IF NOT EXISTS models (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    model_id TEXT NOT NULL UNIQUE,

    family TEXT,

    version TEXT,

    status TEXT NOT NULL DEFAULT 'QUEUED',

    storage_path TEXT,

    size_bytes INTEGER,

    sha256 TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    verified_at TIMESTAMP

);


CREATE INDEX IF NOT EXISTS idx_models_status
ON models(status);


CREATE INDEX IF NOT EXISTS idx_models_family
ON models(family);