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


def write(msg, verbose=False):
    """Write a message to standard out if verbose is true."""
    if verbose:
        sys.stdout.write(u"{0}\n".format(msg))


def read(filename, verbose=False):
    """Reads content from the file, does a little bit of cleanup, and returns
    a list of words.

    """
    # Some informative output (if running in verbose mode)
    write("-" * 80, verbose)
    write("Reading File.", verbose)

    content = open(filename, 'r').read()
    # kill the unicode things (e.g. smart quotes)
    content = content.decode('utf8').encode('ascii', 'ignore')
    # condense all whitespace chars into a single space
    content = re.sub('\s+', ' ', content)
    # Remove everything but words, major punctuation, and single quotes
    content = re.sub('[^A-Za-z\.\?\!\' ]+', '', content)
    content = string.split(content)

    write("Read {0} lines.".format(len(content)), verbose)
    return content


def analyze_text(data, verbose=True):
    """Given the dictionary of trained data, print the mean word sample size.
    Larger numbers yield better results.

    This function assumes you want to print things to stdout.

    """

    size = 0
    for word_list in data.values():
        size += len(word_list)
    avg_sample_size = float(size) / len(data.values())

    write("-" * 80, verbose)
    write("Average Sample Size: {0}".format(avg_sample_size), verbose)
    if avg_sample_size < 2:
        write("--> This is a small sample size, and is probably like a poor "
              "at generating text.", verbose)
    if avg_sample_size > 2:
        write("--> This looks like a decent sample size.", verbose)
    else:
        write("--> This looks like a good sample size.", verbose)
    write("-" * 80, verbose)


def train(filename, verbose=False):
    """Reads a file, building the data model used to generate text.
    Returns trained data; a dictionary of the form:

        { content: {},
          endings: [] }

    """
    write("Training...", verbose)
    endings = []  # Pairs of words that end a sentence
    data = {}  # Key: Pairs of words, Values: List of words that follow those pairs.

    # and here's a pair of words that we encounter in a text.
    prev1 = ''
    prev2 = ''

    # Load up a dictionary of data from the input files.
    for word in read(filename, verbose):
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
    if verbose:
        analyze_text(data)
    return {'content': data, 'endings': endings}


def generate(data, count=10, verbose=False):
    """Given the appropriate data library (dict of 'content' and 'endings' keys),
    this will generate text strings.

    Returns a list of `count` strings.

    """
    write("Generating output:", verbose)

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


def run(filename=None, count=10, verbose=False):
    """Given a path to a file, read it, build a library, and generate 10
    sentences from it, printing them.
    """
    write("Running in verbose mode.", verbose)
    if filename is None:
        filename = raw_input('Enter name of a textfile to read: ')

    data = train(filename, verbose)
    results = generate(data, count, verbose)
    for r in results:
        write("\n* {0}".format(r), verbose)
    write("-" * 80, verbose)
    return results


if __name__ == '__main__':
    filename = None if len(sys.argv) < 2 else sys.argv[1]
    run(filename, verbose=True)  # accept a command-line filename
