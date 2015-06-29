#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import project2_constants as c


def check_street_type(street_name):
    m = c.street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in c.expected_street_type:
            if street_type in c.street_type_mapping:
                # This will apply the mapping specifically to deal with street type
                street_name = update_name(street_name,c.street_type_mapping)
    return street_name


def update_name(name, mapping):
    return name
    streettype = street_type_re.search(name)
    #Cannot use replace() as the likes of "Station St" would be corrupted
    #Therefore use rfind to find first instance from the right
    #Can be achieved by regular expression groups as well.
    pos = name.rfind(streettype.group()) 
    if pos > -1:
        name = name[:pos]+mapping[streettype.group()]
    return name

def process_key_value(node,key,value):
    if key in c.ignore_tag_list:
        return
    elif key in c.substitute_tags:
        key = c.substitute_tags[key]
        node[key] = value
    elif key in c.bump_tags:
        newkey = c.bump_tags[key]
        #Attempt to preserve orignal value
        value = key + " (" + value +")"
        node[newkey] = value
    elif c.lower_colon.search(key):
        keyarray = key.split(":")
        if keyarray[0] == "addr":
            #Ignore subclassification like addr:street:prefix 
            if len(keyarray) > 2:
                return
            if not "address" in node:
                node["address"] = {}
            if key == "addr:street":
                check_street_type(value)
            node["address"][keyarray[1]]=value
        else:
            node[key] = value
    elif c.lower.search(key):
        if key in c.created_keys:
            #collect all fields id'ed as created fields as a sub category to "created"
            if not "created" in node:
                node["created"] = {}
            node["created"][key] = value
        elif key in ["lat","lon"]: #Convert the lat and lon strings to floats and position in a list
            if not "pos" in node:
                node["pos"] = [None,None]
            node["pos"][(0 if key=="lat" else 1)]=(float(value)) #TODO Needs to be way more robust
        else:
            node[key] = value

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :

        #First process attributes of element itself
        for key,value in element.attrib.items():
            process_key_value(node,key,value)

        #Process any tag elements for k and v values    
        for tag in element.iter("tag"):
            process_key_value(node,tag.attrib["k"],tag.attrib["v"])

        #Process any "nd" elements for node_refs in "way" elements
        for tag in element.iter("nd"):
            if not "node_refs" in node:
                node["node_refs"] = []
            node["node_refs"].append(tag.attrib["ref"])

        node["type"] = element.tag
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # USing data dict, but if file sizes get vary large loading the entire set into memory is not good.
    data = []
    with codecs.open(c.json_file_name, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def process():
    data = process_map(c.osm_file_name, False)

if __name__ == "__main__":
    process()