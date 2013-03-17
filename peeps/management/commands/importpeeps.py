from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
from peeps.models import Person
import sqlite3
import csv
import re


class UnicodeCsvReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next() 
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num


class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)


def map_reset ( self, option, opt_str, value, parser ):
    parser.values.map = []

    
class Command ( BaseCommand ):

    args = 'infile'
    help = "Monitor connected scanner"
    
    default_map = [
        "firstname=name",
        "rl_first=name",
        "lastname=name",
        "surname=name",
        "rl_last=name",
        "name=name",
        "address=address1",
        "address1=address1",
        "address 1 line 1=address1",
        "address2=address2",
        "address 1 line 2=address2",
        "city=city",
        "address 1 city=city",
        "town=city",
        "county=state",
        "state=state",
        "address 1 state=state",
        "province=state",
        "country=country",
        "address 1 country=country",
        "zip=postcode",
        "zipcode=postcode",
        "postcode=postcode",
        "address 1 zip=postcode",
        "phone=phone",
        "cell=phone",
        "phone1=phone",
        "ph 1=phone",
        "cell1=phone",
        "email=email",
        "email1=email",
        "regid=reg_id",
        "reg_id=reg_id",
        "id=reg_id",
        "uid=reg_id",
        "fc2013_reg_num=reg_id",
        "con_id=reg_id",
        "comment=comment",
        ]
    
    targets = ( "name", "address1", "address2", "city", "state", "country", "postcode", "phone", "email", "reg_id", "comment" )
        
    map_re = re.compile ( "(?P<source>[\w ]+)=(?P<target>\w+)$" )
        
    option_list = BaseCommand.option_list + (
        make_option ( "--map", type="string", action="append", default=default_map, help="add a new map. sourcename=targetname." ),
        make_option ( "--map-reset", action="callback", callback=map_reset, help="clear the map" ),
        make_option ( "--comment", type="string", default="", help="add this comment" ),
        make_option ( "-n", "--dry-run", action="store_true", default=False, help="show results, Don't update DB" ),
        make_option ( "-o", "--results", type="string", default=None, help="write results to file" ),
        make_option ( "-i", "--input", type="string", default=None, help="read previous results to assist in decisions from file" ),
        make_option ( "--dialect", type="string", default="excel", help="csv dialect [%default]" ),
        make_option ( "--encoding", type="string", default="utf-8", help="encoding [%default]" ),
        )
    
    def handle ( self, *args, **options ):
    
        mapping = self.convert_mapping ( options['map'] )
        db = self.read_reg_csv ( args[0], mapping, options['dialect'], options['encoding'] )
        
        if options['results']:
            results = open( options['results'], "w" )
        else:
            results = None
        
        self.merge_peeps ( db, dry_run=options['dry_run'], results=results, comment=options['comment'] )
        
    def print_person ( self, person ):
        print "Person ID:%s  Name:%s  RegID:%s  Comment:%s" % ( person.id, person.name, person.reg_id, person.comment )
        print "Address:%s  Address2:%s  City:%s  State:%s  Country:%s  Postcode:%s" % ( person.address1, person.address2, person.city, person.state, person.country, person.postcode )
        print "Phone:%s  Email:%s" % ( person.phone, person.email )
        print
        
    def print_person_summary ( self, person ):
        print "Person ID:%s  Name:%s  RegID:%s  Comment:%s" % ( person.id, person.name, person.reg_id, person.comment )
        
    def row_into_person ( self, result ):
        p = Person ( name=result[0], address1=result[1], address2=result[2], city=result[3], state=result[4], country=result[5],
                            postcode=result[6], phone=result[7], email=result[8], reg_id=result[9], comment=result[10] )
        return p
        
        
    def merge_peeps ( self, db, dry_run=False, results=None, comment=None ):
    
        print
    
        for person in Person.objects.all ():
        
            if person.reg_id == "":
                print "Missing Reg ID for:"
                self.print_person_summary ( person )
                csv_person = None
            else:
                results = db.execute ( "select * from person where reg_id=?", ( person.reg_id, ) )
                result = results.fetchone()
                if result:
                    csv_person = self.row_into_person ( result )
                else:
                    print "Reg ID not found for:"
                    self.print_person_summary ( person )
                    csv_person = None
                    
            if csv_person is None:
                results = db.execute ( "select * from person where name like ?", ( person.name[:4]+"%", ) )
                results=results.fetchall()
                results = [ self.row_into_person(row) for row in results ]
                print "Database search:", len(results), "possibilities found"
                for index, found_person in enumerate(results):
                    print "Option", index+1, ":"
                    self.print_person ( found_person )
                response = raw_input ( "Option (or 0 for none): ")
                while True:
                    try:
                        index = int(response)
                        if index == 0: break
                        csv_person = results[index-1]
                    except ValueError, IndexError:
                        print "Invalid Option"
                    else:
                        break
                print
            
            if csv_person is not None:
                person.reg_id = csv_person.reg_id
                if person.name != csv_person.name:
                    print "CSV Entry found, but names mismatch"
                    self.print_person_summary ( person )
                    while True:
                        print "Database:", person.name, " CSV:", csv_person.name
                        print "  1) Keep Database Name:", person.name
                        print "  2) Use CSV Name:", csv_person.name
                        print "  3) Enter Anew"
                        response = raw_input ( "Option: " )
                        if response == "1":
                            break
                        elif response == "2":
                            person.name = csv_person.name
                            break
                        elif response == "3":
                            new_name = raw_input ( "Enter Name: " )
                            if new_name:
                                person.name = new_name
                            break
                        else:
                            print "Invalid Option"
                    print
                if not ( person.address1 or person.address2 or person.city or person.state or person.country or person.postcode ):
                    person.address1 = csv_person.address1
                    person.address2 = csv_person.address2
                    person.city = csv_person.city
                    person.state = csv_person.state
                    person.country = csv_person.country
                    person.postcode = csv_person.postcode
                if not person.phone:
                    person.phone = csv_person.phone
                if not person.email:
                    person.email = csv_person.email
                person.save ()
            

        
    def convert_mapping ( self, map ):
        mapping = []
        for s in map:
            mo = self.map_re.match ( s )
            if not mo:
                raise ValueError ( "mapping %s is not in expected form" % s )
            source = mo.group('source').lower()
            target = mo.group('target').lower()
            if target not in self.targets:
                raise ValueError ( "target %s is not valid" % target )
            mapping.append ( ( source, target ) )
        return mapping
        
    def read_reg_csv ( self, filename, mapping, dialect, encoding ):

        infile = open(filename)
        csvfile = UnicodeDictReader ( infile, dialect=dialect, encoding=encoding )
        fieldnames = csvfile.fieldnames
        fieldnames = [ x.lower() for x in fieldnames ]
        csvfile.fieldnames = fieldnames
        
        db = sqlite3.connect ( ":memory:" )
        db.execute ( "create table person ( name text, address1 text, address2 text, city text, state text, country text, postcode text, phone text, email text, reg_id text primary key, comment text )" )
        db.execute ( "create index table_name_idx on person ( name )")
        db.execute ( "create index table_email_idx on person ( email )")
        
        for row in csvfile:
            values = dict ( ( ( t, "" ) for t in self.targets ) )
            for source, target in mapping:
                value = row.get(source,'')
                value = value.strip()
                if value:
                    if values[target]:
                        values[target] += " " + value
                    else:
                        values[target] = value
            values['reg_id'] = values['reg_id'].replace ( ' ', '-' )
            db.execute ( "insert into person values ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )", tuple ( values[t] for t in self.targets ) )
            
        return db
