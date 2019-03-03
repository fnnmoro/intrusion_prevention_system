import sqlite3
from core import app


def database_connection(func):
    def conn_close(*args):
        db = sqlite3.connect(app.config['DATABASE'])

        result = func(*args, db)

        db.commit()
        db.close()

        return result

    return conn_close


@database_connection
def create_database(db=None):
    with open('schema.sql') as sql_script:
        db.executescript(sql_script.read())


@database_connection
def insert_flows(flows, db=None):
    for entry in flows:
        entry[5] = str(entry[5])
        entry[-1] = int(entry[-1])

        db.execute('INSERT INTO flows (ts, te, sa, da, pr, flg, sp, dp, td, '
                   'ipkt, ibyt, bps, bpp, pps, flw, lbl) VALUES (?, ?, ?, ?, '
                   '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entry)


@database_connection
def delete_flows(db=None):
    db.execute('DELETE FROM flows')


@database_connection
def create_blacklist(db=None):
    blacklist = db.execute('SELECT sa, da, pr, ts, COUNT(sa) FROM flows '
                           'WHERE lbl = 1 GROUP BY sa, da, pr').fetchall()

    return blacklist


@database_connection
def insert_blacklist(entry, db=None):
    db.execute('INSERT INTO blacklist (sa, da, pr, ts, flw, rule) '
               'VALUES (?, ?, ?, ?, ?, ?)', entry)


@database_connection
def select_blacklist(db=None):
    blacklist = db.execute('SELECT sa, da, ts, pr, flw, rule '
                           'FROM blacklist').fetchall()

    return blacklist

@database_connection
def delete_blacklist(db=None):
    db.execute('DELETE FROM blacklist')


@database_connection
def sum_anomalous_flows(db=None):
    anomalous_flows = db.execute('SELECT SUM(flw) '
                                 'FROM blacklist').fetchone()

    if not anomalous_flows[0]: anomalous_flows = [0]

    return anomalous_flows[0]


@database_connection
def delete_false_positive(rule, db=None):
    db.execute('DELETE FROM blacklist WHERE rule = ?', [rule])
