from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

try:
    engine = create_engine(
        "postgresql://postgres:Welcome4$@localhost:5012/image_upload",
        echo=False
    )
    session = sessionmaker(bind=engine)()
    base = declarative_base()

except Exception as e: print(e)