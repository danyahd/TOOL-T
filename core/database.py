import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "trades.db"


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            setup_type TEXT NOT NULL,
            risk_percent REAL NOT NULL,
            stop_loss INTEGER NOT NULL,
            entry_reason TEXT,
            trade_score INTEGER,
            entry_price REAL,
            exit_price REAL,
            result TEXT,
            profit_loss REAL,
            emotion_score INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def save_trade(trade: dict) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO trades (coin, timeframe, setup_type, risk_percent, stop_loss,
            entry_reason, trade_score, entry_price, emotion_score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade["coin"], trade["timeframe"], trade["setup_type"],
        trade["risk_percent"], int(trade["stop_loss"]), trade["entry_reason"],
        trade["trade_score"], trade.get("entry_price"), trade.get("emotion_score"),
        trade.get("notes", "")
    ))
    conn.commit()
    trade_id = cur.lastrowid
    conn.close()
    return trade_id


def get_all_trades() -> list[dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM trades ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_trade_result(trade_id: int, exit_price: float, result: str, profit_loss: float):
    conn = get_connection()
    conn.execute(
        "UPDATE trades SET exit_price=?, result=?, profit_loss=? WHERE id=?",
        (exit_price, result, profit_loss, trade_id)
    )
    conn.commit()
    conn.close()
