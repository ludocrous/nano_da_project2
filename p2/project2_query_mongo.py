#!/usr/bin/env python

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.osm
    return db

def make_user_address_pipeline():
    pipeline = [{"$match": { "address" : {"$exists" : True}}}, 
		{"$project" : {"created.user" : 1, "_id" : 0}},
		{"$group" : {"_id" : "$created.user", "count" : {"$sum" : 1}}}, 
		{"$sort" : {"count" : -1}}]
    return pipeline


def make_popular_amenity_pipeline():
    pipeline = [{"$match": { "amenity" : {"$exists" : True}}}, 
		{"$group" : {"_id" : "$amenity", "count" : {"$sum" : 1}}}, 
		{"$sort" : {"count" : -1}}]
    return pipeline


def make_pipeline():
    pipeline = [{"$match": { "address" : {"$exists" : True}}}]
    return pipeline

def aggregate(db, pipeline):
	result = db.capetown.aggregate(pipeline)
	return result

if __name__ == '__main__':
    db = get_db('osm')
    pipeline = make_popular_amenity_pipeline()
    result = list(aggregate(db, pipeline))
    import pprint
    pprint.pprint(result)
    