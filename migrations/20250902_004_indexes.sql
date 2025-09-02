-- SPORTS
CREATE INDEX IF NOT EXISTS idx_sports_code ON sports(sports_code);

-- TOURS
CREATE INDEX IF NOT EXISTS idx_tours_sports_id ON tours(sports_id);

-- TOUR YEARS
CREATE INDEX IF NOT EXISTS idx_tour_years_sports_id ON tour_years(sports_id);
CREATE INDEX IF NOT EXISTS idx_tour_years_tour_id ON tour_years(tour_id);

-- EVENTS
CREATE INDEX IF NOT EXISTS idx_events_sports_id ON events(sports_id);
CREATE INDEX IF NOT EXISTS idx_events_tour_year_id ON events(tour_year_id);

-- TEAMS
CREATE INDEX IF NOT EXISTS idx_teams_sports_id ON teams(sports_id);

-- PLAYERS
CREATE INDEX IF NOT EXISTS idx_players_sports_id ON players(sports_id);
CREATE INDEX IF NOT EXISTS idx_players_team_id ON players(team_id);

-- EVENT PARTICIPANTS
CREATE INDEX IF NOT EXISTS idx_event_participants_sports_id ON event_participants(sports_id);
CREATE INDEX IF NOT EXISTS idx_event_participants_event_id ON event_participants(event_id);

-- ROUNDS
CREATE INDEX IF NOT EXISTS idx_rounds_sports_id ON rounds(sports_id);

-- EVENT ROUNDS
CREATE INDEX IF NOT EXISTS idx_event_rounds_sports_id ON event_rounds(sports_id);
CREATE INDEX IF NOT EXISTS idx_event_rounds_event_id ON event_rounds(event_id);
CREATE INDEX IF NOT EXISTS idx_event_rounds_round_id ON event_rounds(round_id);

-- SCORES
CREATE INDEX IF NOT EXISTS idx_scores_sports_id ON scores(sports_id);
CREATE INDEX IF NOT EXISTS idx_scores_event_id ON scores(event_id);
CREATE INDEX IF NOT EXISTS idx_scores_event_round_id ON scores(event_round_id);
CREATE INDEX IF NOT EXISTS idx_scores_event_participant_id ON scores(event_participant_id);
