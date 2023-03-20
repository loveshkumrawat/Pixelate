from sqlalchemy import Column, Integer, String, DateTime
from db_connection_for_page_splitter import base, engine


class PageSplitter(base):
    __tablename__ = 'pageSplitter'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    fetch_time = Column(DateTime, nullable=False)
    status = Column(String(64), nullable=True)
    error = Column(String(128), nullable=True)
    submission_time = Column(String(DateTime), nullable=True)


base.metadata.create_all(engine)