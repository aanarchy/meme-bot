from sqlalchemy import Table, Integer, String, Column, DateTime, PickleType
import waffle.database

metadata = waffle.database.metadata

TasksTable = Table(
    "tasks",
    metadata,
    Column("channel_id", Integer),
    Column("message_id", Integer, primary_key=True),
    Column("time", DateTime, nullable=False),
    Column("function", String(32), nullable=False),
)
