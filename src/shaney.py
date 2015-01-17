#!/usr/bin/env python
"""
shaney.py by Greg McFarlane some editing by Joe Strout
search for "Mark V.  Shaney" on the WWW for more info!

"""
from __future__ import print_function

import sys
import random
import string



def run(filename='', count=10):
    if filename == '':
        file = open(raw_input('Enter name of a textfile to read: '), 'r')
    else:
        file = open(filename, 'r')

    end_sentence = []
    data = {}
    prev1 = ''
    prev2 = ''

    # Load up a dictionary of data from the input files.
    for word in string.split(file.read()):
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
    file.close()

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
