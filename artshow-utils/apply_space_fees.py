#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Artist, Payment, PaymentType
import datetime

for a in Artist.objects.all():
	payment_type = PaymentType.objects.get(name="Panel Fee")
	total = 0
	for alloc in a.allocation_set.all():
		total += alloc.space.price * alloc.allocated
	if total <= 0:
		print a, total, "not applying fees"
	else:
		print a, total
		allocated_spaces_str = ", ".join ( "%s:%s" % (al.space.shortname,al.allocated) for al in a.allocation_set.all() )
		payment = Payment ( artist=a, amount=-total, payment_type=payment_type, description="Panel Fee (%s)" % allocated_spaces_str, date=datetime.datetime.now() )
		payment.save ()
