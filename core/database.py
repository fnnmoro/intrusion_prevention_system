import os
import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))


def store_flows(flows):
    db = sqlite3.connect('../instance/flows.sqlite')

    for entry in flows:
        print(type(entry[7]))
        db.execute(
            'INSERT INTO flows (ts, te, ismc, odmc, sa, da, pr, iflg, sp, dp, '
            'td, ipkt, ibyt, bps, bpp, pps, flw, lbl) VALUES (?, ?, ?, ?, ?, ?, '
            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entry)


    db.commit()

    print("number of flows", db.execute('SELECT count(1) FROM flows').fetchall())
    print("number of flows", db.execute('SELECT count(1) FROM flows').fetchone())