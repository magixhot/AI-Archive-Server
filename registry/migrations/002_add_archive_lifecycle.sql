ALTER TABLE models
ADD COLUMN archive_created TIMESTAMP;


ALTER TABLE models
ADD COLUMN archive_validated TIMESTAMP;


ALTER TABLE models
ADD COLUMN last_verified TIMESTAMP;