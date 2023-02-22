from modules import dotenv
import pymongo

client = pymongo.MongoClient(dotenv.mongo_uri)

database = client.coin
twtDB = client.aqw

