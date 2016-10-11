#!/usr/bin/env python
"""
shaney.py by Greg McFarlane some editing by Joe Strout
search for "Mark V.  Shaney" on the WWW for more info!

The original code implements a 2nd-order markov chain, where output is
based on the two previous inputs. This is implemented in this module
using the two functions:

- train -- train the markov chain on some input text.
- generate -- generate text based on the training data.

Additionally, a 3rd-order markov chain is implemented here as well, in
the following functions:

- train3 -- train the markov chain on some input text.
- generate3 -- generate text based on the training data.

Original code listed without a license, here:
http://www.strout.net/info/coding/python/shaney.py

"""
import argparse
import random
import re
import sys
import textwrap

from string import ascii_lowercase


def write(msg, verbose=False):
    """Write a message to standard out if verbose is true."""
    if verbose:
        msg = u"\n".join(textwrap.wrap(msg, width=80))
        sys.stdout.write(u"{0}\n".format(msg))


def read(filename, verbose=False):
    """Reads content from the file, does a little bit of cleanup, and returns
    a list of words.

    """
    # Some informative output (if running in verbose mode)
    write("-" * 80, verbose)
    write("Reading File.", verbose)

    try:
        content = open(filename, 'r').read()
    except Exception:
        # assume we were just given content?
        content = filename

    # kill the unicode things (e.g. smart quotes)
    content = content.encode('ascii', 'ignore').decode('utf8')

    # condense all whitespace chars into a single space
    content = re.sub('\s+', ' ', content)
    content = content.replace(u"\u2018", "'").replace(u"\u2019", "'")
    content = content.replace(u"\u201c", "").replace(u"\u201d", "")

    # Remove everything but words, major punctuation, and single quotes
    content = re.sub('[^A-Za-z\.\?\!\' ]+', '', content)
    content = content.split()

    def _clean(word):
        """A function that helps us filter out certain words."""
        return (
            not word.startswith('http') and  # exclude links
            not word.startswith('@') and  # e.g. tweets, remove mentions
            not (word.startswith('&') and len(word) > 1) and
            word != 'RT' and  # and this
            word != '...' and
            word != 'amp'
        )
    content = list(filter(_clean, content))
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
    elif avg_sample_size > 2:
        write("--> This looks like a decent sample size.", verbose)
    else:
        write("--> This looks like a good sample size.", verbose)
    write("-" * 80, verbose)


def _is_ending(word):
    """How to determin if a word ends a sentence. We can't just look at
    punctuation because things like Mr. or Dr. might be in the middle of
    a sentence. (note: this is clunky, yes, but mean to be simple & OK for
    most cases).

    """
    # Things that should not be considered as an ending.
    non_endings = [
        'mr.', 'mrs.', 'ms.', 'dr.', 'phd.', 'd.c.', 'u.s.', 'a.m.', 'p.m.',
        '.', '.net', 'no.', 'i.e.', 'e.g.', 'st.', 'lt.', 'n.c.', 'adm.',
        'u.n.', 'jr.', 'rep.', 'u.a.e.', 'u.k.', 's.m.a.r.t.', 'sen.', 'inc.',
        'u.i.', 'u.x.', 'sr.', 's.m.', 'ph.',
    ]
    # Peoples' initials are not endings.
    non_endings.extend(["{}.".format(letter) for letter in ascii_lowercase])

    is_number = bool(re.match(r'\d+\.\d+', word))  # Numbers e.g. "4.5"
    if is_number or word.lower().strip() in non_endings:
        return False

    endings = ['.', '?', '!', ';']  # Things we DO consider sentence endings.
    return any([word.endswith(punct) for punct in endings])


def train(filename, verbose=False):
    """Reads a file, building the data model used to generate text.
    Returns trained data; a dictionary of the form:

        { content: {},
          endings: [] }

    """
    write("Training...", verbose)
    endings = set()  # Pairs of words that end a sentence
    # Our Data Dict:
    # - Key: Pairs of words
    # - Values: List of words that follow those pairs.
    data = {}

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
                if _is_ending(key[-1]):
                    endings.add(key)

        prev2 = prev1
        prev1 = word

    assert endings != set(), "Sorry, there are no sentences in the text."
    if verbose:
        analyze_text(data)

    return {'content': data, 'endings': list(endings)}


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


def train3(filename, verbose=False):
    """Reads a file, building the data model used to generate text using a 3rd-
    order markof chain. That is, looking at 3 words at a time instead of a pair.

    Returns trained data; a dictionary of the form:

        { content: {},
          endings: [] }

    """
    write("Training...", verbose)
    endings = []  # Words (keys) that end a sentence
    # Our Data Dict:
    # - Key: Triples of words
    # - Values: List of words that follow those.
    data = {}

    # and here's the group of words that we encounter in a text.
    prev1 = ''
    prev2 = ''
    prev3 = ''

    # Load up a dictionary of data from the input files.
    for word in read(filename, verbose):

        if prev1 != '' and prev2 != '' and prev3 != '':
            key = (prev3, prev2, prev1)

            if key in data:
                data[key].append(word)
            else:
                data[key] = [word]
                if _is_ending(key[-1]):
                    endings.append(key)

        prev3 = prev2
        prev2 = prev1
        prev1 = word

    assert endings != [], "Sorry, there are no sentences in the text."
    if verbose:
        analyze_text(data)

    return {'content': data, 'endings': endings}


def generate3(data, count=10, verbose=False):
    """Given the 3rd-order data library (dict of 'content' and 'endings' keys),
    this will generate text strings.

    Returns a list of `count` strings.

    """
    write("Generating output:", verbose)

    output = ""
    generated_strings = []
    key = None

    while True:
        if key and key in data['content']:
            word = random.choice(data['content'][key])
            output = "{0}{1} ".format(output, word)

            key = (key[1], key[2], word)
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


def run(filename=None, count=10, verbose=False, order=2):
    """Given a path to a file, read it, build a library, and generate 10
    sentences from it, printing them.
    """
    write("Running in verbose mode.", verbose)
    if filename is None:
        filename = input('Enter name of a textfile to read: ')

    if order == 2:
        data = train(filename, verbose)
        results = generate(data, count, verbose)
    elif order == 3:
        data = train3(filename, verbose)
        results = generate3(data, count, verbose)

    for r in results:
        write("* {0}".format(r.strip()), verbose)
        write("\n", verbose)
    write("-" * 80, verbose)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Path to the training text.", type=str)
    parser.add_argument(
        "-o",
        "--order",
        help="Order: how many words to consider at a time? 2 or 3",
        type=int,
        default=2
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Run in verbose mode",
        action='store_true'
    )
    args = parser.parse_args()
    run(args.filename, verbose=args.verbose, order=args.order)
