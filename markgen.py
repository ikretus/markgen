import cPickle
import re
import time
from collections import defaultdict
from random import randint, shuffle
from subprocess import Popen, PIPE

########################################################################

class markgen:
    """
    Provides general implementation of the markov text generator.
    Encapsulates all related parameters:
      args       : path/to/curl with corresponding options
      chain      : dictionary representation of the markov chain
      order      : the order of the markov chain
      status     : current status of markgen object
      uniqs      : set of unique tokens extracted from (text) data
      url        : the url of the (text) data
    and methods:
      add(o)     : adds an(o)ther markgen object's chain
      gen(n)     : generates an example text of (n)-words
      genfrom(t) : 
      load()     : loads markgen object from pickled file
      save()     : saves markgen object into pickled file
      train()    : builds the chain
    Note that user can manually change the curl options (self.args).
    """
    #
    def __init__(self, order=3, url=''):
        self.args = ['curl','--buffer','--connect-timeout','1','--location',\
                     '--max-time','37','--silent','--show-error']
        self.chain = defaultdict(set)
        self.order = order if order > 0 else 3
        self.status = 'empty'
        self.uniqs = set()
        self.url = str(url)
    #
    #
    def add(self, other):
        if self.order != other.order:
            return
        self.status = 'ok'
        self.url = '#merged'
        # update the set of unique words:
        self.uniqs.update(other.uniqs)
        # update each set of 'future states' of the chain:
        for key in other.chain.keys():
            self.chain[key].update( other.chain[key] )
    #
    #
    def gen(self, nw):
        if self.status != 'ok':
            return ''
        # choose a start/seed key:
        key = self.chain.keys()[ randint(0, len(self.chain) - 1) ]
        #
        text = list(key)
        for i in xrange(nw):
            try:
                vals = list(self.chain[key])
            except KeyError:
                break
            val = vals[ randint(0, len(vals) - 1) ]
            key = tuple(list(key[1:]) + [val])
            text.append(val)
        return text
    #
    #
    def genfrom(self, text, nw):
        n_keys = len(text) - self.order + 1
        if (self.status != 'ok') or (n_keys <= 0):
            return ''
        if nw <= self.order:
            return text[:nw]
        # split the input text into key-tuples:
        text_keys = list()
        for i in xrange(n_keys):
            text_keys.append( tuple( text[:self.order] ) )
            del text[0]
        # choose only common key-tuples:
        text_keys_set = set(text_keys) & set( self.chain.keys() )
        text_keys = list(text_keys_set)
        shuffle(text_keys)
        #
        text = list()
        #
        for key in text_keys:
            c_text = list(key)
            c_key = key
            for i in xrange(nw - self.order):
                val = list(self.chain[c_key])[0]
                c_text.append(val)
                c_key = tuple(list(c_key[1:]) + [val])
                if c_key not in text_keys_set:
                    break
            if len(c_text) >= nw:
                return c_text
            if len(c_text) > len(text):
                text = c_text
        return text
    #
    #
    def load(self, fn='markgen.pickle'):
        try:
            with open(fn, 'r') as ff:
                (self.args, self.chain, self.order, \
                 self.status, self.uniqs, self.url) = cPickle.load(ff)
        except IOError:
            self.status = 'empty'
    #
    #
    def save(self, fn='markgen.pickle'):
        if self.status != 'empty':
            with open(fn, 'w') as ff:
                cPickle.dump((self.args, self.chain, self.order, \
                              self.status, self.uniqs, self.url), ff)
    #
    #
    def train(self):
        # execute curl and connect to it via pipe:
        try:
            ps = Popen(args=self.args + [self.url], bufsize=-1, \
                       stdout=PIPE, stderr=PIPE, shell=False)
        except OSError:
            self.status = 'curl not found in $PATH'
            return
        # wait (a bit more than specified) for connection to url:
        time.sleep(0.1 + float( self.args[3] ))
        # exit if non-zero error code is returned by curl:
        if ps.poll():
            self.status = ps.stderr.read()
            return
        # process data if poll() returned None or zero:
        else:
            c_words = list()
            for line in ps.stdout:
                words = re.findall(r'\w+', line.decode('utf8').lower(), re.UNICODE)
                self.uniqs.update(words)
                c_words.extend(words)
                n_keys = len(c_words) - self.order
                if n_keys <= 0:
                    continue
                for i in xrange(n_keys):
                    self.chain[ tuple( c_words[:self.order] ) ].add(c_words[self.order])
                    del c_words[0]
            if len(self.chain) != 0:
                self.status = 'ok'
            return

########################################################################
