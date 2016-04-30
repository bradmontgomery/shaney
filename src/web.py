import argparse

from flask import Flask
from flask import render_template

import shaney


global LIMIT  # Limit the number of words displayed.
app = Flask(__name__)
shaney_bot = None


class Shaney:
    def __init__(self, file, order=2):
        if order == 3:
            self.data = shaney.train3(file)
            self._generate = shaney.generate3
        else:
            self.data = shaney.train(file)
            self._generate = shaney.generate

    def quote(self):
        try:
            quotes = self._generate(self.data, count=1, verbose=False)
            quote = quotes[0].strip()
        except:
            quote = "oops. I failed to generate a quote. Try again?"
        return quote


@app.route('/')
def hello_world():
    if shaney_bot:
        quote = shaney_bot.quote()
    else:
        quote = "oops."

    if LIMIT:  # limit the number of words in the quote
        words = quote.split()
        while len(words) > LIMIT:
            words = words[:-1]
        quote = " ".join(words)
    return render_template('index.html', quote=quote)


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
        "-l",
        "--limit",
        help="Number of words to display",
        type=int,
        default=None
    )
    args = parser.parse_args()

    LIMIT = args.limit
    shaney_bot = Shaney(args.filename, args.order)
    app.run()
