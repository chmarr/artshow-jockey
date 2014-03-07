#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.template import Template, Context
from .utils import artshow_settings
from .models import Piece

default_wrap_cols = 79


def wrap(text, cols=default_wrap_cols, always_wrap=False):
    old_lines = text.split("\n")
    new_lines = []
    for l in old_lines:
        if always_wrap or l.startswith('.'):
            if not always_wrap:
                l = l[1:]
            while len(l) > cols:
                pos = l.rfind(" ", 0, cols)
                if pos == -1:
                    pos = l.find(" ", cols)
                if pos == -1:
                    break
                new_lines.append(l[:pos].rstrip())
                l = l[pos:].lstrip()
        new_lines.append(l)
    return "\n".join(new_lines)


def make_email(artist_obj, template_str, signature, cols=default_wrap_cols, autoescape=False):
    pieces_in_show = artist_obj.piece_set.exclude(status=Piece.StatusNotInShow)
    payments = artist_obj.payment_set.all().order_by('date')
    c = {
        'artist': artist_obj,
        'pieces_in_show': pieces_in_show,
        'payments': payments,
        'artshow_settings': artshow_settings,
        'signature': signature,
    }
    return make_email2(c, template_str, cols, autoescape)


def make_email2(context, template_str, cols=default_wrap_cols, autoescape=False):
    if not autoescape:
        template_str = "{% autoescape off %}" + template_str + "{% endautoescape %}"
    context = dict(context)
    context.update({'artshow_settings': artshow_settings})
    t = Template(template_str)
    c = Context(context)
    new_str = t.render(c)
    new_str = wrap(new_str, cols)
    return new_str
