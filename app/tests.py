import unittest
import sqlite3
from main import get_product

class TestGetProductFunction(unittest.TestCase):
    def test_get_product(self):
        product = get_product(1)
        self.assertEqual(product[0][1], "AK47")  # Первый элемент кортежа содержит имя продукции
        self.assertEqual(product[0][2], "Weapon")  # Второй элемент кортежа содержит категорию продукции
        self.assertEqual(product[0][3], "AssaultRifle")  # Третий элемент кортежа содержит подкатегорию продукции
        self.assertEqual(product[0][4], 100000.0)  # Четвертый элемент кортежа содержит цену продукции

    def test_get_nonexistent_product(self):
        product = get_product(1000)
        expected = None
        self.assertEqual(product, None)

    def test_invalid_input(self):
        product = get_product("Текст, а не id")
        self.assertEqual(get_product(product), None)


if __name__ == '__main__':
    unittest.main()