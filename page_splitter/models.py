from sqlalchemy import Column, Integer, String, DateTime
from page_splitter.db_connection import base, engine


class PageSplitter(base):
    __tablename__ = 'page_splitter'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    fetch_time = Column(DateTime, nullable=False)
    status = Column(String(64), nullable=True)
    error = Column(String(128), nullable=True)
    submission_time = Column(DateTime, nullable=True)


base.metadata.create_all(engine)