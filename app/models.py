from sqlalchemy import (
    Column, String, Text, Integer, ForeignKey,
    UniqueConstraint
)
<<<<<<< HEAD
from sqlalchemy.dialects.postgresql import UUID, JSON, TIMESTAMP
=======
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func, text

Base = declarative_base()

# ---------- MASTER ----------
class Sport(Base):
    __tablename__ = "sports"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_code = Column(Text, nullable=False, unique=True)  # e.g., motorsport, combat, football
    name = Column(Text, nullable=False)
<<<<<<< HEAD
    meta = Column("metadata", JSON)
=======
    info = Column(JSONB)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

    tours = relationship("Tour", back_populates="sport")

# ---------- CORE ENTITIES ----------
class Tour(Base):
    __tablename__ = "tours"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

    sport = relationship("Sport", back_populates="tours")
    years = relationship("TourYear", back_populates="tour")

class TourYear(Base):
    __tablename__ = "tour_years"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    tour_id = Column(UUID(as_uuid=True), ForeignKey("tours.id"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))
<<<<<<< HEAD
=======

>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    tour = relationship("Tour", back_populates="years")

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    tour_year_id = Column(UUID(as_uuid=True), ForeignKey("tour_years.id"), nullable=False)
    name = Column(Text, nullable=False)
    start_date = Column(TIMESTAMP(timezone=True))
    end_date = Column(TIMESTAMP(timezone=True))
    venue = Column(Text)
<<<<<<< HEAD
    meta = Column("metadata", JSON)
=======
    info = Column(JSONB)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name = Column(Text, nullable=False)
<<<<<<< HEAD
    meta = Column("metadata", JSON)
=======
    info = Column(JSONB)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    name = Column(Text, nullable=False)
    date_of_birth = Column(TIMESTAMP(timezone=True))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
<<<<<<< HEAD
    meta = Column("metadata", JSON)
=======
    info = Column(JSONB)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

# ---------- PARTICIPATION ----------
class EventParticipant(Base):
    __tablename__ = "event_participants"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))  # event_participant_id
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    role = Column(Text)  # team|player|driver|fighter|coach
<<<<<<< HEAD
    meta = Column("metadata", JSON)
=======
    info = Column(JSONB)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

# ---------- ROUNDS ----------
class Round(Base):
    __tablename__ = "rounds"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    code = Column(Text, nullable=False, unique=True)  # PRACTICE|QUALIFYING|RACE|GROUP|SEMI|FINAL
    name = Column(Text, nullable=False)
    round_no = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

class EventRound(Base):
    __tablename__ = "event_rounds"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))  # event_round_id
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    round_id = Column(UUID(as_uuid=True), ForeignKey("rounds.id"), nullable=False)
    parent_round_id = Column(UUID(as_uuid=True), ForeignKey("event_rounds.id"))
    order_in_parent = Column(Integer)
<<<<<<< HEAD
    meta = Column("metadata", JSON)
=======
    info = Column(JSONB)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))

# ---------- SCORES ----------
class Score(Base):
    __tablename__ = "scores"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    sports_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    event_round_id = Column(UUID(as_uuid=True), ForeignKey("event_rounds.id"))
    event_participant_id = Column(UUID(as_uuid=True), ForeignKey("event_participants.id"), nullable=False)
    metric_key = Column(Text, nullable=False)      # lap_time_ms|KD|SIG|goals|cards...
<<<<<<< HEAD
    metric_value = Column(JSON, nullable=False)
=======
    metric_value = Column(JSONB, nullable=False)
>>>>>>> 70f9b5e61fd5c4f2698d523fa425b1d481d92c75
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True))
