ALTER TABLE models
ADD COLUMN download_started TIMESTAMP;


ALTER TABLE models
ADD COLUMN download_finished TIMESTAMP;


ALTER TABLE models
ADD COLUMN error_message TEXT;