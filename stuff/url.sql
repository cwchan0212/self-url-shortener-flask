-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               PostgreSQL 15.0, compiled by Visual C++ build 1914, 64-bit
-- Server OS:                    
-- HeidiSQL Version:             12.3.0.6589
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES  */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table public.url
CREATE TABLE IF NOT EXISTS "url" (
	"url_id" INTEGER NOT NULL DEFAULT 'nextval(''url_url_id_seq''::regclass)',
	"url_short_url" VARCHAR(25) NULL DEFAULT NULL,
	"url_long_url" TEXT NULL DEFAULT NULL,
	"url_description" TEXT NULL DEFAULT NULL,
	"url_created_date" TIMESTAMP NULL DEFAULT 'CURRENT_TIMESTAMP',
	"url_updated_date" TIMESTAMP NULL DEFAULT 'CURRENT_TIMESTAMP',
	PRIMARY KEY ("url_id"),
	UNIQUE INDEX "url_url_short_url_key" ("url_short_url")
);

-- Dumping data for table public.url: 14 rows
/*!40000 ALTER TABLE "url" DISABLE KEYS */;
INSERT INTO "url" ("url_id", "url_short_url", "url_long_url", "url_description", "url_created_date", "url_updated_date") VALUES
	(1, 'aa7254', 'https://replit.com/@cwchan0212/hyperiondev-capstone1?embed=true', 'Capstone Project 1: Financial Calculator', '2023-02-02 17:22:57.887947', '2023-02-04 14:10:51.37284'),
	(2, '392aa7', 'https://replit.com/@cwchan0212/hyperiondev-capstone2?embed=true', 'Capstone Project 2: Task Manager', '2023-02-02 17:24:33.323112', '2023-02-04 14:11:19.176391'),
	(3, 'bc9cd6', 'https://replit.com/@cwchan0212/hyperiondev-capstone3?embed=true', 'Capstone Project 3: Task Manager (Advanced)', '2023-02-02 17:24:56.317357', '2023-02-04 14:11:37.689598'),
	(4, '995ce4', 'https://replit.com/@cwchan0212/hyperiondev-capstone4?embed=true', 'Capstone Project 4: Inventory Management System', '2023-02-03 13:33:42.378675', '2023-02-04 14:12:04.676722'),
	(5, '7351b3', 'https://replit.com/@cwchan0212/hyperiondev-capstone5?embed=true', 'Capstone Project 5: Bookstore Management System', '2023-02-04 13:56:06.209532', '2023-02-04 14:12:29.173883'),
	(6, '1842e4', 'https://replit.com/@cwchan0212/hyperiondev-capstone1-gui?embed=true', 'Capstone Project 1: Financial Calculator (Advanced)', '2023-02-04 14:12:53.955382', '2023-02-04 14:28:04.97479'),
	(7, 'a4563b', 'https://hyperiondev-capstone3-django.cwchan0212.repl.co/', 'Capstone Project 3 - Task Manager (Django)', '2023-02-04 14:15:47.474489', '2023-02-04 14:28:09.588374'),
	(8, '9b0294', 'https://hyperiondev-capstone5-flask.cwchan0212.repl.co/', 'Capstone Project 5: Bookstore Management System (Flask)', '2023-02-04 14:29:12.590838', '2023-02-04 14:29:31.55538'),
	(9, 'be3c83', 'https://self-exchange-rate2.cwchan0212.repl.co/', 'Side Project: Exchange Rate Tracker', '2023-02-04 14:31:21.990263', '2023-02-04 14:31:21.990263'),
	(10, '63b56e', 'https://self-staff-scheduler.cwchan0212.repl.co/', 'Side Project: Staff Scheduler', '2023-02-04 14:31:52.310574', '2023-02-04 14:31:52.310574'),
	(11, '6d71a5', 'https://www.linkedin.com/in/cwchanst/', 'My LinkedIn URL', '2023-02-04 18:27:48.572628', '2023-02-04 18:27:48.572628'),
	(12, 'bb9eaa', 'https://github.com/cwchan0212', 'My GitHub', '2023-02-04 18:28:06.102119', '2023-02-04 18:28:06.102119'),
	(13, '49e347', 'https://replit.com/@cwchan0212', 'My Replit', '2023-02-04 18:28:28.471523', '2023-02-04 18:28:28.471523'),
	(14, 'd60640', 'https://cwchan0212.github.io/', 'My Personal Portfolio Page', '2023-02-04 18:27:28.630099', '2023-02-04 20:12:06.731998');
/*!40000 ALTER TABLE "url" ENABLE KEYS */;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
