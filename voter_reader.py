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

YYYYMMDD = '(\d{4})(\d{2})(\d{2})'
def non_empty_list(l, empty=''):
    for x in l:
        if x != empty:
            return True
    return False

def set_item(obj, attr, size, v):
    """
    The original idea was not to store empty fields. Now storing all fields, 
    checking for errors. Later passes will produce more abstract versions
    of the data.
    """
    if type(obj) is dict:
        obj[attr]=v
    else: 
        setattr(obj, attr, v)
    if type(size) is list:
        if not (type(v) is list and len(v)==len(size)):
            return set([('expected list of ' + len(size) + ' elements, of size ' + size)])
        devs = [('length error', attr, vv, s)
                for vv, s in zip(v, size)
                if len(vv) > s]
        return set(devs)
    return set() if len(v) <= size else set([('length error', attr, size, v)])

def set_patt(obj, attr, patt, v, must_have=False):
    "Check the value (it must exist), satisfies the pattern"
    if type(obj) is dict:
        obj[attr] = v
    else:
        setattr(obj, attr, v)
    if v == '':
        return set([('empty, expected patt', attr, patt, v)]) if must_have else set()
    test = re.fullmatch(patt, v)
    return set() if test != None else set([('match failed', attr, patt, v)]) 


def set_YYYYMMDD(obj, attr, v, must_have=False):
    if type(obj) is dict:
        obj[attr] = v
    else:
        setattr(obj, attr, v)
    if v == '':
        return set([('empty, expected YYYYMMDD', attr, v)]) if must_have else set()
    test=re.fullmatch(YYYYMMDD, v)
    if test == None:
        return set([('date YYYYMMDD error', attr, v)])
    ignore, year, month, day, ignore = re.split(YYYYMMDD, v)
    date =  {'year':int(year), 'month':int(month), 'day':int(day)}
    if type(obj) is dict:
        obj[attr] = date
    else:
        setattr(obj, attr, date)
    return set()

def set_history_codes(obj, attr, codes, bypass=True):
    if type(obj) is dict:
        obj[attr] = codes
    else:
        setattr(obj, attr, codes)
    "TODO: Check for failure of this pattern first"
    test = re.fullmatch('(\w{4})*', codes)
    if test == None:
        return set([('history code error', attr, codes)])
    codes = [{'year':x[3], 'type':x[1]} 
             for r in re.split('(\w{4})', codes) 
             if r !='' 
             for x in [re.split('(\w{2})', r)]]
    if type(obj) is dict:
        obj[attr] = codes
    else:
        setattr(obj, attr, codes)
    return set()


FORMAT_DEFINITION = {
    'file_name': 'NTS VTR EXPORT FILE FORMAT STANDARD.pdf',
    'date': '5/24/2007',
    'updated': '01/10/2008'
    }

SCHOOL_DISTRICT_CODES={
    '001': 'Mahopac School Dist.',
    '002': 'Carmel School Dist.',
    '003': 'Brewster School Dist.',
    '004': 'Lakeland School Dist.',
    '005': 'North Salem School Dist.',
    '006': 'Putnam Valley School Dist.',
    '007': 'Wappingers Falls School Dist.',
    '008': 'Pawling School Dist.',
    '009': 'Garrison School Dist.',
    '010': 'Haldane School Dist.'
    }
FIRE_DISTRICT_CODES={
    '001': 'Mahopac School Dept.',
    '002': 'Mahopac Falls Fire Dept.',
    '003': 'Carmel Fire Dept.',
    '004': 'Croton Falls Fire Dept.',    
    '005': 'Kent Fire Dept.',
    '006': 'Putnam Valley Fire Dept.',
    '007': 'Lake Carmel Fire Dept.',
    '008': 'Patterson Fire Dept.',
    '009': 'Putnam Lake Fire Dept.',
    '010': 'Garrison Fire Dept.',
    '011': 'Cold Spring Fire Dept.',
    '012': 'Continental Village Fire Dept.',
    '013': 'No. Highland Fire Dept.',
    '014': 'Brewster Fire Dept.'
    }
TOWN_CODES={
    'CA': 'Carmel',
    'KE': 'Kent',
    'PA': 'Patterson',
    'PH': 'Phillipston',
    'PV': 'Putnam Valley',
    'SE' : 'Southeast'
    }
LIBRARY_DISTRICT_CODES={
    '000': 'No Assigned Library Dist',
    '001': 'Mahopac Library Dist'
    }

# BLK=Blank
AFFILIATIONS={'BLK', 'CON', 'DEM', 'GRE', 'IND', 'LBT', 'OTH', 'REF', 'REP', 'WEP', 'WOR'}


