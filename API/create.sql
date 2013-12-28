CREATE TABLE Users(
       ID INTEGER PRIMARY KEY,
       username TEXT,
       permissions INTEGER,
       password TEXT,
       salt TEXT,
       image BLOB       
);

CREATE TABLE Groups(
       ID INTEGER PRIMARY KEY,
       groupname TEXT
);

CREATE TABLE Comments(
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       userID INTEGER,  
       comment TEXT, 
       timestamp TEXT,
       group_name TEXT,
       CONSTRAINT userID FOREIGN KEY (ID) REFERENCES Users(ID)
);

CREATE TABLE Users_Groups(
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       userID INTEGER,
       groupID INTEGER,  
       CONSTRAINT userID  FOREIGN KEY (ID) REFERENCES Users(ID) ,
       CONSTRAINT groupID FOREIGN KEY (ID) REFERENCES Groups(ID)
);

INSERT INTO "Groups" VALUES(1, "all");
INSERT INTO "Groups" VALUES(2, "Banned");
INSERT INTO "Groups" VALUES(3, "group1");

INSERT INTO "Users" VALUES(1, 'openic_admin',127,'09ae76728d35d3f41de600a6df700c02c3f3ba65742c7ed0e667555e11e1aca3c994eeb2c1755ef8261c75ea8d942a68c643fefb99f5ae3dedc2145c80c74666','6831e5dfdf6a456683146334051b34dc',X'80025D2E');

INSERT INTO Users_Groups VALUES(NULL,1,1);
INSERT INTO Users_Groups VALUES(NULL,1,3);
