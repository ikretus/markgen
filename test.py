#!/usr/bin/env python
import re
import sys
from markgen import markgen

########################################################################

if __name__ == '__main__':

    if len(sys.argv) == 1:
        sys.stderr.write('USAGE: %s  [N=100]\n' % sys.argv[0])
        sys.stderr.write('Waiting for data from stdin...\n')
        nwords = 100
    else:
        try:
            nwords = int(sys.argv[1])
            if nwords < 1: nwords = 100
        except ValueError:
            nwords = 100

    o = markgen()
    o.load()
    if o.status != 'ok':
        sys.stderr.write('Cannot load pickled markgen object!\n')
        sys.exit(1)

    text = sys.stdin.read()
    text = re.findall(r'\w+', text.decode('utf8').lower(), re.UNICODE)

    if len(text) < o.order:
        sys.stderr.write('Please input more than %d words!\n' % o.order)
        sys.exit(1)

    print ' '.join( o.genfrom(text, nwords) )

########################################################################
