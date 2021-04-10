import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
import waffle.config

CONFIG = waffle.config.CONFIG["database"]

engine = create_async_engine(CONFIG["uri"], connect_args={"check_same_thread": False})
metadata = sa.MetaData()