class Voter:
    """Representation of the data for a voter in Putnam County, per Board of Elections.
       See FORMAT_DEFINITION for provenance.
       Received 07/10/2017 via email from Barbara Spofford at BoE in response to a FOIL.
    """
    def __init__(self,l):
        dev = set()
        dev |= set_item(self, 'voter_id',    15, l[0])              # 15 chars
        name={}
        dev |= set_item(name, 'first_name',  15, l[1])              # 15 chars
        dev |= set_item(name, 'middle_name', 15, l[2])              # 15 chars
        dev |= set_item(name, 'last_name',   20, l[3])              # 20 chars
        dev |= set_item(name, 'suffix',       4, l[4])              # 4 chars
        if name != {}:
            self.name = name

        addr={}
        dev |= set_item(addr, 'street_number', 8, l[5])             # 8 chars
        dev |= set_item(addr, 'half_code',     5, l[6])             # 5 chars ... "1/2"
        dev |= set_item(addr, 'street_name',  30, l[7])             # 30 chars
        dev |= set_item(addr, 'apt_number',   12, l[8])             # 12 chars
        dev |= set_item(addr, 'address_lines', [40, 40], l[9:11])   # 2 x 40 chars
        dev |= set_item(addr, 'city',         25, l[11])            # 25 chars
        dev |= set_item(addr, 'state',         2, l[12])            # 2 chars
        dev |= set_item(addr, 'zip',           5, l[13])            # 5 chars
        dev |= set_item(addr, 'zip_plus',      4, l[14])            # 4 chars
        if addr != {}:
            self.address = addr

        dev |= set_item(self, 'file_date', 15, l[15])               # 15 chars
        dev |= set_YYYYMMDD(self, 'dob', l[16])                     # YYYYMMDD=\d{4}\d{2}\d{2}

        dev |= set_patt(self, 'sex', 'M|F', l[17])                  # M|F
        dev |= set_item(self, 'eye',       3, l[18])                # 3 chars
        dev |= set_item(self, 'height',    [1,1], l[19:21])         # ft 1 char, inches 2 char
        dev |= set_patt(self, 'area_code', '\d{3}', l[21])          # 3 chars
        dev |= set_patt(self, 'tel_number', '(\d{3})?-(\d{4})?', l[22])   # \d{3}-\d{4}
        dev |= set_YYYYMMDD(self, 'reg_date', l[23])                # YYYYMMDD=\d{4}\d{2}\d{2}
        
        dev |= set_item(self, 'reg_source',    10, l[24])        # 10 chars
        dev |= set_item(self, 'filler',        20, l[25])        # 20 chars
        dev |= set_item(self, 'affiliation',    3, l[26])        # 3 chars 
        dev |= set_item(self, 'town',           3, l[27])        # 3 chars
        dev |= set_item(self, 'ward',           3, l[28])        # 3 chars
        dev |= set_item(self, 'dist',           3, l[29])        # 3 chars
        dev |= set_item(self, 'congress_dist',  3, l[30])        # 3 chars
        dev |= set_item(self, 'senatorial_dist',3, l[31])        # 3 chars
        dev |= set_item(self, 'assembly_dist',  3, l[32])        # 3 chars
        dev |= set_item(self, 'school_dist',    3, l[33])        # 3 chars
        dev |= set_item(self, 'county_dist',    3, l[34])        # 3 chars
        dev |= set_item(self, 'village_dist',   3, l[35])        # 3 chars
        dev |= set_item(self, 'fire_dist',      3, l[36])        # 3 chars
        dev |= set_item(self, 'lib_dist',       3, l[37])        # 3 chars
        dev |= set_patt(self, 'voter_status', 'A|I|P', l[38])    # A|I|P
        dev |= set_item(self, 'reason',        10, l[39])        # \w{10}
        dev |= set_patt(self, 'absentee',      'Y|N', l[40])     # Y|N

        mailing={}
        dev |= set_item(mailing, 'address', [40,40,40,40],l[41:45])  # 4 x 40
        dev |= set_item(mailing, 'city',    25, l[45])               # 25
        dev |= set_item(mailing, 'state',    2, l[46])               # 2
        dev |= set_patt(mailing, 'zip', '\d{5}', l[47])              # \d{5}
        dev |= set_patt(mailing, 'zip_plus', '\d{4}', l[48])         # \d{4}
        if mailing != {}:
            self.mailing = mailing

        absentee={}
        dev |= set_item(absentee, 'election_code', 4, l[49])           # 4
        dev |= set_item(absentee, 'code',          3, l[50])           # 3
        dev |= set_YYYYMMDD(absentee, 'application_received_date', l[51]) # YYYYMMDD
        absentee_add ={}
        dev |= set_item(absentee_add, 'add', [40,40,40,40], l[52:56])  # 4 x 40 chars
        dev |= set_item(absentee_add, 'city',    25, l[56])            # 25 chars
        dev |= set_item(absentee_add, 'state',    2, l[57])            # 2 chars
        dev |= set_patt(absentee_add, 'zip',  '\d{5}', l[58])          # 5 chars
        dev |= set_patt(absentee_add, 'zip_plus','\d{4}', l[59])       # 4 chars
        if absentee_add !={}:
            absentee['add'] = absentee_add
        dev |= set_YYYYMMDD(absentee, 'ballot_issued_date',      l[60])       
        dev |= set_YYYYMMDD(absentee, 'ballot_received_date',    l[61])     
        dev |= set_YYYYMMDD(absentee, 'ballot_re_issued_date',   l[62])    
        dev |= set_YYYYMMDD(absentee, 'ballot_re_received_date', l[63])  
        dev |= set_YYYYMMDD(absentee, 'expiration_date', l[64])          
        dev |= set_patt(absentee, 'eligible', 'Y|N', l[65])              # 'Y'/'N'
        dev |= set_item(absentee, 'ineligible_reason', 40, l[66])        # 40 chars
        if absentee != {}:
            self.absentee = absentee

        dev |= set_history_codes(self, 'history_codes', l[-2])      # should be 12 x 4-char codes
        # vj: hack for now, to work around bugs in rows
        self.deviations = dev
        
    def get_name(self):
        res = self.name['last_name'] + "," + self.name['first_name']
        if self.name['middle_name'] != '':
            res = res + ' ' + self.name['middle_name']
        if self.name['suffix'] != '':
            res = res + ' ' + self.name['suffix']
        return res

    def __repr__(self):
        return "<Voter {}, voter_id=...{}>".format(self.get_name(), self.voter_id[-4:])
    def __str__(self):
        return "<Voter {}, voter_id=...{}>".format(self.get_name(), self.voter_id[-4:])
    def validate(self):
        "Return list of all deviations against the spec."
        devs =[]
        devs = check_length(self, 'voter_id', 15)
        devs = check_length(self, 'first_name', 15)
        
    # end Voter


class VoterEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
    
def read_file(fn):
    results=[]
    rows=[]
    with open(fn, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            v = Voter(row)
            results.append(v)
            rows.append(row)
    return results, rows
        
        
def write_json(data, fn):
    with open(fn, 'w') as fp:
        json.dump(data, fp, cls=VoterEncoder,ensure_ascii=False, indent=4, sort_keys=True)


def print_errors_in_voting_records(results, raws):
    "(results, raws) obtained after a read_file(...)"
    for ind, (result, raw) in enumerate(zip(results,raws)):
        if result.deviations != set():
            pprint((ind, result, len(raw), result.deviations))
        
def voting_record(votes):
    "Given a voting record as a string 'GE09PE04', return the list of elections."
    if votes=='':
        return [{}]
    else:
        return [{'year':x[3], 'type':x[1]} 
                for r in re.split('(\w{4})', votes) 
                if r !='' 
                for x in [re.split('(\w{2})', r)]]
    
def generate_all_elections(rows):
    "rows is the list of input rows, where each row has been converted to a list by the csv reader."
    voting = [r[len(r)-2] for r in rows] # Since some records are erroneous, just get the second last entry
    codes = []
    for v in voting:
        codes.append(voting_record(v))
    x ={}
    for cs in codes:
        for c in cs:
            if 'year' in c:
                year = int(c['year'])
                if year in x:
                    x[year].add(c['type'])
                else: 
                    x[year]=set([c['type']])
    return x

            
            
def num_elections_since(year, elecs):
    num = 0
    if year > 95:
        while (year < 100):
            num = num + len(elecs[year])
            year = year+1
        year=0
        while (year < 18):
            num = num + len(elecs[year])
            year = year + 1
    else:
        while (year < 18):
            num = num + len(elecs[year])
            year = year +1
    return num
        
def voting_efficiency(votes, elecs):
    #votes = voting_record(votes)
    if len(votes)==0:
        return 0.0
    else:
        year = int(votes[-1]['year'])
        num = num_elections_since(year, elecs)
        return len(votes)/num

def avg_voting_efficiency_by_party(results, elecs, parties=['DEM', 'REP','BLK']):
    return [(x, float2(sum(l)/len(l)))
            for x in parties
            for l in [[voting_efficiency(r.history_codes, elecs) 
                       for r in results
                       if r.affiliation == x]]]

def rank_by_efficiency(results, elecs, bar=5):
    sorted([(x, float2(voting_efficiency(results[x].history_codes, elecs))) 
        for x in range(0,len(results))
            if len(results[x].history_codes) > bar], key=lambda x:-x[1])

def float2(x):
    return int(100*x)/100
