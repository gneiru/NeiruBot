from modules import dotenv
import pymongo

client = pymongo.MongoClient(dotenv.mongo_uri)

database = client.coin
aqwDB = client.aqw

