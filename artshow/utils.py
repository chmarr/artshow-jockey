import re
import csv
import codecs
import cStringIO
from django.contrib.auth import get_user_model

from .conf import settings
from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail

User = get_user_model()


class AttributeFilter(object):
    """This creates a proxy object that will only allow
    access to the proxy if the attribute matches the
    regular expression. Otherwise,
    an AttributeError is returned."""

    def __init__(self, target, expression):
        """'target' is the object to be proxied. 'expression' is a regular expression
        (compiled or not) that will be used as the filter."""
        self.__target = target
        self.__expression = expression
        if not hasattr(self.__expression, 'match'):
            self.__expression = re.compile(self.__expression)

    def __getattr__(self, name):
        if self.__expression.match(name):
            return self.__target.__getattr__(name)
        else:
            raise AttributeError("AttributeFilter blocked access to '%s' on object '%s'" % ( name, self.__target ))


artshow_settings = AttributeFilter(settings, r"ARTSHOW_|SITE_NAME$|SITE_ROOT_URL$")


class UnicodeCSVWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def create_user_from_email(email):
    max_username_length = User._meta.get_field('username').max_length
    if len(email) > max_username_length:
        username = email.split("@")[0]
        if User.objects.filter(username=username).exists():
            for i in range(1, 1000):
                test_username = username + str(i)
                if len(test_username) > 30:
                    return ValueError("Could not create user. Pre-@ part is too long to add a unique number.")
                if not User.objects.filter(username=test_username).exists():
                    username = test_username
                    break
            else:
                return ValueError("Could not create user. Ran out of numbers to add.")
    else:
        username = email
    user = User(username=username, email=email)
    user.set_unusable_password()
    user.save()
    return user


def send_password_reset_email(artist, user, subject=None, template=None):
    from django.utils.http import int_to_base36
    from django.contrib.auth.tokens import default_token_generator
    from artshow.email1 import wrap, default_wrap_cols


    if template is None:
        template = artshow_settings.ARTSHOW_PASSWORD_RESET_TEMPLATE
    if not hasattr(template, 'render'):
        template = get_template(template)

    if subject is None:
        subject = artshow_settings.ARTSHOW_PASSWORD_RESET_SUBJECT

    c = {
        'artist': artist,
        'user': user,
        'uid': int_to_base36(user.id),
        'token': default_token_generator.make_token(user),
        'artshow_settings': artshow_settings
    }

    body = template.render(Context(c))
    body = wrap(body, default_wrap_cols)
    send_mail(subject, body, settings.ARTSHOW_EMAIL_SENDER, [user.email], fail_silently=False)
