import sqlite3
import os


# DB FOLDER
DB_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_base_sql"))

# DB CREATE PATHS
PHONE_NUMBERS_DB_FILE = os.path.join(DB_FOLDER, "data/leads.db")
SEEN_MESSAGES_DB_FILE = os.path.join(DB_FOLDER, "data/seen_messages.db")


# DB MANAGER CLASS -------------------------------------------------------------------------------------------------[SC]


class DBManager:
    def __init__(self, default_db):
        self.default_db = default_db


    # DB CONNECT ------------------------------------------------------------------------------------------------------>


    def connect(self, db_file=None):
        return sqlite3.connect(db_file or self.default_db)


    # EXECUTE REQ-S --------------------------------------------------------------------------------------------------->


    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            if commit:
                conn.commit()

        return cursor




# LEADS_DB CLASS -------------------------------------------------------------------------------------------------[SubC]


class LeadDB(DBManager):
    def __init__(self):
        super().__init__(default_db=PHONE_NUMBERS_DB_FILE)


    # PHONE NUMBERS DB INIT ------------------------------------------------------------------------------------------()


    def init_db(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                phone_number TEXT,
                status BOOLEAN,
                service TEXT,
                stage TEXT
        )
        """, commit=True)


    #  UPDATE STAGE --------------------------------------------------------------------------------------------------->

    
    def update_stage(self, stage, user_id):
        self.execute_query("""
            UPDATE leads SET stage = ? WHERE user_id = ?
        """, (stage, user_id), commit=True
        )


    # GET STAGE ------------------------------------------------------------------------------------------------------->


    def get_stage(self, user_id):
        result = self.execute_query("""
            SELECT stage FROM leads WHERE user_id = ?
        """, (user_id,), fetchone=True
        )
        return result[0] if result else None


    # GET ACTIVE STATUS OF USER'S REQUEST TRUE/FALSE ------------------------------------------------------------------>


    def get_status(self, user_id):
        result = self.execute_query("""
            SELECT status FROM leads WHERE user_id = ?
        """, (user_id,), fetchone=True
        )
        return bool(result[0]) if result else None


    # SAVE SERVICE --------------------------------------------------------------------------------------------[NEW ONE]


    def save_service(self, user_id, service):
        self.execute_query("""
            UPDATE leads SET service = ? WHERE user_id = ?
        """, (service, user_id), commit=True
        )


    # GET SERVICE ---------------------------------------------------------------------------------------------[NEW ONE]


    def get_service(self, user_id):
        result = self.execute_query("""
            SELECT service FROM leads WHERE user_id = ?
        """, (user_id,), fetchone=True
        )
        return result[0] if result else None


    # FOR CHECK IF USER EXISTS ---------------------------------------------------------------------------------------->


    def user_exists(self, user_id):
        result = self.execute_query("""
            SELECT 1 FROM leads WHERE user_id = ?
        """, (user_id,), fetchone=True
        )
        return result is not None


    # INSERT NEW USER -------------------------------------------------------------------------------------------------<


    def insert_user(self, user_id, stage):
        self.execute_query("""
            INSERT OR IGNORE INTO leads (user_id, status, stage) VALUES (?, ?, ?)
        """, (user_id, False, stage), commit=True
        )


    # INSERT PHONE NUMBER ---------------------------------------------------------------------------------------------<


    def save_phone_number(self, user_id, phone_number):
        self.execute_query("""
            UPDATE leads SET phone_number = ? WHERE user_id = ?
        """, (phone_number, user_id), commit=True
        )


    # GET ID, PHONE AND STATUS ---------------------------------------------------------------------------------------->


    def get_leads(self):
        result = self.execute_query("""
            SELECT * FROM leads
        """, fetchall=True
        )
        return result


    # DELETE EXISTING USER -------------------------------------------------------------------------------------------->


    def delete_user(self, lead_id):
        self.execute_query("""
            DELETE FROM leads WHERE id = ?
        """, (lead_id,), commit=True)




# SEEN MESSAGES CLASS --------------------------------------------------------------------------------------------[SubC]


class SeenMessages(DBManager):
    def __init__(self):
        super().__init__(default_db=SEEN_MESSAGES_DB_FILE)


    # DB SEEN MESSAGES ID INIT ---------------------------------------------------------------------------------------()


    def init_db(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS seen_messages (
                thread_id TEXT PRIMARY KEY,
                message_id TEXT
        )""", commit=True)


    # GET LAST MESSAGE ------------------------------------------------------------------------------------------------>


    def get_last_message_id(self, thread_id):
        result = self.execute_query("""
            SELECT message_id FROM seen_messages WHERE thread_id = ?
            """, (thread_id,), fetchone=True
        )
        return result[0] if result else None


    # SAVE LAST MESSAGE ID --------------------------------------------------------------------------------------------<


    def save_last_message_id(self, thread_id, message_id):
        self.execute_query("""
            INSERT INTO seen_messages (thread_id, message_id) VALUES (?, ?)
            ON CONFLICT (thread_id) DO UPDATE SET message_id=excluded.message_id
    """, (thread_id, message_id), commit=True)


    # DELETE MESSAGE ID ----------------------------------------------------------------------------------------------->


    # def delete_message_id(self, user_id):
    #     self.execute_query("""
    #         DELETE FROM seen_messages WHERE user_id = ?
    #     """, (user_id,), commit=True)
    #     pass


# INIT DB PHONE NUMBERS OBJECT --------------------------------------------------------------------------------------->>

lead_db = LeadDB()


if __name__ == "__main__":
    leads = lead_db.get_leads()

    for lead in leads:
        print(f"ID: {lead[0]}, Phone: {lead[3]}, Status: {lead[4]}")

