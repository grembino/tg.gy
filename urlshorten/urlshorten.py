#!/var/www/tg.gy/urlshorten/venv/bin/python3.5


from flask import Flask, request, render_template, redirect
from urllib.parse import urlparse
from math import floor
import base64
import string, psycopg2


host = 'https://tg.gy/'

def checkTable():
    createTable = """
        CREATE TABLE WEB_URL(
            ID SERIAL PRIMARY KEY,
            URL TEXT NOT NULL
        );
        """
    with psycopg2.connect(dbname="url.db", user="postgres", password="tggydb") as conn:
        cur = conn.cursor()
        try:
            cur.execute(createTable)
        except psycopg2.ProgrammingError:
            pass

def Base62(num, ref=62):
    lib = string.digits + string.ascii_lowercase + string.ascii_uppercase
    loc = num % ref              # location
    res = lib[loc]               # Calculates initial result char
    y = floor(num / ref)         # Defines remaining loops to gen result string
    while y:                 # Keeps adding characters to string until y is 0
        loc = y % ref
        y = floor(y / ref)
        res = lib[int(loc)] + res
    return res


def Base10(num, ref=62):
    lib = string.digits + string.ascii_lowercase + string.ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = ref * res + lib.find(num[i])   # Checks library for matching char
    return res                               # and reports location in string back



app = Flask(__name__)

    # Generates short url when a long url is added
@app.route('/', methods=['GET', 'POST'])
def urlshorten():
    if request.method == 'POST':
        originalUrl = str.encode(request.form.get('url'))
        if urlparse(originalUrl).scheme == b'':
            longUrl = b'http://' + originalUrl
        else:
            longUrl = originalUrl
        
        stored = str(base64.urlsafe_b64encode(longUrl),'utf-8')
        with psycopg2.connect(dbname="url.db", user="postgres", password="tggydb") as conn:
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO WEB_URL (URL) VALUES (%s) RETURNING ID',
                [stored]
            )
            shortened = Base62(cur.fetchone()[0])
        return render_template('index.html', shortUrl=host + shortened)
    return render_template('index.html')



     # Links long url if short url is used
@app.route('/<shortUrl>')
def redirShortUrl(shortUrl):
    decodedUrl = Base10(shortUrl)
    url = host                
    with psycopg2.connect(dbname="url.db", user="postgres", password="tggydb") as conn:
        cur = conn.cursor()
        cur.execute('SELECT URL FROM WEB_URL WHERE ID=%s', [decodedUrl])
        short = cur.fetchone()
        try:
            if short is not None:
                url = base64.urlsafe_b64decode(str.encode(short[0]))
        except Exception as e:
            print('printingexeception')
            print(e)   
    return redirect(url)


if __name__ == '__main__':
    # Checks for database table
    checkTable()
    app.run(host='tg.gy', port=8080, debug=True)	# Port 80 is in use by nginx

