from supporting import env
from pymongo import MongoClient

try: client = MongoClient(f"mongodb://{env.MONGO_DB_HOST}:{env.MONGO_DB_PORT}/")
except: print('Connection refused')

database = client['metadata_extractor']
