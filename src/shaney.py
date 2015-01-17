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
    # Remove everything but words, major punctuation, and single quotes
    content = re.sub('[^A-Za-z\.\?\!\' ]+', '', content)
    return string.split(content)


def run(filename=None, count=10):
    if filename is None:
        filename = raw_input('Enter name of a textfile to read: ')

    end_sentence = []
    data = {}
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
                    end_sentence.append(key)
        prev2 = prev1
        prev1 = word

    if end_sentence == []:
        print('Sorry, there are no sentences in the text.')
        return

    # Generate some text.
    key = ()
    output = ""
    while True:
        if key in data:
            word = random.choice(data[key])
            print(word, end=" ")

            key = (key[1], word)
            if key in end_sentence:
                print("\n\n{0}\n".format("-" * 80))
                count = count - 1
                key = random.choice(end_sentence)
                if count <= 0:
                    break
        else:
            key = random.choice(end_sentence)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(sys.argv[1])  # accept a command-line filename
    else:
        run()
