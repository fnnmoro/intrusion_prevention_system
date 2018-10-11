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
        db.execute(
            'INSERT INTO flows (ts, te, ismc, odmc, sa, da, pr, iflg, sp, dp, '
            'td, ipkt, ibyt, bps, bpp, pps, flw, lbl) VALUES (?, ?, ?, ?, ?, ?, '
            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (str(entry[0]), str(entry[1]), entry[2], entry[3], entry[4],
             entry[5], entry[6], str(entry[7]), entry[8], entry[9], entry[10],
             entry[11], entry[12], entry[13], entry[14], entry[15], entry[16],
             int(entry[17]))
        )

    db.commit()

    print("number of flows", db.execute('SELECT count(1) FROM flows').fetchall())