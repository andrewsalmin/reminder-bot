CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    remind_at TIMESTAMPTZ NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reminders_time_sent ON reminders(remind_at, sent);

ALTER TABLE reminders
ADD CONSTRAINT remind_at_future CHECK (sent = TRUE OR remind_at > NOW() - INTERVAL '1 minute')
NOT VALID;