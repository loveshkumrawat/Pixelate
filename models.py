from Connection.Postgres_Database_Connection import  engine, base
from sqlalchemy import Column, Integer, String, DateTime


class File(base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    file_path = Column(String(128), nullable=False)
    uploaded_time = Column(DateTime, nullable=False)
    submitted_time = Column(DateTime)


base.metadata.create_all(engine)
