Mark V. Shaney
==============

_SLIDES: I've given a few talks at meetups and conferences on Markov Chains,
most recently at DevSpace 2016. You can find [those slides on speakerdeck](https://speakerdeck.com/bkmontgomery/fun-with-markov-chains-devspace-2016)_.

----

This started out as a copy of the `shaney.py` Markov Chain implementation taken
from [Yisong Yue's website](http://www.yisongyue.com/shaney/).

I've refactored the code a bit, but the important parts are still pretty much
the same. This version works with Python 3.


That site describes shaney as:

> Mark V. Shaney is a Python script which takes in a typically fairly large body
> of text and generates another [smaller] body of text which resembles the
> original, usually with hilarious side-effects. This page is a web version of
> the script for all those people fortunate enough to have never acquired a
> savviness for nerdy coding. Mark V. Shaney was first written by Bruce Ellis.

According to comments in the file, this python script was written by Greg McFarlane
with some editing by Joe Strout.

I've also cleaned it up a bit.

Usage
-----

Run the file, and pass it a path to some training text.

    python shaney.py /path/to/text.txt -v


For additional options, run `python shaney.py -h`. Notably, this script
implements both a 2nd-order (the original) and 3rd-order markov chain. To
run the 3rd-order chain, use:

    python shaney.py /path/to/text.txt -v -o 3



Web App
-------

There's also a simple web app that will display quotes generated from training
data. Run it with:

    python web.py /path/to/text.txt


