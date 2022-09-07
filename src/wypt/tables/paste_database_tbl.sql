-- Order of table columns much match the `Paste` dataclass model.
CREATE TABLE IF NOT EXISTS paste (
    key text NOT NULL,
    captured_on text NOT NULL
);

-- Create a unique index on the paste key
CREATE UNIQUE INDEX IF NOT EXISTS paste_key ON paste(key);
