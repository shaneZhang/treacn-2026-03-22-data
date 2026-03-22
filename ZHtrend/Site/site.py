# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, json
import sys

sys.path.append("..")

from ZHtrend.DB import db

app = Flask(__name__)


@app.route('/API/getTrend', methods=["POST"])
def getTrend():
    date = json.loads(request.get_data().decode('utf-8'))
    ret = db.SITEGetTrend(date["date"])
    return json.dumps(ret, ensure_ascii=False)


@app.route('/')
def hello():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
