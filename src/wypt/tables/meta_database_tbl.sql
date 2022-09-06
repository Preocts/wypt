-- Order of table columns much match the `PasteMeta` dataclass model.
CREATE TABLE IF NOT EXISTS pastemeta (
    scrape_url text NOT NULL,
    full_url text NOT NULL,
    date text NOT NULL,
    key text NOT NULL,
    size text NOT NULL,
    expire text NOT NULL,
    title text NOT NULL,
    syntax text NOT NULL,
    user text NOT NULL,
    hits text NOT NULL
);

-- Create a unique index on the paste_key
CREATE UNIQUE INDEX IF NOT EXISTS paste_key ON pastemeta(key);
-- Create an index on the syntax flag for searching
CREATE INDEX IF NOT EXISTS syntax_flag ON pastemeta(syntax);
