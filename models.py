from connection.postgres_database_connection import engine, base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table


class File(base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    file_path = Column(String(128), nullable=False)
    uploaded_time = Column(DateTime, nullable=False)



#
# JsonSplit = Table('jsonsplit', base.metadata,
#     Column('file_id',Integer, ForeignKey('files.id')),
#     Column('submitted_time',DateTime),
#     Column('status',String),
#     Column('execution_time',DateTime)
#
# )
# PageSplit= Table('pagesplit', base.metadata,
#     Column('file_id',Integer, ForeignKey('files.id')),
#     Column('submitted_time',DateTime),
#     Column('status',String),
#     Column('execution_time',DateTime)
#
# )

base.metadata.create_all(engine)