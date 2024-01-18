from xitelib.node import Blockchain, User
from settings.settings import Settings
import sqlite3

BLOCKCHAIN_NAME = Settings.BLOCKCHAIN_NAME.value


class XiteUser(User):
    def __init__(self, username: str, password: str, blockchain: Blockchain):
        super().__init__(username, blockchain)
        self.username = username
        self.password = password

    def save(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                    )''')
        
        c.execute('''
            INSERT INTO users (username, password) VALUES (?,?)''', (self.username, self.password))
        
        conn.commit()
        # c.execute('PRAGMA integrity_check')
        # print(c.fetchone())
        conn.close()

if __name__ == "__main__":
    testUser = XiteUser("abhisnsdfsdf123", "myasp124124", Blockchain("testsetestset"))
    print(testUser.blockchain)