-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema quotedash
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema quotedash
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `quotedash` DEFAULT CHARACTER SET utf8 ;
USE `quotedash` ;

-- -----------------------------------------------------
-- Table `quotedash`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `quotedash`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `fname` VARCHAR(255) NULL DEFAULT NULL,
  `lname` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `quotedash`.`quotes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `quotedash`.`quotes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `quote` TEXT NULL DEFAULT NULL,
  `author` TEXT NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  `posted_by` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_quotes_users1_idx` (`posted_by` ASC) VISIBLE,
  CONSTRAINT `fk_quotes_users1`
    FOREIGN KEY (`posted_by`)
    REFERENCES `quotedash`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `quotedash`.`liked_quotes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `quotedash`.`liked_quotes` (
  `users_id` INT(11) NOT NULL,
  `quotes_id` INT(11) NOT NULL,
  PRIMARY KEY (`users_id`, `quotes_id`),
  INDEX `fk_users_has_quotes_quotes1_idx` (`quotes_id` ASC) VISIBLE,
  INDEX `fk_users_has_quotes_users1_idx` (`users_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_quotes_quotes1`
    FOREIGN KEY (`quotes_id`)
    REFERENCES `quotedash`.`quotes` (`id`),
  CONSTRAINT `fk_users_has_quotes_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `quotedash`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
