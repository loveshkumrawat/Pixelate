from sqlalchemy import Column, Integer, String, DateTime,TEXT
from metadata_extractor.db_connection import base, engine


class MetaDataExtractor(base):
    __tablename__ = 'meta_data_extractor'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    fetch_time = Column(DateTime, nullable=False)
    status = Column(String(64), nullable=True)
    error = Column(String(128), nullable=True)
    submission_time = Column(DateTime, nullable=True)


base.metadata.create_all(engine)
