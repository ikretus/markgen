#!/usr/bin/env python
import sys
from hashlib import md5
from markgen import markgen

########################################################################

if __name__ == '__main__':

    if len(sys.argv) == 1:
        sys.stderr.write('USAGE: %s  [N=3]  URL(s)\n' % sys.argv[0] )
        sys.exit(1)
    try:
        urls = sys.argv[2:]
        order = int(sys.argv[1])
        if order < 1: order = 3
    except ValueError:
        urls = sys.argv[1:]
        order = 3
    # create an empty markgen object:
    target = markgen(order)
    # for each url the separate markgen objects gonna be created, trained
    # and collected together at end 
    # these steps may be easily parallelized, i.e. via python.multiprocessing
    for url in urls:
        o = markgen(order, url)
        o.train()
        sys.stderr.write( 'URL<%s> processed with status: %s\n' % (url, o.status) )
        if o.status == 'ok':
            #o.save('markgen.pickle.'+ md5(o.url).hexdigest())
            target.add(o)
    # saving aggregated instance to default './markgen.pickle' file
    target.save()
    # and generating sample text:
    print ' '.join( target.gen(500) )

########################################################################
