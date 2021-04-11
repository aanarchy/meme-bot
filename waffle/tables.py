from sqlalchemy import Table, Integer, String, Column, DateTime, PickleType
import waffle.database

metadata = waffle.database.metadata

TasksTable = Table(
    "tasks",
    metadata,
    Column("guild_id", Integer),
    Column("message_id", Integer, primary_key=True),
    Column("channel_id", Integer),
    Column("time", DateTime, nullable=False),
    Column("function", String(32), nullable=False),
    Column("user_id", Integer),
)
