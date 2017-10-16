#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(c) Vijay Saraswat 2017
All rights reserved
"""
import re
import csv
import json
from pprint import pprint
from json import JSONEncoder


THIS_YEAR=2017
def extract_fb_info(records):
    """
    records is a list of Voter records, pre-selected according to some criteria.
    Convert to the list of col names that FB expects in its input csv.
         phone,fn,ln,zip,ct,st,country,dob,doby,gen,age
    (The fields we can populate are:
       email,email,email,phone,phone,phone,madid,fn,ln,zip,ct,st,country,dob,doby,gen,age,uid
    For the formats for these fields, see https://www.facebook.com/business/help/606443329504150
    )
    """
    result = [
        {
            'phone': '' if r.tel_number == '' or r.tel_number == None else '1-('+ r.area_code+')-'+r.tel_number,
            'fn': r.name['first_name'], 'ln': r.name['last_name'],
            'zip': r.address['zip'], 'ct': r.address['city'], 'st':r.address['state'], 'country':'US',
            'dob': str(r.dob['month']) + '/' + str(r.dob['day']) + '/' + str(r.dob['year'])[2:4],
            'doby': r.dob['year'],
            'gen': r.sex,
            'age': THIS_YEAR-r.dob['year']
        }
        for r in records
        ]
    return result

def write_fb(fn, results):
    "Write out results into fn."
    with open(fn, 'w') as csvfile:
        fieldnames = ['phone','fn', 'ln', 'zip','ct','st','country','dob','doby','gen','age']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    
