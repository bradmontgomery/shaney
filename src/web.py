import sys

from flask import Flask
from flask import render_template
from shaney import train, generate


app = Flask(__name__)
shaney_bot = None


class Shaney:
    def __init__(self, file):
        self.data = train(file)

    def quote(self):
        try:
            quotes = generate(self.data, count=1, verbose=False)
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
    return render_template('index.html', quote=quote)


if __name__ == '__main__':
    filename = None if len(sys.argv) < 2 else sys.argv[1]
    if filename is not None:
        shaney_bot = Shaney(filename)
        app.run()
    else:
        print("\n\nUsage: python web.py /path/to/content.txt\n\n")
