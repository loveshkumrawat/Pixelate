from sqlalchemy import Column, Integer, String, DateTime
from db_connection_for_text_extractor import base, engine


class TextExtractor(base):
    __tablename__ = 'textExtractor'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    fetch_time = Column(DateTime, nullable=True)
    status = Column(String(64), nullable=True)
    error = Column(String(128), nullable=True)
    submission_time = Column(String(DateTime), nullable=True)


base.metdata.create_all(engine)
