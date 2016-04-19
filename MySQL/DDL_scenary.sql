-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema rms
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema rms
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rms` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
USE `rms` ;

-- -----------------------------------------------------
-- Table `rms`.`Position`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rms`.`Position` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idPosition_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rms`.`Employee`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rms`.`Employee` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `manager_id` INT NOT NULL,
  `position_id` INT NOT NULL,
  `salary` INT NOT NULL,
  UNIQUE INDEX `idEmployee_UNIQUE` (`id` ASC),
  PRIMARY KEY (`id`),
  INDEX `fk_Employee_Employee1_idx` (`manager_id` ASC),
  INDEX `fk_Employee_Position1_idx` (`position_id` ASC),
  CONSTRAINT `fk_Employee_Employee1`
    FOREIGN KEY (`manager_id`)
    REFERENCES `rms`.`Employee` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Employee_Position1`
    FOREIGN KEY (`position_id`)
    REFERENCES `rms`.`Position` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rms`.`Task`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rms`.`Task` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `creation_date` DATETIME NULL,
  `finish_date` DATETIME NULL,
  `assignee_id` INT NULL,
  `status` VARCHAR(45) NULL,
  `description` VARCHAR(255) NULL,
  `title` VARCHAR(20) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idTask_UNIQUE` (`id` ASC),
  INDEX `fk_Task_Employee1_idx` (`assignee_id` ASC),
  CONSTRAINT `fk_Task_Employee1`
    FOREIGN KEY (`assignee_id`)
    REFERENCES `rms`.`Employee` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rms`.`CalendarMark`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rms`.`CalendarMark` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `employee_id` INT NOT NULL,
  `date` DATETIME NOT NULL,
  `type` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idCalendarMark_UNIQUE` (`id` ASC),
  INDEX `fk_CalendarMark_Employee1_idx` (`employee_id` ASC),
  CONSTRAINT `fk_CalendarMark_Employee1`
    FOREIGN KEY (`employee_id`)
    REFERENCES `rms`.`Employee` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
