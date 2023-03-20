from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

try:
    engine = create_engine(
        "postgresql://postgres:postgres@localhost:5001/file_upload",
        echo=False
    )
    session = sessionmaker(bind=engine)()
    base = declarative_base()

except Exception as e: print(e)