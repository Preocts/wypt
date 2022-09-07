-- Order of table columns much match the `Match` dataclass model.
CREATE TABLE IF NOT EXISTS match (
    key text NOT NULL,
    match_name text NOT NULL,
    content text NOT NULL
);

-- Create a unique index on the paste key
CREATE UNIQUE INDEX IF NOT EXISTS match_key ON match(key, match_name);
