CREATE TABLE IF NOT EXISTS crypto_prices (
    id BIGSERIAL PRIMARY KEY,
    asset_id TEXT NOT NULL,
    asset_name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price_usd NUMERIC(20, 8) NOT NULL,
    volume_24h_usd NUMERIC(24, 2),
    change_24h_percent NUMERIC(10, 4),
    observed_at TIMESTAMPTZ NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news_headlines (
    id BIGSERIAL PRIMARY KEY,
    source TEXT,
    title TEXT NOT NULL,
    url TEXT,
    published_at TIMESTAMPTZ,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fear_greed_index (
    id BIGSERIAL PRIMARY KEY,
    value INTEGER NOT NULL,
    classification TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL UNIQUE,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
