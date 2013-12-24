CREATE TABLE IF NOT EXISTS Users(
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT,
       permissions INTEGER,
       password TEXT,
       salt TEXT,
       group_name TEXT,
       image BLOB       
);

CREATE TABLE IF NOT EXISTS Comments(
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       userID INTEGER,  
       comment TEXT, 
       timestamp TEXT,
       CONSTRAINT userID FOREIGN KEY (ID) REFERENCES Users(ID)
);

INSERT INTO Users VALUES(NULL, "openic_admin", 31, "09ae76728d35d3f41de600a6df700c02c3f3ba65742c7ed0e667555e11e1aca3c994eeb2c1755ef8261c75ea8d942a68c643fefb99f5ae3dedc2145c80c74666", "6831e5dfdf6a456683146334051b34dc", "admins", 0); --Password is OpenIC
