-- Order of table columns much match the `Meta` dataclass model.
CREATE TABLE IF NOT EXISTS meta (
    key text NOT NULL,
    scrape_url text NOT NULL,
    full_url text NOT NULL,
    date text NOT NULL,
    size text NOT NULL,
    expire text NOT NULL,
    title text NOT NULL,
    syntax text NOT NULL,
    user text NOT NULL,
    hits text NOT NULL
);

-- Create a unique index on the paste_key
CREATE UNIQUE INDEX IF NOT EXISTS meta_key ON meta(key);
-- Create an index on the syntax flag for searching
CREATE INDEX IF NOT EXISTS syntax_flag ON meta(syntax);
