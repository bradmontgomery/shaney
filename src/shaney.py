#!/usr/bin/env python

# shaney.py by Greg McFarlane
# some editing by Joe Strout
# search for "Mark V.  Shaney" on the WWW for more info!

import sys
import random
import string


def run(filename=''):
    if filename == '':
        file = open(raw_input('Enter name of a textfile to read: '), 'r')
    else:
        file = open(filename, 'r')

    text = file.read()
    file.close()
    words = string.split(text)

    end_sentence = []
    data = {}
    prev1 = ''
    prev2 = ''

    for word in words:
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
        print 'Sorry, there are no sentences in the text.'
        return

    key = ()
    count = 10

    while 1:
        if key in data:
            word = random.choice(data[key])
            print word,

            key = (key[1], word)
            if key in end_sentence:
                print "\n\n{0}\n".format("-" * 80)
                count = count - 1
                key = random.choice(end_sentence)
                if count <= 0:
                    break
        else:
            key = random.choice(end_sentence)


# immediate-mode commands, for drag-and-drop or execfile() execution
if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(sys.argv[1])  # accept a command-line filename
    else:
        run()
else:
    print "Module shaney imported."
    print "To run, type: shaney.run()"
    print "To reload after changes to the source, type: reload(shaney)"
