import sqlite3
from core import app

def create_database():
    db = sqlite3.connect(app.config['DATABASE'])

    with open('schema.sql') as sql_script:
        db.executescript(sql_script.read())

    db.close()


def store_flows(flows):
    db = sqlite3.connect(app.config['DATABASE'])

    for entry in flows:
        entry[7] = str(entry[7])
        entry[-1] = int(entry[-1])

        db.execute(
            'INSERT INTO flows (ts, te, ismc, odmc, sa, da, pr, iflg, sp, dp, '
            'td, ipkt, ibyt, bps, bpp, pps, flw, lbl) VALUES (?, ?, ?, ?, ?, ?, '
            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entry)
    db.commit()

    db.close()


def get_anomalous_flows():
    db = sqlite3.connect(app.config['DATABASE'])

    anomalous_flows = db.execute('SELECT sa, da, COUNT(flw) FROM flows '
                                 'WHERE lbl = 1 GROUP BY sa').fetchall()

    db.close()

    return anomalous_flows
