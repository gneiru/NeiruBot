from dotenv import load_dotenv
import os

load_dotenv()

prefix = os.environ.get("PREFIX")
mongo_uri = os.environ.get("MONGO_URI")
token = os.environ.get("TOKEN")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token_key = os.environ.get("ACCESS_TOKEN_KEY")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")