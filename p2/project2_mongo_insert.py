import json
import project2_constants as c

def insert_data(data, db):
    for a in data:
        db.capetown.insert(a)


if __name__ == "__main__":
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.osm
    db.capetown.drop()

    print "Importing JSON files to Mongo"
    print "No of records in capetown collection before import: ",db.capetown.count()
    data = []
    with open(c.json_file_name) as f:
        for line in f:
            data.append(json.JSONDecoder().decode(line))
        insert_data(data, db)
        # print db.capetown.find_one()
    print "No of records in capetown collection after import: ",db.capetown.count()
    
