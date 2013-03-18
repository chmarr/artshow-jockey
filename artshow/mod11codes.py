#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

# The first element must be 1 for check-digit calculation to be correct
default_factors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class CheckDigitError(ValueError):
    pass


def make_check(s, check10="X", factors=default_factors, offset=0):
    tally = -offset
    for i in range(len(s)):
        tally += int(s[-1 - i]) * factors[(1 + i) % len(factors)]
    check = (-tally) % 11
    return str(check) if check != 10 else check10


def check(s, check10="X", factors=default_factors, offset=0):
    tally = -offset
    for i in range(len(s)):
        c = s[-1 - i]
        try:
            c = int(c) if c != check10 else 10
        except ValueError:
            raise CheckDigitError("invalid character: %s" % c)
        tally += c * factors[i % len(factors)]
    if tally % 11 != 0:
        raise CheckDigitError("check digit failed for " + s)
