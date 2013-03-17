#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

import optparse
import sys

default_factors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class CheckDigitError(ValueError):
    pass


def make_check(s, check10="X", factors=default_factors):
    tally = 0
    for i in range(len(s)):
        tally += int(s[-1 - i]) * factors[(1 + i) % len(factors)]
    check = (-tally) % 11
    if check == 10:
        return check10
    else:
        return str(check)


def check(s, check10="X", start=0, end=None, factors=default_factors):
    s2 = s[start:end]
    tally = 0
    for i in range(len(s2)):
        c = s2[-1 - i]
        c = (c == check10) and 10 or int(c)
        tally += c * factors[i % len(factors)]
    if tally % 11 != 0:
        raise CheckDigitError("check digit failed for " + s)


def make_codes(num, first=0, count=1, min_digits=3, check10=False, factors=default_factors):
    i = 0
    bare_code = first
    while i < num:
        bare_code_str = "%0*d" % (min_digits, bare_code)
        bare_code += 1
        check = make_check(bare_code_str, factors=factors)
        if check == "X":
            if not check10:
                continue
            check = check10
        for c in range(count):
            yield bare_code_str + check
        i += 1


def _get_options():
    # noinspection PyUnusedLocal
    def factors_callback(option, opt, value, parser):
        try:
            factors = value.split(",")
            factors = [int(x) for x in factors]
            parser.values.factors = factors
        except ValueError, x:
            raise optparse.OptionValueError(str(x))

    parser = optparse.OptionParser()
    parser.add_option("-c", "--count", type="int", default=1)
    parser.add_option("--min_digits", type="int", default=3)
    parser.add_option("--check10", type="str", default="")
    parser.add_option("--prefix", type="str", default="")
    parser.add_option("--suffix", type="str", default="")
    parser.add_option("--factors", type="str", action="callback", callback=factors_callback, default=default_factors)
    parser.add_option("--check", action="store_true", default=False)
    opts, args = parser.parse_args()

    if opts.check:
        opts.sample = args[0]
    else:
        opts.num = int(args[0])
        try:
            opts.first = int(args[1])
        except IndexError:
            opts.first = 0

    return opts


def _main():
    opts = _get_options()
    if opts.check:
        try:
            check(opts.sample, check10=opts.check10, start=len(opts.prefix), end=len(opts.suffix) or None,
                  factors=opts.factors)
        except ValueError, x:
            print >> sys.stderr, x
            raise SystemExit(1)
    else:
        for c in make_codes(opts.num, opts.first, opts.count, min_digits=opts.min_digits, check10=opts.check10,
                            factors=opts.factors):
            print opts.prefix + c + opts.suffix


if __name__ == "__main__":
    _main()

