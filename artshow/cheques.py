#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009-2012 Chris Cogdon
# See file COPYING for licence details

from decimal import Decimal

from .conf import settings

from num2words import num2words
from .email1 import wrap


class PRINT_GRID:
    x_size = 87
    y_size = 66

    def __init__(self):
        # noinspection PyUnusedLocal
        self.data = [" " * self.x_size for i in range(self.y_size)]

    def print_at(self, x, y, msg):
        if x + len(msg) - 1 > self.x_size:
            raise Exception("line too long")
        msg_len = len(msg)
        s = self.data[y - 1]
        s = s[:x - 1] + msg + s[x - 1 + msg_len:]
        self.data[y - 1] = s
        self.last_line_printed = y

    def print_on_next_line(self, msg):
        self.print_at(1, self.last_line_printed + 1, msg)

    def save(self, f):
        for line in self.data:
            print >> f, line


def dotpad(s, max_length):
    l = len(s)
    if l >= max_length:
        return s
    s += " " * ((max_length - l) % 4)
    s += "  .." * ((max_length - l) / 4)
    return s


def cheque_to_text(cheque, f):
    date_str = cheque.date.strftime("%d %b %Y").upper()

    cheque_amount = -cheque.amount

    cheque_dollars = int(cheque_amount)
    cheque_cents = int((cheque_amount - cheque_dollars) * 100 + Decimal("0.5"))

    cheque_words = "** " + num2words(cheque_dollars) + " dollars and %d cents" % cheque_cents + " **"
    cheque_words = cheque_words.upper()

    person = cheque.artist.person

    grid = PRINT_GRID()

    grid.print_at(77, 3, date_str)

    grid.print_at(8, 7, cheque.payee.upper())
    grid.print_at(77, 7, "$%-8.2f" % cheque_amount)

    grid.print_at(1, 9, cheque_words)

    mailing_label_lines = [cheque.payee, person.address1]
    if person.address2:
        mailing_label_lines.append(person.address2)
    mailing_label_lines.append("%s %s  %s" % (person.city, person.state, person.postcode))
    if person.country and person.country != "USA":
        mailing_label_lines.append(person.country)
    mailing_label_lines = [x.upper() for x in mailing_label_lines]

    for i in range(len(mailing_label_lines)):
        grid.print_at(9, 14 + i, mailing_label_lines[i])

    print_items(cheque, grid, 23, True)
    print_items(cheque, grid, 46, False)

    grid.save(f)


def print_items(cheque, grid, offset, payee_side):
    date_str = cheque.date.strftime("%d %b %Y").upper()

    s = "(%d) %s" % (cheque.artist.artistid, cheque.artist.person.name)
    if cheque.artist.publicname:
        s += " (%s)" % cheque.artist.publicname

    grid.print_at(1, offset, s)
    grid.print_at(77, offset, date_str)

    grid.last_line_printed = offset + 1

    item_no = 0
    for item in cheque.artist.payment_set.all().order_by('date', 'id'):
        item_no += 1
        if item.id == cheque.id:
            name = dotpad("This cheque", 71)
        else:
            name = dotpad("%s: %s" % (item.payment_type.name, item.description), 71)[:71]
        grid.print_on_next_line(" %2d. %-71s $%8.2f" % (item_no, name, item.amount))

    grid.print_on_next_line("     %71s $%8.2f" % ("Balance:", cheque.artist.balance()))

    if payee_side:
        grid.print_on_next_line("")
        message = wrap(settings.ARTSHOW_CHEQUE_THANK_YOU, cols=78, always_wrap=True)
        message_lines = message.split("\n")
        for l in message_lines:
            grid.print_on_next_line(l)
    else:
        grid.print_on_next_line("")
        grid.print_on_next_line("Signature: _____________________________________________ Date: __________")
        grid.print_on_next_line("I have received this cheque and agree to return any amount paid in error.")
