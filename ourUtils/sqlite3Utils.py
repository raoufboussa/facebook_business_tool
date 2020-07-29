import sqlite3
def insertAdInDB(adName,adText,adScore):
    db = sqlite3.connect('mydb2')#connect if exists or creates if not
    cursor = db.cursor()
    cursor.execute('''INSERT INTO Ads(name, text, score) VALUES(?,?,?)''', (adName,adText,adScore))
    print(' inserted ad ')
    db.commit()

#only create once (can simply execute this function in python shell in the desired folder)
def createDb():
    db = sqlite3.connect('mydb2')#connect if exists or creates if not
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE Ads(id INTEGER PRIMARY KEY, Name TEXT,Text TEXT,Score INTEGER)''')
    db.commit()
    db.close()
