import unittest
from PyQt5.QtWidgets import QApplication
from Main_bd import BdApi
from Gui import AutorizationWindow, Manager_Win, order_history

app = QApplication([])  # Для инициализации GUI, необходимой для тестов

class TestGuiAndDatabaseIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Настраивает тестовую среду перед выполнением тестов."""
        cls.db = BdApi()  # Подключение к базе данных
        cls.gui_autorization = AutorizationWindow()  # Окно авторизации
        cls.gui_manager = Manager_Win()  # Окно менеджера
        cls.gui_order_history = order_history()  # Окно истории заказов

    def test_authorization_flow(self):
        """Проверяет процесс авторизации."""
        self.gui_autorization.ui.lineEdit_login.setText("asd")
        self.gui_autorization.ui.lineEdit_password.setText("123")

        # Проверка авторизации
        self.gui_autorization.autor_in()
        role = self.db.authorization("asd", "123")
        self.assertEqual(role, "Менеджер", "Ошибка авторизации или несоответствие роли")

    def test_add_partner(self):
        """Проверяет добавление партнера из GUI."""
        self.gui_manager.open_add_client_win()
        self.gui_manager.a_p.ui.lineEdit_partnertype.setText("ООО")
        self.gui_manager.a_p.ui.lineEdit_partname.setText("Test Partner")
        self.gui_manager.a_p.ui.lineEdit_dname.setText("Director Name")
        self.gui_manager.a_p.ui.lineEdit_email.setText("testdfsd@example.com")
        self.gui_manager.a_p.ui.lineEdit_telep.setText("1234567890")
        self.gui_manager.a_p.ui.lineEdit_uradd.setText("Test Address")
        self.gui_manager.a_p.ui.lineEdit_inn.setText("123456789012")
        self.gui_manager.a_p.ui.lineEdit_rating.setText("50")

        self.gui_manager.a_p.part_reg()

        partner_names = self.db.get_partner_names()
        self.assertIn("Test Partner", partner_names, "Партнер не добавился в базу данных")

    def test_calculate_material(self):
        """Проверяет расчет количества материала через GUI."""
        self.gui_manager.open_calculate_products_Win()
        self.gui_manager.cal_win.ui.comboBox_products_type.setCurrentIndex(0)
        self.gui_manager.cal_win.ui.comboBox_material_type.setCurrentIndex(0)
        self.gui_manager.cal_win.ui.lineEdit_products.setText("10")

        try:
            self.gui_manager.cal_win.calculate_material_needed()
            self.assertTrue(True, "Расчет выполнен успешно")
        except Exception as e:
            self.fail(f"Ошибка при расчете материалов: {e}")


    @classmethod
    def tearDownClass(cls):
        """Закрывает окна и соединение после выполнения тестов."""
        cls.db.connection.close()
        app.quit()

if __name__ == "__main__":
    unittest.main()
