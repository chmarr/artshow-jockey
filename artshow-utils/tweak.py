#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Piece
import sys

pid = int(sys.argv[1])
piece = Piece.objects.get(id=pid)

if piece.status == 1 and piece.voice_auction:
	print "setting"
	piece.status = 2
	piece.save ()
else:
	print "not setting"
	print "status = ", piece.status
	print "voice_auction = ", piece.voice_auction






