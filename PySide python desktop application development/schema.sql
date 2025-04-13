CREATE DATABASE IF NOT EXISTS billing_app;

USE billing_app;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    date DATE,
    amount DECIMAL(10,2),
    details TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
