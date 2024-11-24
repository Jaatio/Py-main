drop database if exists p4_question;
create database if not exists p4_question;
use p4_question;


CREATE TABLE user_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_log ENUM('Менеджер', 'Партнер') NOT NULL,
    login VARCHAR(24),
    password VARCHAR(24),
    UNIQUE (login)
);

-- Таблица для партнеров
CREATE TABLE Partners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partner_type ENUM('ЗАО','ООО','ПАО','ОАО'),
    partner_name VARCHAR(255),
    director_name VARCHAR(255),
    email VARCHAR(100),
    partner_phone VARCHAR(20),
    ur_adress VARCHAR(255),
    inn VARCHAR(12),
    rating int (3)
);

CREATE TABLE Partners_products(
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name varchar(255),
    partner_name varchar(255),
    product_quantity int(15),
    selling_data DATETIME 
    
);

CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    partner_id INT,
    partner_name varchar(255),
	product_type varchar(255),
    product_name varchar(255),
	total_price int(10),  
    total_amount DECIMAL(10, 2),
	order_date TIMESTAMP ,
    status ENUM('created', 'canceled', 'paid', 'in_production', 'completed')


);

create table products(
	id INT AUTO_INCREMENT PRIMARY KEY,
    product_type varchar(255),
    product_name varchar(255),
    articul int,
    min_price FLOAT (13.2)

);


