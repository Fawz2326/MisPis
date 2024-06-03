import sqlite3

database_path = './database.db'

try:
    with sqlite3.connect(database_path) as db:
        cursor = db.cursor()
        queries = [
            """CREATE TABLE IF NOT EXISTS products (
                   id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   name VARCHAR(255) NOT NULL,
                   category VARCHAR(100) NOT NULL,
                   subcategory VARCHAR(100),
                   description TEXT,
                   price DECIMAL(10, 2) NOT NUL
            )""",
            """CREATE TABLE IF NOT EXISTS customers (
                   id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   name VARCHAR(255) NOT NULL,
                   username VARCHAR(255) NOT NULL,
                   password TEXT NOT NULL,
                   contact_details VARCHAR(255),
                   role_id INTEGER NOT NULL,
                   FOREIGN KEY (role_id) REFERENCES roles(id),
                   CONSTRAINT valid_role CHECK (role_id IN (1, 2))
            )""",
    
            """CREATE TABLE IF NOT EXISTS orders (
                   order_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   customer_id INTEGER NOT NULL,
                   order_date DATE NOT NULL,
                   total_amount DECIMAL(10, 2) NOT NULL,
                   FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)    
            )""",
    
            """CREATE TABLE IF NOT EXISTS orderitems (
                   order_item_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   order_id INTEGER NOT NULL,
                   product_id INTEGER NOT NULL,
                   quantity INTEGER NOT NULL,
                   price DECIMAL(10, 2) NOT NULL,
                   FOREIGN KEY (order_id) REFERENCES Orders(order_id),
                   FOREIGN KEY (product_id) REFERENCES Products(product_id)
            )""",
    
            """CREATE TABLE IF NOT EXISTS stock (
                   stock_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   product_id INTEGER NOT NULL,
                   quantity INTEGER NOT NULL,
                   FOREIGN KEY (product_id) REFERENCES Products(product_id) 
            )""",
    
            """CREATE TABLE IF NOT EXISTS deals (
                   deal_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   customer_id INTEGER NOT NULL,
                   product_id INTEGER NOT NULL,
                   deal_date DATE NOT NULL,
                   quantity INTEGER NOT NULL,
                   total_price DECIMAL(10, 2) NOT NULL,
                   FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
                   FOREIGN KEY (product_id) REFERENCES Products(product_id)  
            )"""

            """CREATE TABLE IF NOT EXISTS roles (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL
            )""",
        ]
        for q in queries:
            cursor.execute(q)

        db.commit()

except sqlite3.Error as e:
    print("Ошибка при работе с базой данных:", e)
