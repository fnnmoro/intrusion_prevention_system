DROP TABLE IF EXISTS flows;
DROP TABLE IF EXISTS blacklist;

CREATE TABLE flows (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  te TEXT NOT NULL,
  sa TEXT NOT NULL,
  da TEXT NOT NULL,
  pr TEXT NOT NULL,
  flg TEXT NOT NULL,
  sp INTEGER NOT NULL,
  dp INTEGER NOT NULL,
  td INTEGER NOT NULL,
  ipkt INTEGER NOT NULL,
  ibyt INTEGER NOT NULL,
  bps INTEGER NOT NULL,
  bpp INTEGER NOT NULL,
  pps INTEGER NOT NULL,
  flw INTEGER NOT NULL,
  lbl INTEGER NOT NULL
);

CREATE TABLE blacklist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sa TEXT NOT NULL,
  da TEXT NOT NULL,
  pr TEXT NOT NULL,
  ts TEXT NOT NULL,
  flw INTEGER NOT NULL,
  rule TEXT NOT NULL
);