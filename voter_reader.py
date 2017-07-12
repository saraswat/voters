#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(c) Vijay Saraswat 2017
All rights reserved
"""
import re
import csv
import json
from json import JSONEncoder

def non_empty_list(l, empty=''):
    for x in l:
        if x != empty:
            return True
    return False

def set_item(obj, attr, v, empty='', bypass=True):
    if not bypass:
        if type(v) is list and not non_empty_list(v, empty):
            return
        if v == empty:
            return
    if type(obj) is dict:
        obj[attr]=v
    else: 
        setattr(obj, attr, v)

def set_YYYYMMDD(obj, attr, date):
    if date == '':
        return
    ignore, year, month, day, ignore = re.split('(\d{4})(\d{2})(\d{2})',date)
    date =  {'year':int(year), 'month':int(month), 'day':int(day)}
    if type(obj) is dict:
        obj[attr] = date
    else:
        setattr(obj, attr, date)

def set_history_codes(obj, attr, codes, bypass=True):
    if not bypass:
        if not non_empty_list(codes):
            return
    codes = [{'year':x[3], 'type':x[1]} 
             for r in re.split('(\w{4})', codes) 
             if r !='' 
             for x in [re.split('(\w{2})', r)]]
    if type(obj) is dict:
        obj[attr] = codes
    else:
        setattr(obj, attr, codes)

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

AFFILIATIONS={'BLK', 'CON', 'DEM', 'GRE', 'IND', 'LBT', 'OTH', 'REF', 'REP', 'WEP', 'WOR'}


class Voter:
    """Representation of the data for a voter in Putnam County, per Board of Elections.
       See FORMAT_DEFINITION for provenance.
       Received 07/10/2017 via email from Barbara Spofford at BoE in response to a FOIL.
    """
    def __init__(self,l):
        set_item(self, 'voter_id', l[0])                  # 15 chars

        name={}
        set_item(name, 'first_name', l[1])                # 15 chars
        set_item(name, 'middle_name', l[2])               # 15 chars
        set_item(name, 'last_name', l[3])                 # 20 chars
        set_item(name, 'suffix', l[4])                    # 4 chars
        if name != {}:
            set_item(self, 'name', name)

        addr={}
        set_item(addr, 'street_number', l[5])             # 8 chars
        set_item(addr, 'half_code', l[6])                 # 5 chars ... "1/2"
        set_item(addr, 'street_name', l[7])               # 30 chars
        set_item(addr, 'apt_number', l[8])                # 12 chars
        set_item(addr, 'address_lines', l[9:11])          # 2 x 40 chars
        set_item(addr, 'city', l[11])                     # 25 chars
        set_item(addr, 'state', l[12])                    # 2 chars
        set_item(addr, 'zip', l[13])                      # 5 chars
        set_item(addr, 'zip_plus', l[14])                 # 4 chars
        if addr != {}:
            set_item(self, 'address', addr)       

        set_item(self, 'file_date', l[15])                # 15 chars
        set_YYYYMMDD(self, 'dob', l[16])                  # YYYYMMDD=\d{4}\d{2}\d{2}

        set_item(self, 'sex', l[17])                      # M|F
        set_item(self, 'eye', l[18])                      # 3 chars
        set_item(self, 'height', l[19:21])                # ft 1 char, inches 2 char
        set_item(self, 'area_code', l[21])                # 3 chars
        set_item(self, 'tel_number', l[22])               # \d{3}-\d{4}
        set_YYYYMMDD(self, 'reg_date', l[23])             # YYYYMMDD=\d{4}\d{2}\d{2}
        
        set_item(self, 'reg_source', l[24])               # 10 chars
        set_item(self, 'filler', l[25])                   # 20 chars
        set_item(self, 'affiliation', l[26])              # 3 chars 
        set_item(self, 'town', l[27])                     # 3 chars
        set_item(self, 'ward', l[28])                     # 3 chars
        set_item(self, 'dist', l[29])                     # 3 chars
        set_item(self, 'congress_dist', l[30])            # 3 chars
        set_item(self, 'senatorial_dist', l[31])          # 3 chars
        set_item(self, 'assembly_dist', l[32])            # 3 chars
        set_item(self, 'school_dist', l[33])              # 3 chars
        set_item(self, 'county_dist', l[34])              # 3 chars
        set_item(self, 'village_dist', l[35])             # 3 chars
        set_item(self, 'fire_dist', l[36])                # 3 chars
        set_item(self, 'lib_dist', l[37])                 # 3 chars
        set_item(self, 'voter_status', l[38])             # A|I|P
        set_item(self, 'reason', l[39])                   # \w{10}
        set_item(self, 'absentee', l[40])                 # Y|N

        mailing={}
        set_item(mailing, 'address', l[41:45])            # 4 x 40
        set_item(mailing, 'city',l[45])                   # 25
        set_item(mailing, 'state', l[46])                 # 2
        set_item(mailing, 'zip', l[47])                   # \d{5}
        set_item(mailing, 'zip_plus', l[48])              # \d{4}
        if mailing != {}:
            set_item(self, 'mailing', mailing)

        absentee={}
        set_item(absentee, 'election code', l[49]),
        set_item(absentee, 'code', l[50])                   # 4
        set_item(absentee, 'application received date', l[51]) # YYYYMMDD
        absentee_add ={}
        set_item(absentee_add, 'add', l[52:56])              # 4 x 40 chars
        set_item(absentee_add, 'city',l[56])                 # 25 chars
        set_item(absentee_add, 'state',l[57])                # 2 chars
        set_item(absentee_add, 'zip', l[58])                 # 5 chars
        set_item(absentee_add, 'zip_plus',l[59])             # 4 chars
        if absentee_add !={}:
            set_item(absentee, 'add', absentee_add)
        set_YYYYMMDD(absentee, 'ballot issued date',      l[60])       
        set_YYYYMMDD(absentee, 'ballot received date',    l[61])     
        set_YYYYMMDD(absentee, 'ballot re-issued date',   l[62])    
        set_YYYYMMDD(absentee, 'ballot re-received date', l[63])  
        set_YYYYMMDD(absentee, 'expiration_date', l[64])          
        set_item(absentee, 'eligible', l[65])                 # 'Y'/'N'
        set_item(absentee, 'ineligible_reason', l[66])        # 40 chars
        if absentee != {}:
            set_item(self, 'absentee', absentee)

        set_history_codes(self, 'history_codes', l[-2])      # should be 12 x 4-char codes
        # vj: hack for now, to work around bugs in rows
        
    def get_name(self):
        res = self.name['last_name'] + "," + self.name['first_name']
        if self.name['middle_name'] != '':
            res = res + ' ' + self.name['middle_name']
        if self.name['suffix'] != '':
            res = res + ' ' + self.name['suffix']
        return res

    def __repr__(self):
        return "<Voter {}>".format(self.get_name())
    def __str__(self):
        return "<Voter {}>".format(self.get_name())
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
