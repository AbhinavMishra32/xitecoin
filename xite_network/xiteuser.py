from xitelib.node import Blockchain, User
from ..settings.settings import Settings
import sqlite3

BLOCKCHAIN_NAME = Settings.BLOCKCHAIN_NAME.value


class XiteUser(User):
    def __init__(self, username: str, password: str, blockchain: Blockchain):
        super().__init__(username, blockchain)

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                    )''')
        
        self.username = username
        self.password = password
        c.execute('''
            INSERT INTO users (username, password) VALUES (?,?)''', (username, password))
        
        conn.commit()
        c.execute('PRAGMA integrity_check')
        print(c.fetchone())
        conn.close()

XiteUser("abhinav123", "myasp124124", Blockchain("testsetestset"))