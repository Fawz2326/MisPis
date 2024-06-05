import sqlite3
import bcrypt
from prettytable import PrettyTable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Product, OrderItem, Deals, Role, Customers, Stock, Order
from sqlalchemy import inspect

database_path = 'app/db/database.db'

engine = create_engine('sqlite:///app/db/database.db')
Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password, hash_password):
    return bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8'))

def register(username, password, name, role_id):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT * FROM customers WHERE username=?"""
    cursor.execute(query, (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Пользователь с таким логином уже зарегистрирован")
        return

    query = "INSERT INTO customers (username, password, name, role_id) VALUES (?, ?, ?, ?)"
    try:
        password = hash_password(password)
        cursor.execute(query, (username, password, name, role_id))
        db.commit()
        print("Регистрация успешна")
        db.close()
        return existing_user
    except sqlite3.Error as e:
        print("Ошибка при работе с базой данных:", e)


def auth(username, password):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT * FROM customers WHERE username=?"""
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    db.close()

    if user:
        saved_password = user[3]
        if check_password(password, saved_password):
            print("Вы вошли успешно")
            return user
        else:
            print("Неправильный логин или пароль")
            return None
    else:
        print("Неправильный логин или пароль")
        return None

def create_order(cart, user):
    if cart['products']:
        db = sqlite3.connect(database_path)
        cursor = db.cursor()
        cursor.execute("INSERT INTO orders (customer_id) VALUES (?)", (user[0],))
        db.commit()

        cursor.execute("SELECT id FROM orders WHERE customer_id = (?) ORDER BY id DESC LIMIT 1", (user[0],))
        order = cursor.fetchone()[0]

        total_price = 0
        data_products = []
        if cart['products']:
            for product in cart['products']:
                data = [product[2][0][0], order, product[3]]
                total_price += product[5]
                data_products.append(data)

        cursor.executemany("INSERT INTO orderitems (product_id, order_id, quantity) VALUES (?, ?, ?)", data_products)
        db.commit()

        cursor.execute("UPDATE orders SET (total_price) = (?) WHERE id = (?) ", (total_price, order,))
        db.commit()
        cart['products'] = []
        print(f'Заказ {order} успешно создан')
        db.close()
    else:
        print("Корзина пуста")

def create_product(name, category, subcategory, price):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()
    cursor.execute("INSERT INTO products (name, category, subcategory, price) VALUES (?,?,?,?)",
                    (name, category, subcategory, price)
                    )
    db.commit()
    print("Товар успешно создан")
    db.close()

def main_menu(cart, user):
    while True:
        print("1. Посмотреть каталог")
        print("2. Посмотреть корзину")
        print("3. Выйти из аккаунта")
        choice = input("Enter your choice: ")
        if choice == "1":
            catalog_menu(cart)
        elif choice == "2":
            cart_table = PrettyTable()
            cart_table.field_names = ["id", "Тип продукции", "Корзина", "Количество", "Цена за штуку", "Цена"]
            n = 1
            for types in cart:
                for product in cart[types]:
                    product[0] = n
                    cart_table.add_row(product)
                    n += 1
            print(cart_table)
            while True:
                print("1. Оформление заказа")
                print("2. Удаление позиции из корзины")
                print("3. Изменение количества товара")
                print("4. Выход из меню")
                choice = input("Введите ваш выбор: ")
                if choice == "1":
                    create_order(cart, user)
                if choice == "2":
                    choice = input("Какую позицию вы хотите удалить?: ")
                    try:
                        choice = int(choice)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    for types in cart:
                        for product in cart[types]:
                            if product[0] == choice:
                                cart[types].remove(product)
                                print("Удаление успешно")

                if choice == "3":
                    choice = input("Какую позицию вы хотите изменить?: ")
                    try:
                        choice = int(choice)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    for types in cart:
                        n = 0
                        for product in cart[types]:
                            if product[0] == choice:
                                quantity = int(input("Новое значеение количества: "))
                                cart[types][n][3] = quantity
                                cart[types][n][5] = quantity * cart[types][n][4]
                                print("Изменение прошло успешно")
                            n += 1

                if choice == "4":
                    break
        elif choice == "3":
            return None

def get_all_products_orm():
    products = session.query(Product).all()

    table = PrettyTable()
    table.field_names = ["ID", "Name", "Category", "Subcategory", "Price"]

    rows = []
    for product in products:
        rows.append([product.id, product.name, product.category, product.subcategory, product.price])

    table.add_rows(rows)

    print(table)


def add_product():
    name = input("Введите название продукции: ")
    category = input("Введите категорию продукции: ")
    subcategory = input("Введите подкатегорию продукции: ")
    while True:
        try:
            price = float(input("Введите цену продукции: "))
            break
        except ValueError:
            print("Ошибка: введите числовое значение для цены.")

    new_product = Product(name=name, category=category, subcategory=subcategory, price=price)
    session.add(new_product)
    session.commit()
    print(f"Добавлена новая продукция: {name}")


