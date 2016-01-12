
"""List of all Artshow Jockey settings. Those that can have reasonable
defaults have their defaults set here. Those that must be overridden
have been set to the _UNCONFIGURED object, which will be checked during
startup of the artshow application. _DISABLED is to leave a non-critical
feature disabled"""

from appconf import AppConf
from django.conf import settings

_UNCONFIGURED = object()
_DISABLED = object()

class ArtshowAppConf(AppConf):
    
    # These are the "PaymentType" IDs used by various procedures
    # These must match the PaymentTypes loaded by the fixtures
    SPACE_FEE_PK = 3
    PAYMENT_SENT_PK = 5
    PAYMENT_RECEIVED_PK = 1
    PAYMENT_PENDING_PK = 9
    COMMISSION_PK = 6
    SALES_PK = 7
    
    # name of the model handling people, in "app.model" format
    PERSON_CLASS = "peeps.Person"
    
    # name of the module used to print forms, in python path format
    PREPRINT_MODULE = "artshow.preprint_dummy"
    
    SHOW_NAME = "Generic Art Show"
    SHOW_YEAR = "1999"
    TAX_RATE = "0.10"  # Used to initialise a Decimal object
    TAX_DESCRIPTION = "Fictitious County 10% Tax"
    EMAIL_SENDER = "Generic Art Show <artshow@example.com>"
    COMMISSION = "0.1" # Used to initialise a Decimal object
    INVOICE_PREFIX = "1999-" # Prefixed on all printed invoices
    EMAIL_FOOTER = """\
    --
    Random J Hacker
    Generic Art Show Lead.
    artshow@example.com - http://www.example.com/artshow
    """
    PASSWORD_RESET_TEMPLATE = "artshow/manage_password_reset.txt"
    PASSWORD_RESET_SUBJECT = "Your Art Show Management Account"
    CHEQUE_THANK_YOU = "Thank you for exhibiting at Generic Art Show"
    BLANK_BID_SHEET = "artshow/files/BidSheet.pdf"
    BLANK_CONTROL_FORM = "artshow/files/ControlForm.pdf"
    
    # The in-build form printing code uses this font to print piece barcodes.
    # Specify as a 2-tuple: ( "font name", "font path" )
    BARCODE_FONT = ('Free3of9', 'artshow/files/free3of9/FREE3OF9.TTF')
    
    # device name of serial-connected scanner reader.
    # eg: "/dev/ttyUSB0"
    SCANNER_DEVICE = _DISABLED
    
    # Set this to "True" to display allocated spaces to logged-in artists
    SHOW_ALLOCATED_SPACES = False
    
    # Set this to "True" to prevent all standard logins from making edits to
    # piece details. Best used when this database is no longer the "master".
    SHUT_USER_EDITS = False
    
    # Command to send a text file to the printer.
    # Eg: "enscript -q -P myprinter -DProcessColorModel:/DeviceGray -B -L 66 -f Courier-Bold10"
    PRINT_COMMAND = _DISABLED
    AUTOPRINT_INVOICE = ["CUSTOMER COPY", "MERCHANT COPY", "PICK LIST"]
    MONEY_PRECISION = 2
    MONEY_CURRENCY = "USD"
    
    # Set this if something has gone wrong, and registration IDs should no longer
    # be checked for uniqueness
    REGID_NONUNIQUE = False
    
    # Disallow piece IDs greater than
    MAX_PIECE_ID = 999
    
    # URL To the paypal standard payments API. Don't put a trailing comma or questionmark.
    PAYPAL_URL = "https://www.paypal.com/cgi-bin/webscr"
    
    PAYPAL_ACCOUNT = _UNCONFIGURED
    
    ARTIST_AGREEMENT_URL = _UNCONFIGURED
    
    # Change this if an offset has been applied to bidder ID MOD11 calculation.
    # Use "None" to disable check completely.
    BIDDERID_MOD11_OFFSET = 0

    # If True, bid sheets will be printed to assist large stack cutting.
    BID_SHEET_PRECOLLATION = False

    # Print Cheques as PDF instead of plain text.
    CHEQUES_AS_PDF = False
