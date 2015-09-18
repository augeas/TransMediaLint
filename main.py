from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests

import json

from lint import lintify

app = Flask(__name__)

@app.route('/')
def root(name=None):
    return render_template('index.html', name=name)

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    url = request.form['url']
    #print url
    response = requests.get(url)
    content = ''.join([str(s) for s in BeautifulSoup(response.text).body.contents])
    count, annotations, newContent = lintify(content)
    print count
    return json.dumps({'count':count, 'content':newContent})

if __name__ == '__main__':
    app.run()