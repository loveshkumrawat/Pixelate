from sqlalchemy import Column, Integer, String, DateTime
from db_connection_for_file_upload import base,engine

class File(base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    file_path = Column(String(128), nullable=False)
    uploaded_time = Column(DateTime, nullable=False)

base.metadata.create_all(engine)