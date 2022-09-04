-- Order of table columns much match the `Paste` dataclass model.
CREATE TABLE IF NOT EXISTS paste (
    key text NOT NULL,
    content text NOT NULL
);

-- Create a unique index on the paste key
CREATE UNIQUE INDEX paste_key ON paste(key);
