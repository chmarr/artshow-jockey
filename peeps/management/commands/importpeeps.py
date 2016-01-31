from optparse import make_option
import sqlite3
import csv
import re

from django.core.management.base import BaseCommand

from ...models import Person


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


# noinspection PyUnusedLocal
def map_reset(self, option, opt_str, value, parser):
    parser.values.map = []


class Command(BaseCommand):
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

    targets = ("name", "address1", "address2", "city", "state", "country",
               "postcode", "phone", "email", "reg_id", "comment")

    map_re = re.compile("(?P<source>[^=]+)=(?P<target>\w+)$")

    option_list = BaseCommand.option_list + (
        make_option("--map", type="string", action="append", default=default_map,
                    help="add a new map. sourcename=targetname."),
        make_option("--map-reset", action="callback", callback=map_reset, help="clear the map"),
        make_option("-n", "--dry-run", action="store_true", default=False, help="show results, Don't update DB"),
        make_option("--skip-missing-reg-id", action="store_true", default=False,
                    help="Skip persons with a missing Reg ID"),
        make_option("--dialect", type="string", default="excel", help="csv dialect [%default]"),
        make_option("--encoding", type="string", default="utf-8", help="encoding [%default]"),
    )

    def handle(self, *args, **options):

        mapping = self.convert_mapping(options['map'])
        db = self.read_reg_csv(args[0], mapping, options['dialect'], options['encoding'])

        self.merge_peeps(db, dry_run=options['dry_run'], skip_no_regid=options['skip_missing_reg_id'])

    def print_person(self, person):
        print "Person ID:%s  Name:%s  RegID:%s  Comment:%s" % (person.id, person.name, person.reg_id, person.comment)
        print "Address:%s  Address2:%s  City:%s  State:%s  Country:%s  Postcode:%s" % (
            person.address1, person.address2, person.city, person.state, person.country, person.postcode)
        print "Phone:%s  Email:%s" % (person.phone, person.email)
        print

    def print_person_summary(self, person):
        print "Person ID:%s  Name:%s  RegID:%s  Comment:%s" % (person.id, person.name, person.reg_id, person.comment)

    def row_into_person(self, result):
        p = Person(name=result[0], address1=result[1], address2=result[2], city=result[3], state=result[4],
                   country=result[5],
                   postcode=result[6], phone=result[7], email=result[8], reg_id=result[9], comment=result[10])
        return p

    def merge_peeps(self, db, dry_run=False, skip_no_regid=False):

        print

        for person in Person.objects.all():

            if person.reg_id == "":
                if skip_no_regid:
                    continue
                print "Missing Reg ID for:"
                self.print_person_summary(person)
                csv_person = None
            else:
                results = db.execute("select * from person where reg_id=?", (person.reg_id,))
                result = results.fetchone()
                if result:
                    csv_person = self.row_into_person(result)
                else:
                    print "Reg ID not found for:"
                    self.print_person_summary(person)
                    csv_person = None

            if csv_person is None:
                results = db.execute("select * from person where name like ?", (person.name[:4] + "%",))
                results = results.fetchall()
                results = [self.row_into_person(row) for row in results]
                print "Database search:", len(results), "possibilities found"
                for index, found_person in enumerate(results):
                    print "Option", index + 1, ":"
                    self.print_person(found_person)
                response = raw_input("Option (or 0 for none): ")
                while True:
                    try:
                        index = int(response)
                        if index == 0:
                            break
                        csv_person = results[index - 1]
                    except (ValueError, IndexError):
                        print "Invalid Option"
                    else:
                        break
                print

            if csv_person is not None:
                skip_person = False
                person.reg_id = csv_person.reg_id
                if person.name != csv_person.name:
                    print "CSV Entry found, but names mismatch"
                    self.print_person_summary(person)
                    while True:
                        print "Database:", person.name, " CSV:", csv_person.name
                        print "  0) Skip"
                        print "  1) Keep Database Name:", person.name
                        print "  2) Use CSV Name:", csv_person.name
                        print "  3) Enter Anew"
                        response = raw_input("Option: ")
                        if response == "0":
                            skip_person = True
                            break
                        elif response == "1":
                            break
                        elif response == "2":
                            person.name = csv_person.name
                            break
                        elif response == "3":
                            new_name = raw_input("Enter Name: ")
                            if new_name:
                                person.name = new_name
                            break
                        else:
                            print "Invalid Option"
                    print
                if skip_person:
                    continue
                if not (person.address1 or person.address2 or person.city or
                            person.state or person.country or person.postcode):
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
                if not dry_run:
                    person.save()

    def convert_mapping(self, map):
        mapping = []
        for s in map:
            mo = self.map_re.match(s)
            if not mo:
                raise ValueError("mapping %s is not in expected form" % s)
            source = mo.group('source').lower()
            target = mo.group('target').lower()
            if target not in self.targets:
                raise ValueError("target %s is not valid" % target)
            mapping.append((source, target))
        return mapping

    def read_reg_csv(self, filename, mapping, dialect, encoding):

        infile = open(filename)
        csvfile = UnicodeDictReader(infile, dialect=dialect, encoding=encoding)
        fieldnames = csvfile.fieldnames
        fieldnames = [x.lower() for x in fieldnames]
        csvfile.fieldnames = fieldnames

        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE person ( name TEXT, address1 TEXT, address2 TEXT, city TEXT, state TEXT, country TEXT, postcode TEXT, phone TEXT, email TEXT, reg_id TEXT PRIMARY KEY, comment TEXT )")
        db.execute("CREATE INDEX table_name_idx ON person ( name )")
        db.execute("CREATE INDEX table_email_idx ON person ( email )")

        for row in csvfile:
            try:
                values = dict(((t, "") for t in self.targets))
                for source, target in mapping:
                    value = row.get(source, '')
                    value = value.strip()
                    if value:
                        if values[target]:
                            values[target] += " " + value
                        else:
                            values[target] = value
                values['reg_id'] = values['reg_id'].replace(' ', '-')
            except Exception as exc:
                print "Problem reading input record. Error: %s Row: %r" % (exc, row)
                raise
            try:
                db.execute("INSERT INTO person VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )",
                           tuple(values[t] for t in self.targets))
            except Exception as exc:
                print "Problem storing data in temporary database. Error: %s Data: %r" % (exc, values)
                raise

        return db
