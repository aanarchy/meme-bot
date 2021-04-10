from sqlalchemy import Table, Integer, String, Column, DateTime
import waffle.database

metadata = waffle.database.metadata

TasksTable = Table(
    "tasks",
    metadata,
    Column("channel_id", Integer),
    Column("message_id", Integer, primary_key=True),
    Column("time", DateTime, nullable=False),
    Column("function", String(60), nullable=False),
    Column("kwargs", String(50), nullable=False),
)
