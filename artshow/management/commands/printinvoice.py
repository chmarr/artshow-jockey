from optparse import make_option

from django.core.management.base import BaseCommand

from ...invoicegen import print_invoices


class Command(BaseCommand):
    args = 'invoiceid ... '
    help = "Print invoices to console or printer"

    option_list = BaseCommand.option_list + (
        make_option("--copy-name", type="string", action="append", default=[], help="copy name"),
        make_option("--printer", action="store_true", default=False, help="send to configured printer"),
    )

    def handle(self, *args, **options):
        invoice_ids = [int(x) for x in args]
        print_invoices(invoice_ids, copy_names=options['copy_name'], to_printer=options['printer'])
