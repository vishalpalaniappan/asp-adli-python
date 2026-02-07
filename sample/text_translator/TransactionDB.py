import sqlite3
import atexit
import uuid

class TransactionDB():

    def __init__(self):
        atexit.register(self.cleanup_function)
        self.initializeDB()

    def cleanup_function(self):
        self.conn.close()

    def initializeDB(self):

        self.conn = sqlite3.connect("translations.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS translation_jobs (
            job_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            uid      TEXT NOT NULL UNIQUE,
            english  TEXT NOT NULL,
            french   TEXT,
            spanish  TEXT,
            tamil    TEXT,
            done     INTEGER NOT NULL DEFAULT 0
        );
        """)
        self.conn.commit()

    def addJob(self, data):
        uid = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO translation_jobs (uid, english)
            VALUES (?, ?)
            """,
            (uid, data)
        )
        self.conn.commit()

        return {
            "uid": uid,
            "value": {"data": data}
        }
    
    def addTranslation(self, msg):
        self.conn.execute(
            f"""
            UPDATE translation_jobs
            SET {msg["value"]["language"]} = ?
            WHERE uid = ?
            """,
            (msg["value"]["translated"], msg["uid"])
        )
        self.conn.commit()


    def isDone(self, uid):
        cur = self.conn.execute(
            """
            SELECT
                french  IS NOT NULL
            AND spanish IS NOT NULL
            AND tamil   IS NOT NULL
            FROM translation_jobs
            WHERE uid = ?
            """,
            (uid,)
        )
        row = cur.fetchone()
        return bool(row[0]) if row else False
    
    def setDone(self, uid):
        self.conn.execute(
            """
            UPDATE translation_jobs
            SET done = 1
            WHERE uid = ?
            """,
            (uid,)
        )
        self.conn.commit()


    