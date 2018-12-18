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

create_database()

@database_connection
def tmp_flows(flows, db=None):
    for entry in flows:
        entry[7] = str(entry[7])
        entry[-1] = int(entry[-1])

        db.execute(
            'INSERT INTO flows (ts, te, ismc, odmc, sa, da, pr, iflg, sp, dp, '
            'td, ipkt, ibyt, bps, bpp, pps, flw, lbl) VALUES (?, ?, ?, ?, ?, ?,'
            '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entry)


@database_connection
def delete_tmp_flows(db=None):
    db.execute('DELETE FROM flows')


@database_connection
def get_anomalous_flows(db=None):
    anomalous_flows = db.execute('SELECT sa, da, COUNT(flw), ts '
                                 'FROM flows GROUP BY sa').fetchall()
    return anomalous_flows


@database_connection
def store_blacklist(entry, db=None):
    db.execute('INSERT INTO blacklist (sa, da, anomalies, ts, rule) '
               'VALUES (?, ?, ?, ?, ?)', entry)


@database_connection
def get_blacklist(db=None):
    blacklist = db.execute('SELECT sa, da, anomalies, ts, rule FROM blacklist').fetchall()

    return blacklist


@database_connection
def get_num_anomalous_flows(db=None):
    num_anomalous_flows = db.execute('SELECT SUM(anomalies) FROM '
                                     'blacklist').fetchone()

    if not num_anomalous_flows[0]: num_anomalous_flows = [0]

    return num_anomalous_flows[0]


@database_connection
def delete_false_positive(rule, db=None):
    db.execute('DELETE FROM blacklist WHERE rule = ?', [rule])
