#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from .models import BatchScan, Piece, Bid, BidderId, Person, Bidder
import datetime
import re
from django.db.models.query import transaction
from django.core.exceptions import ValidationError


location_scan_re = re.compile(r'[PL](\w\d+)$')
piece_scan_re = re.compile(r'A(\d+)P(\d+)$')
end_location_scan_re = re.compile(r'[PL]END$')

bidder_scan_re = re.compile(r'B(\d+)$')
price_scan_re = re.compile(r'(\d+)$')
normal_sale_scan_re = re.compile(r'NS$')
buy_now_scan_re = re.compile(r'NBN$')
no_bids_scan_re = re.compile(r'NB$')
auction_sale_scan_re = re.compile(r'NAS$')
auction_complete_scan_re = re.compile(r'NAC$')
not_for_sale_scan_re = re.compile(r'NFS$')

person_scan_re = re.compile(r'P(\d+)$')

comments_re = re.compile(r'\s+#.*')


class StateL:
    start = 1
    read_location = 2
    error_skipping = 99


def add_error(errors, lines, lineno, message):
    if lineno is not None:
        errors.append("line %d: %s" % (lineno+1, message))
        if len(lines) < lineno+1:
            lines.append("")
        lines[lineno] += " # " + message
    else:
        errors.append(message)


@transaction.atomic
def process_locations(data):
    errors = []
    state = StateL.start
    current_location = None
    lines = data.splitlines()
    for lineno, l in enumerate(lines):
        l = l.strip()
        l = comments_re.sub('', l)
        lines[lineno] = l
        if l == "":
            continue
        mo = location_scan_re.match(l)
        if mo:
            if state not in [StateL.start, StateL.error_skipping]:
                add_error(errors, lines, lineno, "previous block incomplete")
            current_location = mo.group(1)
            state = StateL.read_location
        if not mo:
            if state == StateL.error_skipping:
                continue
            mo = piece_scan_re.match(l)
            if mo:
                if state == StateL.read_location:
                    try:
                        piece = Piece.objects.get(artist=int(mo.group(1)), pieceid=int(mo.group(2)))
                    except Piece.DoesNotExist:
                        add_error(errors, lines, lineno, "piece does not exist")
                        state = State.error_skipping
                        continue
                    piece.location = current_location
                    if piece.status in [Piece.StatusNotInShow, Piece.StatusNotInShowLocked]:
                        piece.status = Piece.StatusInShow
                    piece.save()
                else:
                    add_error(errors, lines, lineno, "piece not found immediately after location")
        if not mo:
            mo = end_location_scan_re.match(l)
            if mo:
                if state == StateL.read_location:
                    state = StateL.start
                else:
                    add_error(errors, lines, lineno, "location block ended without being begun")
        if not mo:
            add_error(errors, lines, lineno, "unknown code")
            state = StateL.error_skipping
    if state != StateL.start:
        add_error(errors, lines, None, "last block missing END")

    data = "\n".join(lines)
    return data, errors


class State:
    start = 1
    read_piece = 2
    read_bidder = 3
    read_price = 4
    error_skipping = 99


