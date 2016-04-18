-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema MashaProject
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema MashaProject
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `MashaProject` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
USE `MashaProject` ;

-- -----------------------------------------------------
-- Table `MashaProject`.`Position`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MashaProject`.`Position` (
  `idPosition` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idPosition`),
  UNIQUE INDEX `idPosition_UNIQUE` (`idPosition` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MashaProject`.`Subordinaries`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MashaProject`.`Subordinaries` (
  `idSubordinaries` INT NOT NULL AUTO_INCREMENT,
  `manager` INT NOT NULL,
  `employee` INT NOT NULL,
  PRIMARY KEY (`idSubordinaries`),
  UNIQUE INDEX `idSubordinaries_UNIQUE` (`idSubordinaries` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MashaProject`.`Employee`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MashaProject`.`Employee` (
  `idEmployee` INT NOT NULL AUTO_INCREMENT,
  `position` INT NULL,
  `name` VARCHAR(100) NULL,
  `Employee_idEmployee` INT NOT NULL,
  UNIQUE INDEX `idEmployee_UNIQUE` (`idEmployee` ASC),
  PRIMARY KEY (`idEmployee`),
  INDEX `fk_Employee_Employee1_idx` (`Employee_idEmployee` ASC),
  CONSTRAINT `fk_Employee_Position1`
    FOREIGN KEY (`idEmployee`)
    REFERENCES `MashaProject`.`Position` (`idPosition`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Employee_Subordinaries1`
    FOREIGN KEY (`idEmployee`)
    REFERENCES `MashaProject`.`Subordinaries` (`employee`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Employee_Subordinaries2`
    FOREIGN KEY (`idEmployee`)
    REFERENCES `MashaProject`.`Subordinaries` (`manager`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Employee_Employee1`
    FOREIGN KEY (`Employee_idEmployee`)
    REFERENCES `MashaProject`.`Employee` (`idEmployee`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MashaProject`.`Task`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MashaProject`.`Task` (
  `idTask` INT NOT NULL AUTO_INCREMENT,
  `creationDate` DATETIME NULL,
  `finishDate` DATETIME NULL,
  `assignee` INT NULL,
  `status` VARCHAR(45) NULL,
  `description` VARCHAR(255) NULL,
  `title` VARCHAR(20) NULL,
  PRIMARY KEY (`idTask`),
  UNIQUE INDEX `idTask_UNIQUE` (`idTask` ASC),
  INDEX `fk_Task_Employee1_idx` (`assignee` ASC),
  CONSTRAINT `fk_Task_Employee1`
    FOREIGN KEY (`assignee`)
    REFERENCES `MashaProject`.`Employee` (`idEmployee`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `MashaProject`.`CalendarMark`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `MashaProject`.`CalendarMark` (
  `idCalendarMark` INT NOT NULL AUTO_INCREMENT,
  `employee` INT NOT NULL,
  `date` DATETIME NOT NULL,
  `type` INT NULL,
  PRIMARY KEY (`idCalendarMark`),
  UNIQUE INDEX `idCalendarMark_UNIQUE` (`idCalendarMark` ASC),
  INDEX `fk_CalendarMark_Employee1_idx` (`employee` ASC),
  CONSTRAINT `fk_CalendarMark_Employee1`
    FOREIGN KEY (`employee`)
    REFERENCES `MashaProject`.`Employee` (`idEmployee`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
