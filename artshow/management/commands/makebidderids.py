from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from artshow.mod11codes import make_check
from django.conf import settings




class Command(BaseCommand):
    args = "firstcode numcodes"
    help = "Generate a list of valid BidderID codes"
    option_list = BaseCommand.option_list + (
        make_option("--digits", type="int", default=3, help="pad to this many digits [%default]"),
        make_option("--allow-x", action="store_true", default=False, help="allow X checkdigit"),
        make_option("--prefix", type="str", default="", help="prefix characters [%default]"),
        make_option("--suffix", type="str", default="", help="suffix characters [%default]"),
        make_option("--offset", type="int", default=settings.ARTSHOW_BIDDERID_MOD11_OFFSET or 0,
                    help="offset checkdigit [%default]"),
        make_option("--copies", type="int", default=1, help="copies [%default]"),
        make_option("--header", type="str", default=None, help="add header"),
    )

    def handle(self, *args, **options):
        try:
            first_code, num_codes = args
        except ValueError:
            raise CommandError("incorrect number of parameters")
        try:
            first_code = int(first_code)
        except ValueError:
            raise CommandError("firstcode is not an integer")
        try:
            num_codes = int(num_codes)
        except ValueError:
            raise CommandError("numcodes is not an integer")
        value = first_code
        digits = options['digits']
        allow_x = options['allow_x']
        prefix = options['prefix']
        suffix = options['suffix']
        offset = options['offset']
        copies = options['copies']
        if options['header']:
            print options['header']
        while num_codes > 0:
            code = "%0*d" % (digits, value)
            value += 1
            check = make_check(code,offset=offset)
            if check=="X" and not allow_x:
                continue
            result = prefix + code + check + suffix
            for i in range(copies):
                print result
            num_codes -= 1
