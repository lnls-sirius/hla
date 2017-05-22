DROP DATABASE IF EXISTS sirius;

CREATE DATABASE sirius CHARACTER SET=utf8mb4;

USE sirius;

CREATE TABLE IF NOT EXISTS section_configuration (
    name VARCHAR(64) NOT NULL,
    section ENUM('BO', 'SI') NOT NULL,
    
    PRIMARY KEY(name, section)
);

CREATE TABLE IF NOT EXISTS section_configuration_values (
    name VARCHAR(64) NOT NULL,
    section ENUM('BO', 'SI') NOT NULL,
    pvname VARCHAR(32) NOT NULL,
    value FLOAT NOT NULL,

    PRIMARY KEY(name, section, pvname),

    FOREIGN KEY (name, section) REFERENCES section_configuration(name, section)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parameter (
  name VARCHAR(64) NOT NULL,
  type ENUM('tune', 'chromaticity') NOT NULL,
  description TEXT NULL,

  PRIMARY KEY(name, type)
);

CREATE TABLE IF NOT EXISTS parameter_values (
  name VARCHAR(64) NOT NULL,
  type ENUM('tune', 'chromaticity') NOT NULL,
  `line` INT NOT NULL,
  `column` INT NOT NULL,
  value FLOAT NOT NULL,

  PRIMARY KEY(name, type, `line`, `column`),

  FOREIGN KEY (name, type) REFERENCES parameter(name, type)
  ON UPDATE CASCADE
  ON DELETE CASCADE
);
