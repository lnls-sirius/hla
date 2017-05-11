USE sirius

CREATE TABLE IF NOT EXISTS element_config (
    name VARCHAR(64) NOT NULL,
    area ENUM('BO', 'SI'),
    PRIMARY KEY(name, area)
);

CREATE TABLE IF NOT EXISTS config_values (
    config_name VARCHAR(64) NOT NULL,
    pvname VARCHAR(32) NOT NULL,
    value FLOAT NOT NULL,

    PRIMARY KEY(config_name, pvname),

    FOREIGN KEY (config_name) REFERENCES element_config(name)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);
