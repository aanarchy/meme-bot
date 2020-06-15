import os
from pymongo import MongoClient
from waffle.config import CONFIG

CONFIG = CONFIG['database']

db = MongoClient(CONFIG['uri'])


def get_collection(collection_name):
    return getattr(db, collection_name)


def add(collection_name, items):
    collection = get_collection(collection_name)
    if isinstance(items, list):
        collection.insert_many(items)
    else:
        collection.insert_one(items)


def remove(collection_name, key, value, single=False):
    collection = get_collection(collection_name)
    if single:
        return collection.delete_one({key: value})
    else:
        return collection.delete_many({key: value})


def get(collection_name, key, value, single=False):
    collection = get_collection(collection_name)
    if single:
        return collection.find_one({key: value})
    else:
        return collection.find({key: value})


def modify(collection_name, key, value, single=False):
    collection = get_collection(collection_name)
    if single:
        return collection.update_one({key: value})
    else:
        return collection.update_many({key: value})
