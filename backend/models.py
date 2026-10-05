from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from backend.database import Base

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, index=True)  # Session UUIDv4
    account_id = Column(String(64), index=True, nullable=False)
    ip_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(32), default="active")  # "active" or "quarantined"

class TelemetryEventModel(Base):
    __tablename__ = "telemetry_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), index=True, nullable=False)
    event_type = Column(String(64), nullable=False)
    flight_time = Column(Float, nullable=True)
    dwell_time = Column(Float, nullable=True)
    jerk = Column(Float, nullable=True)
    route = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ClusterLogModel(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, index=True, nullable=False)
    node_count = Column(Integer, nullable=False)
    modularity_q = Column(Float, nullable=False)
    reasons_json = Column(Text, nullable=True)
    status = Column(String(32), default="quarantined")
    quarantined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))