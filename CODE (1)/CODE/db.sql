/*
SQLyog Enterprise - MySQL GUI v6.56
MySQL - 5.5.5-10.1.13-MariaDB : Database - smart_attendance
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

CREATE DATABASE /*!32312 IF NOT EXISTS*/`smart_attendance` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `smart_attendance`;

/*Table structure for table `attendance` */

DROP TABLE IF EXISTS `attendance`;

CREATE TABLE `attendance` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `rno` varchar(100) DEFAULT NULL,
  `in_time` varchar(100) DEFAULT NULL,
  `in_status` varchar(100) DEFAULT NULL,
  `out_time` varchar(100) DEFAULT NULL,
  `out_status` varchar(100) DEFAULT NULL,
  `overall_time` varchar(100) DEFAULT NULL,
  `date1` varchar(100) DEFAULT NULL,
  `m1` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;



insert  into `attendance`(`id`,`rno`,`in_time`,`in_status`,`out_time`,`out_status`,`overall_time`,`date1`,`m1`) values (1,'100','11:26:06','Late Coming',NULL,NULL,NULL,'16-07-2022','July');


