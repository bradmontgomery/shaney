Mark V. Shaney
==============

This started out as a copy of the `shaney.py` Markov Chain implementation taken
from [Yisong Yue's website](http://www.yisongyue.com/shaney/).

I've refactored the code a bit, but the important parts are still pretty much
the same.


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

    python shaney.py /path/to/text.txt


