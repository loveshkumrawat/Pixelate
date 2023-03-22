from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:5000/')
except:
    print('connection not successful')

database = client['text_extractor']

