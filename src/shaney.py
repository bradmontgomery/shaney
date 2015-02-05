#!/usr/bin/env python
"""
shaney.py by Greg McFarlane some editing by Joe Strout
search for "Mark V.  Shaney" on the WWW for more info!

"""
from __future__ import print_function

import random
import re
import string
import sys


def read(filename):
    """Reads content from the file, does a little bit of cleanup, and returns
    a list of words.

    """
    content = open(filename, 'r').read()
    # kill the unicode things (e.g. smart quotes)
    content = content.decode('utf8').encode('ascii', 'ignore')
    # condense all whitespace chars into a single space
    content = re.sub('\s+', ' ', content)
    # Remove everything but words, major punctuation, and single quotes
    content = re.sub('[^A-Za-z\.\?\!\' ]+', '', content)
    return string.split(content)


def train(filename):
    """Reads a file, building the data model used to generate text.
    Returns trained data; a dictionary of the form:

        { content: {},
          endings: [] }

    """
    endings = []  # Pairs of words that end a sentence
    data = {}  # Key: Pairs of words, Values: List of words that follow those pairs.

    # and here's a pair of words that we encounter in a text.
    prev1 = ''
    prev2 = ''

    # Load up a dictionary of data from the input files.
    for word in read(filename):
        if prev1 != '' and prev2 != '':
            key = (prev2, prev1)
            if key in data:
                data[key].append(word)
            else:
                data[key] = [word]
                if any([prev1.endswith(punct) for punct in ['.', '?', '!']]):
                    endings.append(key)
        prev2 = prev1
        prev1 = word
    assert endings != [], "Sorry, there are no sentences in the text."
    return {'content': data, 'endings': endings}


def generate(data, count=10):
    """Given the appropriate data library (dict of 'content' and 'endings' keys),
    this will generate text strings.

    Returns a list of `count` strings.

    """
    output = ""
    generated_strings = []
    key = ()

    while True:
        if key in data['content']:
            word = random.choice(data['content'][key])
            output = "{0}{1} ".format(output, word)

            key = (key[1], word)
            if key in data['endings']:
                generated_strings.append(output)
                output = ""
                key = random.choice(data['endings'])
                count = count - 1
                if count <= 0:
                    break
        else:
            key = random.choice(data['endings'])

    return generated_strings


def run(filename=None, count=10):
    """Given a path to a file, read it, build a library, and generate 10
    sentences from it, printing them.
    """

    if filename is None:
        filename = raw_input('Enter name of a textfile to read: ')

    data = train(filename)
    results = generate(data, count)
    for r in results:
        print("\n{0}".format(r))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(sys.argv[1])  # accept a command-line filename
    else:
        run()
