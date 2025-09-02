-- sports table
CREATE TABLE sports (
    id UUID DEFAULT UUID_STRING() PRIMARY KEY,
    sports_code STRING NOT NULL UNIQUE,
    name STRING NOT NULL,
    metadata VARIANT,
    created_at TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_TZ
);
-- Enable required extension for UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ======================
-- SPORTS TABLE
-- ======================
DROP TABLE IF EXISTS sports CASCADE;
CREATE TABLE sports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sports_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

-- ======================
-- TOURS TABLE
-- ======================
DROP TABLE IF EXISTS tours CASCADE;
CREATE TABLE tours (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sports_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    tour_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

-- ======================
-- TOUR YEARS TABLE
-- ======================
DROP TABLE IF EXISTS tour_years CASCADE;
CREATE TABLE tour_years (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tour_id UUID NOT NULL REFERENCES tours(id) ON DELETE CASCADE,
    year INT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ,
    UNIQUE(tour_id, year)
);

-- ======================
-- EVENTS TABLE
-- ======================
DROP TABLE IF EXISTS events CASCADE;
CREATE TABLE events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tour_year_id UUID NOT NULL REFERENCES tour_years(id) ON DELETE CASCADE,
    event_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

-- ======================
-- TEAMS TABLE
-- ======================
DROP TABLE IF EXISTS teams CASCADE;
CREATE TABLE teams (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sports_id UUID NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    team_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

-- ======================
-- PLAYERS TABLE
-- ======================
DROP TABLE IF EXISTS players CASCADE;
CREATE TABLE players (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    player_code TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

-- ======================
-- EVENT PARTICIPANTS TABLE
-- ======================
DROP TABLE IF EXISTS event_participants CASCADE;
CREATE TABLE event_participants (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    player_id UUID REFERENCES players(id) ON DELETE SET NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ,
    CHECK (
        (team_id IS NOT NULL AND player_id IS NULL)
        OR (team_id IS NULL AND player_id IS NOT NULL)
    )
);

-- ======================
-- ROUNDS TABLE
-- ======================
DROP TABLE IF EXISTS rounds CASCADE;
CREATE TABLE rounds (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    round_number INT NOT NULL,
    name TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ,
    UNIQUE(event_id, round_number)
);

-- ======================
-- EVENT ROUNDS TABLE
-- ======================
DROP TABLE IF EXISTS event_rounds CASCADE;
CREATE TABLE event_rounds (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    round_id UUID NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES event_participants(id) ON DELETE CASCADE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);

-- ======================
-- SCORES TABLE
-- ======================
DROP TABLE IF EXISTS scores CASCADE;
CREATE TABLE scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_round_id UUID NOT NULL REFERENCES event_rounds(id) ON DELETE CASCADE,
    score_value NUMERIC NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);
