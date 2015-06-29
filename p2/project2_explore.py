#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

import project2_constants as c

#A list to contain the unique tags encountered in the file and how many times they appear
global_unique_tag_list = defaultdict(int)
file_name = c.osm_file_name

def key_type(element, keys):
    if element.tag == "tag":
        tagkey = element.attrib['k']
        if c.lower.search(tagkey):
            keys["lower"] += 1
        elif c.lower_colon.search(tagkey):
            keys["lower_colon"] += 1
        elif c.problemchars.search(tagkey):
            keys["problemchars"] += 1
            # print "Problem: ",tagkey
        else:
            # print "Other: ",tagkey
            keys["other"] += 1
        
    return keys

def get_user(element):
    #Extract the UID from the elements attributes dictionary
    if "uid" in element.attrib:
        return element.attrib["uid"]
    else:
        return None

def check_keys(filename):
    #use re to etsbalish the type of tag keys and id problem ones
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

def count_tags(filename):
    collection = {}
    parser = ET.iterparse(filename,("start", "end"))
    for event, elem in parser:
        if event == "start":
            collection[elem.tag] = collection.get(elem.tag,0) + 1
    return collection

def get_users(filename):
    #build list of users
    users = set()
    for _, element in ET.iterparse(filename):
        user = get_user(element)
        if user is not None:
            users.add(user)
    return users



def audit_street_type(street_types, street_type_count, street_name):
    #check if street_name ends in one of the recognised types Eg Street, Road etc
    m = c.street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in c.expected_street_type:
            street_types[street_type].add(street_name)
            street_type_count[street_type] += 1


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_possible_address(tag):
    if  tag.attrib['k'] == "name":
        name = tag.attrib["v"]
        name_end = c.street_type_re.search(name)
        return (name_end and (name_end.group() in c.expected_street_type))
    else:
        return False

def check_addresses(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    street_type_count = defaultdict(int)
    post_codes = defaultdict(int)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, street_type_count, tag.attrib['v'])
                if is_post_code(tag):
                    post_codes[tag.attrib['v']] += 1

    pprint.pprint(dict(post_codes))
    pprint.pprint(dict(street_type_count))
    return street_types



def check_possible_address(osmfile):
    #Test whether the name attrribute actually contains a street name
    osm_file = open(osmfile, "r")
    total_count = 0
    possible_count = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            total_count += 1
            for tag in elem.iter("tag"):
                if is_possible_address(tag):
                   possible_count += 1 
    print "Element Counts - Total: {} - Possible Address: {}".format(total_count,possible_count)


def track_global_keys(key):
    global_unique_tag_list[key] += 1


def analyse_tags(osmfile):
    osm_file = open(osmfile, "r")
    unique_tags = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                tagkey = tag.attrib["k"]
                tagval = tag.attrib["v"]
                track_global_keys(tagkey)
                unique_tags[elem.tag].add(tag.attrib["k"])
    return unique_tags

def test_tag_distribution():
    global_unique_tag_list.clear()
    tag_dist = analyse_tags(file_name)
    #pprint.pprint(tag_dist["node"])
    print
    #pprint.pprint(tag_dist["way"])
    print
    print "Global Tag Summary: ", len(global_unique_tag_list)
    pprint.pprint(dict(global_unique_tag_list),width=-1)


def test_street_names():
    st_types = check_addresses(file_name)
    pprint.pprint(dict(st_types))

def test_check_keys():
    keys = check_keys(file_name)
    pprint.pprint(keys)
    pprint

def test_count_tags():
    tags = count_tags(file_name)
    pprint.pprint(tags)

def test_users():
    users = get_users(file_name)
    pprint.pprint(users)
    print "Number of users: ",len(users)
    
def test_check_possible_address():
    check_possible_address(file_name)

if __name__ == "__main__":
    # test_count_tags()
    #test_check_keys()
    # test_users()
    #test_street_names()
    # test_check_possible_address()
    test_tag_distribution()