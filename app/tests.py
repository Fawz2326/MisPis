import unittest
import sqlite3
from main import get_product

class TestGetProductFunction(unittest.TestCase):
    def test_get_product(self):
        product = get_product(6)
        self.assertEqual(product[0][1], "AK-103")  # Первый элемент кортежа содержит имя продукции
        self.assertEqual(product[0][2], 150000.0)  # Второй элемент кортежа содержит цену продукции
        self.assertEqual(product[0][3], "Weapon")  # Третий элемент кортежа содержит категорию продукции
        self.assertEqual(product[0][4], "AR")  # Четвертый элемент кортежа содержит  подкатегорию продукции

    def test_get_nonexistent_product(self):
        product = get_product(1000)
        expected = None
        self.assertEqual(product, None)

    def test_invalid_input(self):
        product = get_product("Текст, а не id")
        self.assertEqual(get_product(product), None)


if __name__ == '__main__':
    unittest.main()