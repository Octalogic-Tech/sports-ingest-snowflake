-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- MASTER / REFERENCE
DROP TABLE IF EXISTS sports CASCADE;
CREATE TABLE sports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

-- CORE ENTITIES
DROP TABLE IF EXISTS tours CASCADE;
CREATE TABLE tours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

DROP TABLE IF EXISTS tour_years CASCADE;
CREATE TABLE tour_years (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    tour_id UUID NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

DROP TABLE IF EXISTS events CASCADE;
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    tour_year_id UUID NOT NULL,
    name TEXT NOT NULL,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    venue TEXT,
    metadata JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

DROP TABLE IF EXISTS teams CASCADE;
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    name TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

DROP TABLE IF EXISTS players CASCADE;
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    name TEXT NOT NULL,
    date_of_birth TIMESTAMPTZ,
    team_id UUID,
    metadata JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

-- PARTICIPATION
DROP TABLE IF EXISTS event_participants CASCADE;
CREATE TABLE event_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    event_id UUID NOT NULL,
    team_id UUID,
    player_id UUID,
    role TEXT,
    metadata JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

-- ROUNDS
DROP TABLE IF EXISTS rounds CASCADE;
CREATE TABLE rounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    round_no INT,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

DROP TABLE IF EXISTS event_rounds CASCADE;
CREATE TABLE event_rounds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    event_id UUID NOT NULL,
    round_id UUID NOT NULL,
    parent_round_id UUID,
    order_in_parent INT,
    metadata JSON,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);

-- SCORES
DROP TABLE IF EXISTS scores CASCADE;
CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sports_id UUID NOT NULL,
    event_id UUID NOT NULL,
    event_round_id UUID,
    event_participant_id UUID NOT NULL,
    metric_key TEXT NOT NULL,
    metric_value JSON NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ
);