@transaction.atomic
def process_bids(data, final_scan=False):
    errors = []
    state = State.start
    current_piece = None
    current_bidder = None
    current_price = None
    lines = data.splitlines()
    for lineno, l in enumerate(lines):
        l = l.strip()
        if l == "":
            continue
        mo = piece_scan_re.match(l)
        if mo:
            if state not in [State.start, State.error_skipping]:
                add_error(errors, lines, lineno, "previous block incomplete")
            try:
                current_piece = Piece.objects.get(artist=int(mo.group(1)), pieceid=int(mo.group(2)))
            except Piece.DoesNotExist:
                add_error(errors, lines, lineno, "piece does not exist")
                state = State.error_skipping
            else:
                state = State.read_piece
        if not mo:
            if state == State.error_skipping:
                continue
            mo = bidder_scan_re.match(l)
            if mo:
                if state == State.read_piece:
                    try:
                        current_bidder = BidderId.objects.get(id=mo.group(1)).bidder
                    except BidderId.DoesNotExist:
                        add_error(errors, lines, lineno, "bidder does not exist")
                        state = State.error_skipping
                    else:
                        state = State.read_bidder
                else:
                    add_error(errors, lines, lineno, "found bidder scan not immediately after piece")
                    state = State.error_skipping
        if not mo:
            mo = price_scan_re.match(l)
            if mo:
                if state == State.read_bidder:
                    current_price = int(mo.group(1))
                    state = State.read_price
                else:
                    add_error(errors, lines, lineno, "found price not immediately after bidder")
                    state = State.error_skipping
        if not mo:
            mo = normal_sale_scan_re.match(l)
            if mo:
                if state == State.start:
                    # Skipping extraneous Normal Sale, a common scanning error
                    pass
                elif state == State.read_price:
                    bid = Bid(bidder=current_bidder, amount=current_price, piece=current_piece)
                    try:
                        bid.validate()
                    except ValidationError, x:
                        add_error(errors, lines, lineno, "invalid bid")
                        continue
                    bid.save()
                    if final_scan:
                        current_piece.bidsheet_scanned = True
                        current_piece.status = Piece.StatusWon
                    current_piece.save()
                    state = State.start
                else:
                    add_error(errors, lines, lineno, "normal sale scan found not immediately after price")
                    state = State.error_skipping
        if not mo:
            mo = buy_now_scan_re.match(l)
            if mo:
                if state == State.read_price:
                    bid = Bid(bidder=current_bidder, amount=current_price, piece=current_piece, buy_now_bid=True)
                    try:
                        bid.validate()
                    except ValidationError, x:
                        add_error(errors, lines, lineno, "invalid bid")
                        state = State.error_skipping
                        continue
                    bid.save()
                    if final_scan:
                        current_piece.bidsheet_scanned = True
                        current_piece.status = Piece.StatusWon
                    current_piece.save()
                    state = State.start
                else:
                    add_error(errors, lines, lineno, "buy now scan found not immediately after price")
                    state = State.error_skipping
        if not mo:
            mo = auction_sale_scan_re.match(l)
            if mo:
                if state == State.read_price:
                    bid = Bid(bidder=current_bidder, amount=current_price, piece=current_piece)
                    try:
                        bid.validate()
                    except ValidationError, x:
                        add_error(errors, lines, lineno, "invalid bid")
                        state = State.error_skipping
                        continue
                    bid.save()
                    if final_scan:
                        current_piece.bidsheet_scanned = True
                    current_piece.voice_auction = True
                    current_piece.save()
                    state = State.start
                    pass
                else:
                    add_error(errors, lines, lineno, "auction sale scan found not immediately after price")
                    state = State.error_skipping
        if not mo:
            mo = auction_complete_scan_re.match(l)
            if mo:
                if state == State.read_price:
                    bid = Bid(bidder=current_bidder, amount=current_price, piece=current_piece)
                    try:
                        bid.validate()
                    except ValidationError, x:
                        add_error(errors, lines, lineno, "invalid bid")
                        state = State.error_skipping
                        continue
                    bid.save()
                    if final_scan:
                        current_piece.bidsheet_scanned = True
                        current_piece.status = Piece.StatusWon
                    current_piece.voice_auction = True
                    current_piece.save()
                    state = State.start
                    pass
                else:
                    add_error(errors, lines, lineno, "auction sale scan found not immediately after price")
                    state = State.error_skipping
        if not mo:
            mo = not_for_sale_scan_re.match(l)
            if mo:
                if state == State.read_piece:
                    if not current_piece.not_for_sale:
                        add_error(errors, lines, lineno, "Not for sale found on non NFS piece")
                        state = State.error_skipping
                        continue
                    if final_scan:
                        current_piece.bidsheet_scanned = True
                    current_piece.save()
                    state = State.start
                    pass
                else:
                    add_error(errors, lines, lineno, "not for sale scan found not immediately after piece")
                    state = State.error_skipping
        if not mo:
            mo = no_bids_scan_re.match(l)
            if mo:
                if state == State.read_piece:
                    num_bids = current_piece.bid_set.count()
                    if num_bids > 0:
                        add_error(errors, lines, lineno, "No Bid found for pieces with bids")
                        state = State.error_skipping
                        continue
                    if final_scan:
                        current_piece.bidsheet_scanned = True
                    current_piece.save()
                    state = State.start
                else:
                    add_error(errors, lines, lineno, "no bids scan found not immediately after piece")
                    state = State.error_skipping

        if not mo:
            add_error(errors, lines, lineno, "unknown line")
            state = State.error_skipping
    if state != StateL.start:
        add_error(errors, lines, None, "block incomplete")

    data = "\n".join(lines)
    return data, errors



class StateCB:
    start = 1
    read_person = 2

@transaction.atomic
def process_create_bidderids(data):
    errors = []
    state = StateCB.start
    current_person = None
    lines = data.splitlines()
    for lineno, l in enumerate(lines):
        l = l.strip()
        if l == "":
            continue

        mo = person_scan_re.match(l)
        if mo:
            if state != StateCB.start:
                add_error(errors, lines, lineno, "was expecting bidder ID")
                continue
            try:
                person = Person.objects.get(id=int(mo.group(1)))
            except Person.DoesNotExist:
                add_error(errors, lines, lineno, "person not found")
                continue
            current_person = person
            state = StateCB.read_person
            continue

        mo = bidder_scan_re.match(l)
        if mo:
            if state != StateCB.read_person:
                add_error(errors, lines, lineno, "unexpected bidder id")
                continue
            bidderid_str = mo.group(1)
            try:
                BidderId.objects.get(id=bidderid_str)
                add_error(errors, lines, lineno, "bidder id already exists")
                continue
            except BidderId.DoesNotExist:
                pass
            bidder, created = Bidder.objects.get_or_create(person=current_person)
            bidderid = BidderId(id=bidderid_str, bidder=bidder)
            bidderid.save()
            state = StateCB.start
            continue

    if state != StateL.start:
        add_error(errors, lines, None, "block incomplete")

    data = "\n".join(lines)
    return data, errors


def process_batchscan(id):
    batchscan = BatchScan.objects.get(id=id)
    if not batchscan.original_data:
        batchscan.original_data = batchscan.data
        batchscan.save()
    now = datetime.datetime.now()
    if batchscan.processed:
        log_str = "%s\nAlready Processed" % now
        batchscan.processing_log = log_str
        batchscan.save()
    elif batchscan.batchtype not in [1, 2, 3, 4]:
        log_str = "%s\nUnknown batchtype" % now
        batchscan.processing_log = log_str
        batchscan.save()
    else:
        if batchscan.batchtype == 1:
            newdata, errors = process_locations(batchscan.data)
        elif batchscan.batchtype in [2, 3]:
            newdata, errors = process_bids(batchscan.data, final_scan=(batchscan.batchtype == 3))
        elif batchscan.batchtype == 4:
            newdata, errors = process_create_bidderids(batchscan.data)
        else:
            newdata = None
            errors = ["Unknown batch type: %d" % batchscan.batchtype]
        if newdata:
            batchscan.data = newdata
        if errors:
            log_str = "\n".join(["Batch Processing error at " + str(now)] + errors)
            batchscan.processing_log = log_str
        else:
            log_str = "%s\nProcessing Complete" % now
            batchscan.processing_log = log_str
            batchscan.processed = True
        batchscan.save()
