-- run to set up the game database on a new computer, database name should be "Farm"

CREATE TABLE Users(
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    pos_row INT NOT NULL,
    pos_col INT NOT NULL
);

CREATE INDEX username_index ON Users(username);

CREATE TABLE Crops(
    coords VARCHAR(255) NOT NULL UNIQUE,
    crop_type INT NOT NULL,
    growth INT NOT NULL
);

CREATE INDEX crops_index ON Crops(coords);

CREATE TABLE Profit(
    val INT NOT NULL
);

INSERT INTO Profit (val) VALUES (0);