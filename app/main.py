import sqlite3
import bcrypt
from prettytable import PrettyTable

database_path = 'db/database.db'

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

def main_menu(cart):
    while True:
        print("1. Посмотреть каталог")
        print("2. Посмотреть корзину")
        print("3. Оформить заказ")
        print("4. Выйти из аккаунта")
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

        elif choice == "4":
            return None

def admin_menu():
    pass    


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
            return user[4]
    elif choice == "2":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        name = input("Enter your name: ")
        role_id = 1
        user = register(username, password, name, role_id)
        if user:
            return user[4]
    elif choice == "3":
        print("Exiting the program")
        raise SystemExit(1)

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

                if product:
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

def get_all_products():
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT p.id, p.name, p.category, p.subcategory, p.price FROM products p"""
    cursor.execute(query)
    products = cursor.fetchall()

    db.close()

    return products

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

    return product

def main():
    user_role_id = None
    cart = {'products': []}
    while True:
        # Блок меню авторизации
        if user_role_id is None:
            user_role_id = auth_menu()
            cart = {'products': []}
        # Блок основного меню
        if user_role_id == 1:
            user_role_id = main_menu(cart)
        elif user_role_id == 2:
            user_role_id = admin_menu()


if __name__ == "__main__":
    main()