CREATE DATABASE IF NOT EXISTS real_estate;

USE real_estate;


-- ---------------- CUSTOMERS ----------------

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100)
);


-- ---------------- AGENTS ----------------

CREATE TABLE IF NOT EXISTS agents (
    agent_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100)
);


-- ---------------- PROPERTIES ----------------

CREATE TABLE IF NOT EXISTS properties (
    property_id INT PRIMARY KEY AUTO_INCREMENT,
    property_type VARCHAR(50),
    location VARCHAR(100),
    price DECIMAL(12,2),
    status VARCHAR(20),
    agent_id INT,

    FOREIGN KEY (agent_id)
    REFERENCES agents(agent_id)
);


-- ---------------- TRANSACTIONS ----------------

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    property_id INT,
    agent_id INT,
    amount DECIMAL(12,2),
    transaction_date DATE,

    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id),

    FOREIGN KEY (property_id)
    REFERENCES properties(property_id),

    FOREIGN KEY (agent_id)
    REFERENCES agents(agent_id)
);


-- ---------------- SAMPLE AGENTS ----------------

INSERT INTO agents
(name, phone, email)
VALUES
('Arun Kumar', '9876543210', 'arun@gmail.com'),
('Priya Sharma', '9876543211', 'priya@gmail.com');


-- ---------------- SAMPLE CUSTOMERS ----------------

INSERT INTO customers
(name, phone, email)
VALUES
('Rahul', '9876543220', 'rahul@gmail.com'),
('Sneha', '9876543221', 'sneha@gmail.com');


-- ---------------- SAMPLE PROPERTIES ----------------

INSERT INTO properties
(property_type, location, price, status, agent_id)
VALUES
('Villa', 'Chennai', 8000000, 'Available', 1),
('Apartment', 'Bangalore', 5500000, 'Available', 2),
('Plot', 'Chennai', 4000000, 'Available', 1);


-- ---------------- SAMPLE TRANSACTION ----------------

INSERT INTO transactions
(customer_id, property_id, agent_id, amount, transaction_date)
VALUES
(1, 1, 1, 8000000, '2026-10-07');