import os
from pymongo import MongoClient
import waffle.config

CONFIG = waffle.config.CONFIG['database']

if not CONFIG['uri']:
    if os.environ.get('MONGODB_URI'):
        CONFIG['uri'] = os.environ.get('MONGODB_URI')
    else:
        CONFIG['uri'] = 'mongodb://localhost:27017/'

client = MongoClient(CONFIG['uri'])


def get_collection(collection_name, database):
    return client[database][collection_name]


def add(database_name, collection_name, items):
    collection = client[database_name][collection_name]
    if isinstance(items, list):
        collection.insert_many(items)
    else:
        collection.insert_one(items)


def remove(database_name, collection_name, key, value, single=False):
    collection = client[database_name][collection_name]
    if single:
        return collection.delete_one({key: value})
    else:
        return collection.delete_many({key: value})


def get(database_name, collection_name, key, value, single=False):
    collection = client[database_name][collection_name]
    if single:
        return collection.find_one({key: value})
    else:
        return collection.find({key: value})


def modify(database_name, collection_name, key, value, single=False):
    collection = client[database_name][collection_name]
    if single:
        return collection.update_one({key: value})
    else:
        return collection.update_many({key: value})
