CREATE DATABASE Master_pol;

USE Master_pol;

CREATE TABLE System_mp(
System_id INT,
Product_id INT,
Provider_id int,
Employee_id int,
Materials_id int,
Partners_id int
);

CREATE TABLE Provider(
PROVIDER_ID INT,
P_name varchar (20),
INN int (5),
supply_history varchar (20),
FOREIGN KEY (PROVIDER_ID) REFERENCES System_mp(Provider_id)
);

CREATE TABLE Materials(
MATERIAL_ID INT,
m_type VARCHAR(20),
m_name VARCHAR(20),
provider VARCHAR(20),
FOREIGN KEY (MATERIAL_ID) REFERENCES System_mp(Materials_id)
);

CREATE TABLE Partners(
PARTNER_ID INT,
partner_type VARCHAR(20),
company_name VARCHAR(20),
ur_address VARCHAR(20),
director_fio VARCHAR(20),
Telephone VARCHAR(20) NOT NULL UNIQUE,
email VARCHAR(20),
rating INT,
selling_place VARCHAR(200),
product_history VARCHAR(20),
FOREIGN KEY (PARTNER_ID) REFERENCES System_mp(Partners_id)
);

CREATE TABLE Employee(
EMPLOYEES_ID INT,
fio VARCHAR(20),
birthday VARCHAR(20),
passport_inf_id INT,
bank_recvisits_id INT,
Family VARCHAR(20),
Health VARCHAR(20),
FOREIGN KEY (EMPLOYEES_ID) REFERENCES System_mp(Employee_id)
);

CREATE TABLE Passport_inf(
P_INF_ID INT,
Serias INT(3) NOT NULL UNIQUE,
Number_p INT(5) NOT NULL UNIQUE,
FOREIGN KEY (P_INF_ID) REFERENCES Employee(passport_inf_id)
);

CREATE TABLE bank_recvisits_inf(
RECVISITS_ID INT,
bank_name VARCHAR(20),material_type_import_bd
BIK INT(8),
INN INT,
BIK INT,
KBK INT,
FOREIGN KEY (RECVISITS_ID) REFERENCES Employee(bank_recvisits_id)
);

CREATE TABLE Product (
  Product_id INT PRIMARY KEY,
  articul VARCHAR(50) NOT NULL,
  p_type VARCHAR(50) NOT NULL,
  p_name VARCHAR(100) NOT NULL,
  p_description TEXT,
  image VARCHAR(255),
  min_price_for_partner DECIMAL(10,2) NOT NULL,
  length DECIMAL(5,2),
  width DECIMAL(5,2),
  height DECIMAL(5,2),
  weight_without_package DECIMAL(7,2),
  weight_with_package DECIMAL(7,2),
  quality_certificate VARCHAR(255),
  standart_number VARCHAR(50),
  history_of_min_price_for_partner TEXT,
  production_time INT NOT NULL,
  cost DECIMAL(10,2) NOT NULL,
  workshop_number INT NOT NULL,
  staff_quantity INT NOT NULL,
  materials_for_production TEXT
);