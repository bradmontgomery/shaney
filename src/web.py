from flask import Flask
from flask import render_template
from shaney import train, generate


app = Flask(__name__)


class Shaney:
    def __init__(self):
        self.data = train("/Users/brad/Downloads/markov-corpus/foxnews.txt")

    def quote(self):
        quotes = generate(self.data, count=1, verbose=False)
        try:
            quote = quotes[0].strip()
        except:
            quote = "oops. I failed to generate a quote. Try again?"
        return quote

shaney_bot = Shaney()


@app.route('/')
def hello_world():
    return render_template('index.html', quote=shaney_bot.quote())


if __name__ == '__main__':
    app.run()
