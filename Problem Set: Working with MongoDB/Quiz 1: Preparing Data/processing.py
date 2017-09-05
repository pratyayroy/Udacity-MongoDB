#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set we'll work with another type of infobox data, audit it,
clean it and come up with a data model.

The task in this exercise is to parse the file, process only the fields that
are listed in the FIELDS dictionary as keys, and return a list of dictionaries
of cleaned values. 

The following things should be done:
- keys of the dictionary changed according to the mapping in FIELDS dictionary
- trim out redundant description in parenthesis from the 'rdf-schema#label'
  field, like "(spider)"
- if 'name' is "NULL" or contains non-alphanumeric characters, set it to the
  same value as 'label'.
- if a value of a field is "NULL", convert it to None
- if there is a value in 'synonym', it should be converted to an array (list)
  by stripping the "{}" characters and splitting the string on "|". Rest of the
  cleanup is up to you, e.g. removing "*" prefixes etc. If there is a singular
  synonym, the value should still be formatted in a list.
- strip leading and ending whitespace from all fields, if there is any
- the output structure should be as follows:

[ { 'label': 'Argiope',
    'uri': 'http://dbpedia.org/resource/Argiope_(spider)',
    'description': 'The genus Argiope includes rather large and spectacular spiders that often ...',
    'name': 'Argiope',
    'synonym': ["One", "Two"],
    'classification': {
                      'family': 'Orb-weaver spider',
                      'class': 'Arachnid',
                      'phylum': 'Arthropod',
                      'order': 'Spider',
                      'kingdom': 'Animal',
                      'genus': None
                      }
  },
  { 'label': ... , }, ...
]
"""

import csv
import pprint
import re
import json

DATAFILE = 'arachnid.csv'
FIELDS = {'rdf-schema#label': 'label',
          'URI': 'uri',
          'rdf-schema#comment': 'description',
          'synonym': 'synonym',
          'name': 'name',
          'family_label': 'family',
          'class_label': 'class',
          'phylum_label': 'phylum',
          'order_label': 'order',
          'kingdom_label': 'kingdom',
          'genus_label': 'genus'}
CLASSIFICATION = ['family', 'class', 'phylum', 'order', 'kingdom', 'genus']


def process_rdf(value):
    """
    this function processes the rdf-schema#label by removing redundant description in parenthesis
    :param value: the uncleaned rdf-schema#label
    :return: cleaned rdf-schema#label
    """
    pattern = re.compile(r"\([\w]+\)")  # the regex to detect redundant description in parenthesis
    return re.sub(pattern, "", value)


def process_name(value, label):
    """
    this function cleans the name field
    :param value: the uncleaned name
    :param label: the label which will override the name in-case it is Null or not alphanumeric
    :return: the cleaned name
    """
    non_alpha = re.compile(r"[\W]")
    if value == "NULL" or non_alpha.search(value):
        return label
    else:
        return value


def process_synonym(value):
    """
    this function returns the cleaned synonym values
    :param value: the uncleaned synonym
    :return: the cleaned and array-converted synonym
    """
    synonym_map = [('{', ''), ('}', ''), ('*', '')]
    for i, j in synonym_map:
        value = value.replace(i, j)  # trims the non-useful characters
    value = value.strip().split("|")  # creates the array to be returned
    return value


def process_file(filename, fields):
    """
    this function process the csv file, cleans it and returns a JSON entry
    :param filename: the name of the csv file
    :param fields: the fields which should be included in the JSON
    :return: the list containing the cleaned dictionary
    """
    process_fields = fields.keys()
    data = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for i in range(3):  # skipping the first 3 redundant lines of the csv
            reader.next()
        for line in reader:
            temp = {}  # the dictionary to contain each converted row of the csv
            classification = {}  # the dictionary to form a dictionary of dictionary of the selected keys
            for element in line:  # data wrangling
                if element in process_fields:
                    if element == "rdf-schema#label":
                        val = process_rdf(line[element]).strip()
                    elif element == "name":
                        val = process_name(line[element], temp["label"]).strip()
                    elif line[element] == "NULL":
                        val = None
                    elif element == "synonym":
                        val = process_synonym(line[element])
                    else:
                        val = line[element].strip()
                    if FIELDS[element] in CLASSIFICATION:
                        classification[FIELDS[element]] = val
                    else:
                        temp[FIELDS[element]] = val
            temp["classification"] = classification
            data.append(temp)
    return data


def test():
    """
    the driver function
    :return: nothing
    """
    data = process_file(DATAFILE, FIELDS)
    file_out = "{}.json".format(DATAFILE.split(".")[0])  # creating the JSON file
    with open(file_out, "w") as fo:
        fo.write(json.dumps(data) + "\n")
    print
    "Your first entry:"
    pprint.pprint(data[0])

    first_entry = {
        "synonym": None,
        "name": "Argiope",
        "classification": {
            "kingdom": "Animal",
            "family": "Orb-weaver spider",
            "order": "Spider",
            "phylum": "Arthropod",
            "genus": None,
            "class": "Arachnid"
        },
        "uri": "http://dbpedia.org/resource/Argiope_(spider)",
        "label": "Argiope",
        "description": "The genus Argiope includes rather large and spectacular spiders that often have a strikingly "
                       "coloured abdomen. These spiders are distributed throughout the world. Most countries in "
                       "tropical or temperate climates host one or more species that are similar in appearance. "
                       "The etymology of the name is from a Greek name meaning silver-faced."
    }

    assert len(data) == 76
    assert data[0] == first_entry
    assert data[17]["name"] == "Ogdenia"
    assert data[48]["label"] == "Hydrachnidiae"
    assert data[14]["synonym"] == ["Cyrene Peckham & Peckham"]


if __name__ == "__main__":
    test()
