import unittest
from Main_bd import BdApi  # Подключаем модуль для тестирования

class TestBdApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Устанавливаем соединение с базой данных перед тестами"""
        cls.db = BdApi()

    def test_connection(self):
        """Проверка успешного подключения к базе данных"""
        self.assertTrue(self.db.connection.open, "Соединение с базой данных не установлено")

    def test_get_product_types(self):
        """Проверка получения типов продукции"""
        product_types = self.db.get_product_types()
        self.assertGreater(len(product_types), 0, "Список типов продукции пуст")


    def test_get_material_types(self):
        """Проверка получения типов материалов"""
        material_types = self.db.get_material_types()
        self.assertGreater(len(material_types), 0, "Список типов материалов пуст")

    def test_calculate_material(self):
        """Проверка расчета материала"""
        try:
            result = self.db.calculate_material(product_id=1, material_id=2, product_quantity=10, param1=1.2, param2=1.5)
            self.assertGreater(result, 0, "Результат расчета должен быть положительным")
        except ValueError as e:
            self.fail(f"Ошибка при расчете материала: {e}")

    def test_fetch_data(self):
        """Проверка получения данных о партнерах"""
        partners = self.db.fetch_data()
        self.assertIsNotNone(partners, "Список партнеров пуст")


    def test_add_partner_to_db(self):
        """Проверка добавления нового партнера"""
        self.db.add_partner_to_db(
            parttype="Type",
            partname="Test Partner",
            directorname="Director",
            email="testss@example.com",
            telephone="1234567890",
            uradress="Address",
            inn="123456789",
            rating=5
        )
        partner_name = self.db.get_user_data("Test Partner", "partner_name")
        self.assertEqual(partner_name, "Test Partner", "Партнер не добавился в базу данных")



    def test_get_partner_names(self):
        """Проверка получения списка имен партнеров"""
        partners_names = self.db.get_partner_names()
        self.assertGreater(len(partners_names), 0, "Список имен партнеров пуст")

    @classmethod
    def tearDownClass(cls):
        """Закрываем соединение после всех тестов"""
        cls.db.connection.close()

    def test_update_partner_rating(self):
        """Проверка обновления рейтинга партнера"""
        try:
            self.db.update_partner_rating(partner_id=1, new_rating=11)
        except Exception as e:
            self.fail(f"Ошибка при обновлении рейтинга: {e}")


if __name__ == "__main__":
    unittest.main()
