import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# =========================
# MASTER / REFERENCE
# =========================
class Sports(Base):
    __tablename__ = "sports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_code = Column(Text, nullable=False, unique=True)  # e.g., motorsport, combat
    name = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


# =========================
# CORE ENTITIES
# =========================
class Tours(Base):
    __tablename__ = "tours"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


class TourYears(Base):
    __tablename__ = "tour_years"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    tour_id = Column(UUID(as_uuid=True), ForeignKey("tours.id"), nullable=True)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


class Events(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_id = Column(Text, unique=True, nullable=False)  # external API ID
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    tour_year_id = Column(UUID(as_uuid=True), ForeignKey("tour_years.id"), nullable=False)
    name = Column(Text, nullable=False)
    sport_type = Column(Text)  # supercross | motocross | supermotocross
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    venue = Column(Text)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


class Teams(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


class Players(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name = Column(Text, nullable=False)
    date_of_birth = Column(DateTime(timezone=True))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


# =========================
# PARTICIPATION
# =========================
class EventParticipants(Base):
    __tablename__ = "event_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    role = Column(Text)  # team|player|driver|fighter|coach
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


# =========================
# ROUNDS
# =========================
class Rounds(Base):
    __tablename__ = "rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    code = Column(Text, nullable=False, unique=True)  # PRACTICE|QUALIFYING|RACE
    name = Column(Text, nullable=False)
    round_no = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


class EventRounds(Base):
    __tablename__ = "event_rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    round_id = Column(UUID(as_uuid=True), ForeignKey("rounds.id"), nullable=False)
    parent_round_id = Column(UUID(as_uuid=True), ForeignKey("event_rounds.id"))
    order_in_parent = Column(Integer)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


# =========================
# SCORES
# =========================
class Scores(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    event_round_id = Column(UUID(as_uuid=True), ForeignKey("event_rounds.id"))
    event_participant_id = Column(UUID(as_uuid=True), ForeignKey("event_participants.id"), nullable=False)
    metric_key = Column(Text, nullable=False)  # lap_time_ms|KD|SIG|goals|cards...
    metric_value = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
