from pymongo import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
import os

# ✅ Access secrets from Replit using os.environ
username = quote_plus(os.environ['MONGO_USERNAME'])
password = quote_plus(os.environ['MONGO_PASSWORD'])
cluster = os.environ['MONGO_CLUSTER']

# ✅ Construct URI using single quotes
uri = f'mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=CourseBuilderCluster'

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['CourseBuilderDB']
users_collection = db['users']
plans_collection = db['plans']
def get_user_plans(username):
  return list(plans_collection.find({"username": username}))
