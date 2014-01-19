CREATE TABLE Users(
       ID INTEGER PRIMARY KEY,
       username TEXT,
       permissions INTEGER,
       password TEXT,
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

INSERT INTO "Users" VALUES(1, 'openic_admin',127,'688126b498e5dc07df6df18b1c786bbc',X'80025D2E');

INSERT INTO Users_Groups VALUES(NULL,1,1);
INSERT INTO Users_Groups VALUES(NULL,1,3);