def delete_product():
    while True:
        try:
            product_id = int(input("Введите ID товара для удаления: "))

            if session.query(Product).filter_by(id=product_id).count() == 0:
                print("Ошибка: товар с указанным ID не существует.")
                continue
            break
        except ValueError:
            print("Ошибка: введите целочисленное значение для ID товара.")

    product = session.query(Product).filter_by(id=product_id).first()
    session.delete(product)
    session.commit()
    print(f"Товар с ID {product_id} удален")

def get_all_orders():
    try:
        orders = session.query(Order).all()
        if not orders:
            print("В базе данных нет заказов.")
            return

        table = PrettyTable()
        table.field_names = ["ID", "ПользовательID", "Дата заказа", "Общая сумма"]

        for order in orders:
            table.add_row([order.id, order.customer_id, order.order_date, order.total_price])

        print("Список заказов:")
        print(table)
    except Exception as e:
        print("Ошибка при получении списка заказов:", e)

def get_all_users():
    try:
        customers = session.query(Customers).all()
        if not customers:
            print("В базе данных нет пользователей.")
            return

        table = PrettyTable()
        table.field_names = ["ID", "Имя", "Логин", "Роль"]

        for user in customers:
            table.add_row([user.id, user.name, user.username, user.role.name])

        print("Список пользователей:")
        print(table)
    except Exception as e:
        print("Ошибка при получении списка пользователей:", e)

def admin_menu():
    while True:
        print("1. Продукция")
        print("2. Заказы")
        print("3. Пользователи")
        print("4. Выйти из аккаунта")
        choice = input("Enter your choice: ")

        if choice == "1":
            product_menu()
        
        if choice == "2":
            get_all_orders()

        if choice == "3":
            get_all_users()

        if choice == "4":
            return None  

def product_menu():
    while True:
        print("1. Получить список продукции")
        print("2. Добавить продукцию")
        print("3. Удалить продукцию")
        print("4. Назад")
        choice = input("Введите ваш выбор: ")

        if choice == "1":
            print(get_all_products_orm())
        elif choice == "2":
            add_product()
        elif choice == "3":
            delete_product()
        elif choice == "4":
            return None
        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")

def auth_menu():
    print("Welcome to the Console Authentication System")
    print("1. Login")
    print("2. Register")
    print("3. Exit")

    choice = input("Enter your choice: ")
    if choice == "1":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        user = auth(username, password)
        if user:
            return user
    elif choice == "2":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        name = input("Enter your name: ")
        role_id = 1
        user = register(username, password, name, role_id)
        if user:
            return user
    elif choice == "3":
        print("Exiting the program")
        raise SystemExit()

def catalog_menu(cart):
    while True:
        print("Catalog Menu")
        print("1. View all products")
        print("2. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            products = get_all_products()
            product_table = PrettyTable()
            product_table.field_names = ["ID", "Название",  "Категория", "Подкатегория", "Цена"]
            product_table.add_rows(products)
            print(product_table)
            while True:
                choice = input(
                    "Для добавления товара в корзину введите его ID, для выхода из меню нажмите b, для отображения списка продуктов нажмите p: ")
                if choice == "b":
                    return False
                elif choice == "p":
                    print(product_table)
                    continue
                try:
                    choice = int(choice)
                except ValueError:
                    print("Пожалуйста, введите правильное число.")
                    continue
                product = ["1", "Продукция", get_product(choice)]

                if product[2] is not None:
                    quantity = input("Введите количество товара: ")
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    product.append(quantity)
                    product.append(product[2][0][2])
                    product.append(product[2][0][2] * quantity)
                    cart['products'].append(product)
                    print(f'Продукция {product[2][0][1]} в количестве {quantity} успешно добавлена в корзину')
                else:
                    print("Продукции с таким ID не найдено")
        if choice == "2":
            return False
##
def get_all_products():
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT p.id, p.name, p.category, p.subcategory, p.price FROM products p"""
    cursor.execute(query)
    products = cursor.fetchall()

    db.close()

    return products
##
def get_product(id):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """
            SELECT p.id, p.name, p.category, p.subcategory, p.price FROM products p
            WHERE p.id == ?
            """
    cursor.execute(query, (id,))
    product = cursor.fetchall()

    db.close()

    if product:
        return product
    else:
        return None

def main():
    user_role_id = None
    user = None
    cart = {'products': []}
    while True:
        # Блок меню авторизации
        if user_role_id is None:
            user = auth_menu()
            if user:
                user_role_id = user[4]
                cart = {'products': []}
        # Блок основного меню
        if user_role_id == 1:
            user_role_id = main_menu(cart, user)
        elif user_role_id == 2:
            user_role_id = admin_menu()


if __name__ == "__main__":
    main()