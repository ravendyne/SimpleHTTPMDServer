#!/usr/bin/python

import sys

USER_PASS = ''

for arg in sys.argv:
    print arg
    if ":" in arg:
        USER_PASS = arg

if USER_PASS:
    print 'USER PASS = ' + USER_PASS
else:
    print 'no USER PASS'

