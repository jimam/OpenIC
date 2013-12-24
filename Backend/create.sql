CREATE TABLE IF NOT EXISTS Users(
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT,
       permissions INTEGER,
       password BLOB,
       salt BLOB
);

CREATE TABLE IF NOT EXISTS Comments(
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       userID INTEGER,  
       comment TEXT, 
       timestamp TEXT,
       CONSTRAINT userID FOREIGN KEY (ID) REFERENCES Users(ID)
);
