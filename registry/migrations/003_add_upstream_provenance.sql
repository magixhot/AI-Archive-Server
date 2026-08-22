ALTER TABLE models
ADD COLUMN upstream_revision TEXT;


ALTER TABLE models
ADD COLUMN upstream_revision_recorded TIMESTAMP;


ALTER TABLE models
ADD COLUMN metadata_refreshed_at TIMESTAMP;
