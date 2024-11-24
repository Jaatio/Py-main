import unittest
from unittest.mock import MagicMock, patch
from Main_bd import BdApi  # Импортируем класс из файла


class TestBdApi(unittest.TestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем объект класса и мокаем соединение с базой
        self.db = BdApi()
        self.db.connection = MagicMock()

    def test_calculate_material(self):
        """Тест метода calculate_material"""
        # Настраиваем моки для SQL-запросов
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {'Коэффициент типа продукции': '1.5'},
            {'the_marriage_percentage': '0.1'}
        ]
        self.db.connection.cursor.return_value.__enter__.return_value = mock_cursor

        # Выполняем тест
        result = self.db.calculate_material(1, 2, 100, 2, 3)
        self.assertEqual(result, 990)  # Проверяем ожидаемый результат
        self.assertEqual(mock_cursor.execute.call_count, 2)

if __name__ == "__main__":
    unittest.main()
