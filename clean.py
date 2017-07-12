#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(c) Vijay Saraswat 2017
All rights reserved

Cleaning voter data for Putnam County. Data extracted from pdf using tika, gives us a line of fields, separated by spaces. Of course some of the fields have spaces in them as well. So need to reconstruct fields. 

Note that the extraction is imperfect. The Town Ward/Dist field appears displaced within the line, not separated from the previous field by a space. We separate it out using the abbreviation of the town (e.g. CA) for now.

Also sometimes the line is actually split over multiple lines and needs to be assembled first. We need a human-in-the-loop solution for this. Basically the human should classify some lines as "ignored", e.g. lines containing operator information, such as |User: ANDREAB Station: BOE-03|. Sometimes lines to be ignored have changing data so we need to match them with a pattern. If the user determines the data is not tbe ignored, then we should look to concatenate the data into one line. So we will need to figure out if a line is a fragment, and also when enough fragments have been combined to form a line.

The fields are:

Town Ward/Dist	xx/yyy/zzz xx = 2 letter code, e.g. CA. yyy, zzz 3 digits. e.g. CA/000/001
Voter ID        8-digit number
Name		<LastName>, <FirstName> [<Initial>] [<Suffix>]
Street Address	Text, e.g. |10 Croton Falls Road|
City            city and zip code, e.g. |MAHOPAC 10541-1617|
AFF	        |DEM| (and |REP|?)
Phone		(xxx) yyy-zzzz or - or blank
Sex	        |M| or |F|
Date of Birth	mm/dd/yyyy
Registered	mm/dd/yyyy
Status          |Active| or |Active ADMIN|
"""
import re

class Voters:
    "Representation of the data for a voter."
    def __init__(self, town_ward, voterid, name, address, city, zip, aff,
                 phone, sex, dob, registered, status):
        self.town_ward = town_ward
        self.voterid = voterid
        self.name = name
        self.address = address
        self.city = city
        self.zip = zip
        self.affiliation=aff
        self.phone = phone
        self.sex = sex
        self.dob = dob
        self.registered = registered
        self.status = status
    def __repr__(self):
        return "<Voter {}>".format(self.name)
    def __str__(self):
        return "<Voter {}>".format(self.name)
    def csv(self, sep='\#'):
        tw = self.town_ward
        dob = self.dob
        reg = self.registered
        return sep.join(['/'.join([tw['town'], tw['ward'], tw['district']]),
                         self.voterid, self.name, self.address,
                         self.city, self.zip, self.affiliation, self.phone, self.sex,
                         date_to_str(dob), date_to_str(month), self.status])
    # end Voter
    
def date_to_string(date):
    return '/'.join(['{0:02d}'.format(date['month']),
                     '{0:02d}'.format(date['day']),
                     '{0:04d}'.format(date['year'])])
                         
    

def clean(line, town='CA', city_in=' (MAHOPAC|CARMEL|PUTNAM VALLEY) '):
    "Clean the data obtained from running tika on a pdf containing voter records"
    pre, town, ward, district, post=re.split("(" + town + ")/(\d{3})/(\d{3})", line)
    r_town_ward={'town':town, 'ward':ward, 'district':district}

    x=re.split(AFFS, pre+post)
    assert len(x)==3, 'pre, aff, post |' + str(x) + '|'
    pre, aff, post = x
    r_aff=aff

    x=re.split("(\d{8})", pre)
    assert len(x)==3, print('empty, voterid, rest' + str(x))
    empty, voterid, rest = x
    r_voterid=voterid

    x=re.split("("+ city_in+")", rest)
    assert len(x)==4, print('name_add, city, zip ' + str(x))
    name_add, city, ignore, zip = x
    r_city=city
    r_zip=zip

    x=re.split("\W([0-9]+)\W", name_add)
    assert len(x) >=3, print('name, num, add ' + str(x))
    r_name=x[0].strip()
    r_address=' '.join(x[1:])

    rx = re.split( '([^MF]*)(M|F)\W*' + MMDDYYYY + '\W*' + MMDDYYYY +'\W*', post)
    ignore, phone, sex, dob, reg_date, status = rx
    r_phone=phone.strip()
    r_sex=sex

    ignore, month, day, year, ignore = re.split('([0-9]{2})/([0-9]{2})/([0-9]{4})', dob)
    r_dob={'month':int(month), 'day':int(day), 'year':int(year)}
    ignore, month, day, year, ignore = re.split('([0-9]{2})/([0-9]{2})/([0-9]{4})', reg_date)
    r_registered={'month':int(month), 'day':int(day), 'year':int(year)}
    r_status=status.strip()

    return Voter(r_town_ward, r_voterid, r_name, r_address, r_city, r_zip, r_aff, r_phone,
                 r_sex, r_dob, r_registered, r_status)


TOWNS = 'PATTERSON|CARMEL|KENT|PHILIPSTOWN|PUTNAM VALLEY|SOUTHEAST'
GENDER = 'M|F'
MMDDYYYY = '([0-9]{2}/[0-9]{2}/[0-9]{4})'
AFFS = '\W(DEM|REP|BLK|CON|IND)\W'
Voter_ID = '\d{8}'
LINE = ""

IGNORES = [
    'Ward/Dist Sex Date of Birth Registered Status',
    'CityVoter ID Name Street Address AFF Phone',
    'Party of DEM',
    'Voter Status of A - Active',
    'Ordered by Town/Ward/District, Street Address',
    'Break on Town/Ward/District',
    'Report Criteria:',
    'TEAM SQL Version 6.7.3 Copyright © NTS Data Services, LLC.',
    'r_avtrcd',
    'Town',
    'WEBCORRECT'
    ]

IGNORE_PATTERNS = [
    '(' + TOWNS+',\WDistrict \d*)',
    '(Putnam County Board of Elections)',
    '(Town of:)',
    '(Detailed Voter Master Call List'),
    '(Voters Reported)',
    '(User:\W\w*\W Station: BOE-)',
    ]

def ignore(line):
    if line in IGNORES:
        return True
    for pat in IGNORE_PATTERNS:
        if len(re.split(pat, line)) > 1:
            return True
    return False

def process_file(fn, town='CA'):
    results=[]
    result={}
    with open(fn) as fp:
        for line in fp:
            line = line.strip()
            if line == '':
                continue
            if line == 'ADMIN':
                if 'status' in result:
                    result['status'] = result['status'] + ' ADMIN'
                continue
            if len(re.split('( DEM )', line)) < 2:
                if not ignore(line):
                    print('Ignoring |' + line + '|')
                continue
            #TODO: Figure out how to concatenate partial lines
            result = clean(line, town)
            results.append(result)
    return results

def write_json(data, fn):
    with open(fn, 'w') as fp:
        json.dump(result, fp, ensure_ascii=False, indent=4, sort_keys=True)

def extract_field_containing(records, field_name, value):
    "This code expects every record to have a field_name field."
    return [ r for r in records if value in r[field_name]]

