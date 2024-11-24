from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableWidgetItem
import re
from PyQt5.QtWidgets import QMessageBox, QMainWindow

import sys
from Gui_win import Orders_edit
from Gui_win.Orders_edit import Ui_Dialo_edit_orders
from Main_bd import BdApi
from Gui_win.Autorization_win import Ui_Autorization_win
from Gui_win.Registration_win import Ui_Registration_win
from Gui_win.Manager_win import Ui_Manager_win
from Gui_win.Partner_win import Ui_Partner_win
from Gui_win.add_partner import Ui_Add_partner_def
from Gui_win.Data_edit import Ui_Data_edit
from Gui_partner import Partner_win
from Gui_win.realisation_partner_products import Ui_Dialog_realistaio_products_table
from Gui_win.Products_type_method import Ui_Dialog_products_method



class AutorizationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Autorization_win()
        self.ui.setupUi(self)

        self.DB = BdApi()
        self.ui.comboBox_role.addItem("Менеджер")
        self.ui.comboBox_role.addItem("Партнер ")


        self.ui.pushButton_autoriz.clicked.connect(self.autor_in)
        self.ui.commandLinkButton.clicked.connect(self.open_registration_window)

    def open_registration_window(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()
        self.close()

    def autor_in(self):
        _login = self.ui.lineEdit_login.text().strip()
        _password = self.ui.lineEdit_password.text().strip()

        try:
            role = self.DB.authorization(_login, _password)

            if role:
                print(f"Авторизация прошла успешно. Роль: {role}")
                # Открытие главного окна в зависимости от роли
                if role == 'Менеджер':
                    self.main_win_manager = Manager_Win()
                    self.main_win_manager.show()
                elif role == 'Партнер':
                    self.main_win_employee = Partner_win()
                    self.main_win_employee.show()
                self.close()  # Закрываем окно авторизации
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

        except Exception as e:
            # Обработка исключений
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")



    def open_employee_window(self):
        self.autorization_window = AutorizationWindow()
        self.autorization_window.show()
        self.close()


class order_history(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialo_edit_orders()
        self.ui.setupUi(self)

        # Подключение к базе данных
        self.db = BdApi()

        # Загрузка имен партнеров
        self.load_partner_names()

        # Настройка сигналов
        self.ui.comboBox_change_name_partner.currentTextChanged.connect(self.load_partner_orders)
        self.ui.comboBox_change_order_partner.currentTextChanged.connect(self.load_order_details)

        self.ui.pushButton_confirm_order.clicked.connect(lambda: self.update_order_status("in_production"))
        self.ui.pushButton_canceled_order.clicked.connect(lambda: self.update_order_status("canceled"))
        self.ui.pushButton_in_process.clicked.connect(lambda: self.update_order_status("in_production"))
        self.ui.pushButton_order_created.clicked.connect(lambda: self.update_order_status("created"))

    def load_partner_names(self):
        """Загружает имена партнеров в comboBox_change_name_partner."""
        partner_names = self.db.get_partner_names()
        self.ui.comboBox_change_name_partner.clear()
        if partner_names:
            self.ui.comboBox_change_name_partner.addItems(partner_names)
        else:
            print("Нет доступных партнеров.")  # Отладка

    def load_partner_orders(self):
        """Загружает и отображает заказы партнера в tableWidget и обновляет список comboBox_change_order_partner."""
        partner_name = self.ui.comboBox_change_name_partner.currentText()

        # Получаем заказы партнера и названия столбцов
        orders, column_names = self.db.get_orders_by_partner(partner_name)

        # Устанавливаем заголовки столбцов
        self.set_table_headers(column_names)

        # Заполняем таблицу данными
        self.fill_table_data(orders)

        if orders:
            order_ids = [str(order[0]) for order in orders]
            self.ui.comboBox_change_order_partner.clear()
            self.ui.comboBox_change_order_partner.addItems(order_ids)
        else:
            print(f"Нет заказов для партнера: {partner_name}")  # Отладка

    def set_table_headers(self, column_names):
        """Устанавливает заголовки столбцов в tableWidget."""
        self.ui.tableWidget_orders_output.setColumnCount(len(column_names))
        self.ui.tableWidget_orders_output.setHorizontalHeaderLabels(column_names)

    def fill_table_data(self, data):
        """Заполняет tableWidget данными."""
        print("Полученные данные:", data)
        self.ui.tableWidget_orders_output.setRowCount(0)

        if not data:
            print("Нет данных для заполнения таблицы.")
            return

        # Установка количества столбцов
        self.ui.tableWidget_orders_output.setColumnCount(
            len(data[0]))  # Установите количество столбцов в зависимости от первого ряда данных

        for row_index, row_data in enumerate(data):
            self.ui.tableWidget_orders_output.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.ui.tableWidget_orders_output.setItem(row_index, col_index, item)

    def load_order_details(self):
        """Загружает детали выбранного заказа (если это необходимо)."""
        order_id = self.ui.comboBox_change_order_partner.currentText()
        if order_id:
            order = self.db.get_order_by_id(order_id)

    def update_order_status(self, new_status):
        """Обновляет статус выбранного заказа."""
        order_id = self.ui.comboBox_change_order_partner.currentText()

        if order_id:
            success = self.db.update_order_status(order_id, new_status)
            if success:
                self.load_partner_orders()
            else:
                print(f"Не удалось обновить статус заказа с ID {order_id}.")

class RegistrationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Registration_win()
        self.ui.setupUi(self)

        self.db = BdApi()

        self.ui.commandLinkButton.clicked.connect(self.open_registration_window)
        self.ui.pushButton_registration.clicked.connect(self.register_user)

        self.load_user_roles()

    def load_user_roles(self):
        """Загружает роли пользователей в comboBox_registr."""
        roles = ["Менеджер", "Партнер"]  # Роли, которые должны быть в системе
        self.ui.comboBox_registr.addItems(roles)  # Заполнение comboBox ролями

    def open_registration_window(self):
        """Открытие окна авторизации."""
        self.autorization_window = AutorizationWindow()
        self.autorization_window.show()
        self.close()

    def register_user(self):
        """Регистрирует нового пользователя в системе."""
        role = self.ui.comboBox_registr.currentText()
        login = self.ui.lineEdit_login_registr.text().strip()
        password = self.ui.lineEdit_password_regist.text().strip()
        repeat_password = self.ui.lineEdit_repit_pass_auto.text().strip()

        # Проверка заполнения всех полей
        if not role or not login or not password or not repeat_password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        # Проверка уникальности логина
        if not self.is_unique_login(login):
            QMessageBox.warning(self, "Ошибка", "Логин уже занят. Выберите другой.")
            return

        # Проверка совпадения паролей
        if password != repeat_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают. Попробуйте снова.")
            return

        # Сохранение пользователя в базе данных
        if self.db.register_new_user(role, login, password):
            QMessageBox.information(self, "Успешно", "Регистрация прошла успешно.")
            self.open_registration_window()  # Открытие окна авторизации после успешной регистрации
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось зарегистрироваться. Повторите попытку.")

    def is_unique_login(self, login):
        """Проверяет уникальность логина в базе данных."""
        return self.db.check_login_unique(login)  # Метод API для проверки уникальности логина




class Manager_Win(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Manager_win()
        self.ui.setupUi(self)
        self.DB = BdApi()


        self.load_data()
        self.ui.pushButton_calculate_m.clicked.connect(self.open_calculate_products_Win)

        self.ui.pushButton_exit_m.clicked.connect(self.open_aut_win)
        self.ui.pushButton_edit_orders.clicked.connect(self.open_edit_orders)
        self.ui.pushButton_partners_products_realization.clicked.connect(self.open_table_product_realisation)
        self.ui.pushButton_partner_regist.clicked.connect(self.open_add_client_win)
        self.ui.pushButton_edit_data.clicked.connect(self.open_edit_data)

    def open_calculate_products_Win(self):
        self.cal_win = Calculate_products_method()
        self.cal_win.show()


    def open_aut_win(self):
        self.aut_win = AutorizationWindow()
        self.aut_win.show()
        self.close()

    def open_edit_orders(self):
        self.o_e_o = order_history()
        self.o_e_o.show()

    def load_data(self):
        all_users = self.DB.fetch_data()

        if all_users:
            self.update_table(all_users)
        else:
            print("Нет данных для отображения.")

    def update_table(self, data):
            model = QStandardItemModel()
            headers = list(data[0].keys()) if data else []
            model.setHorizontalHeaderLabels(headers)

            for row in data:
                items = [QStandardItem(str(value)) for value in row.values()]
                model.appendRow(items)

            self.ui.tableView_partners_list.setModel(model)

    def open_add_client_win(self):
        self.a_p = Add_partner()
        self.a_p.show()


    def open_edit_data(self):
        self.e_r = Edit_data()
        self.e_r.show()

    def open_table_product_realisation(self):
        self.p_e_r = partner_product_import()
        self.p_e_r.show()


class Calculate_products_method(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_products_method()
        self.ui.setupUi(self)
        self.db = BdApi()

        # Загрузка данных в combobox при инициализации
        self.load_comboboxes()

        # Связывание действий с виджетами
        self.ui.comboBox_material_type.currentIndexChanged.connect(self.update_marriage_percentage)
        self.ui.pushButton_calculation.clicked.connect(self.calculate_material_needed)

    def load_comboboxes(self):
        # Загрузка типов продукции
        products = self.db.get_product_types()
        for product in products:
            self.ui.comboBox_products_type.addItem(product['Тип продукции'], product['id'])

        # Загрузка типов материалов
        materials = self.db.get_material_types()
        for material in materials:
            self.ui.comboBox_material_type.addItem(material['material_type'], material['id'])

    def update_marriage_percentage(self):
        # Отображение процента брака для выбранного типа материала
        material_id = self.ui.comboBox_material_type.currentData()
        materials = self.db.get_material_types()
        for material in materials:
            if material['id'] == material_id:
                self.ui.label_the_marriage_percentage.setText(str(material['the_marriage_percentage']))
                break

    def calculate_material_needed(self):
        try:
            product_id = self.ui.comboBox_products_type.currentData()
            material_id = self.ui.comboBox_material_type.currentData()
            product_quantity = int(self.ui.lineEdit_products.text())

            # Проверка корректности ввода
            if product_quantity <= 0:
                raise ValueError("Количество продукции должно быть положительным числом.")

            # Параметры продукции для расчета (например, 1.5 и 2.0, они могут быть введены пользователем)
            param1, param2 = 1.5, 2.0

            # Получение расчета из API
            material_needed = self.db.calculate_material(product_id, material_id, product_quantity, param1, param2)
            QMessageBox.information(self, "Результат расчета", f"Необходимое количество материала: {material_needed}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {e}")








class Edit_data(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Data_edit()
        self.ui.setupUi(self)
        self.DB = BdApi()

        # Загрузка имен пользователей в comboBox
        self.load_usernames()

        # Подключение сигналов к слотам
        self.ui.comboBox_user_name_for_de.currentIndexChanged.connect(self.on_username_selected)
        self.ui.comboBox_user_data_change.currentIndexChanged.connect(self.on_data_field_selected)
        self.ui.pushButton_save_data_edit.clicked.connect(self.save_data_edit)


    def load_usernames(self):
        usernames = self.DB.fetch_usernames()
        if usernames:
            self.ui.comboBox_user_name_for_de.addItems(usernames)

    def on_username_selected(self):
        # Загружаем столбцы через метод из BdApi
        fields = self.DB.get_table_columns()
        self.ui.comboBox_user_data_change.clear()
        self.ui.comboBox_user_data_change.addItems(fields)

    def on_data_field_selected(self):
        # Получаем имя пользователя и выбранное поле
        selected_username = self.ui.comboBox_user_name_for_de.currentText()
        selected_field = self.ui.comboBox_user_data_change.currentText()

        if selected_username and selected_field:
            # Извлекаем текущее значение из базы данных
            current_value = self.DB.get_user_data(selected_username, selected_field)
            if current_value is not None:
                self.ui.lineEdit_user_data_Edit.setText(str(current_value))

    def save_data_edit(self):
        # Получаем текущие значения
        selected_username = self.ui.comboBox_user_name_for_de.currentText()
        selected_field = self.ui.comboBox_user_data_change.currentText()
        new_value = self.ui.lineEdit_user_data_Edit.text().strip()

        if selected_username and selected_field and new_value:
            try:
                self.DB.update_user_data(selected_username, selected_field, new_value)
                QtWidgets.QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось обновить данные: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите все поля и введите новое значение.")

    def load_usernames(self):
        usernames = self.DB.fetch_usernames()

        for username in usernames:
            self.ui.comboBox_user_name_for_de.addItem(username)

class partner_product_import(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_realistaio_products_table()
        self.ui.setupUi(self)
        self.DB = BdApi()
        self.load_realisation_data()

    def load_realisation_data(self):
        """Загружает и отображает данные о реализации продукции в tableView."""
        # Получаем данные из базы
        data = self.DB.fetch_realisation_products_partners()

        if data is None:
            print("Не удалось загрузить данные.")
            return

        # Создание модели для tableView
        model = QStandardItemModel()

        # Установка заголовков
        if data:
            column_names = data[0].keys()  # Получение имен столбцов
            model.setColumnCount(len(column_names))
            model.setHorizontalHeaderLabels(column_names)

            # Заполнение модели данными
            for row_data in data:
                row_items = [QStandardItem(str(value)) for value in row_data.values()]
                model.appendRow(row_items)

        # Устанавливаем модель для tableView
        self.ui.tableView_realisation_product_view.setModel(model)




class Add_partner(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Add_partner_def()
        self.ui.setupUi(self)
        self.ui.pushButton_add_partner.clicked.connect(self.part_reg)
        self.DB = BdApi()
        #self.ui.lineEdit_telep.setInputMask("+7(000)000-00-00")

    # Регистрация партнера
    def part_reg(self):
        # Считываем данные с полей ввода и убираем пробелы в начале и в конце
        parttype = self.ui.lineEdit_partnertype.text().strip()
        partname = self.ui.lineEdit_partname.text().strip()
        directorname = self.ui.lineEdit_dname.text().strip()
        email = self.ui.lineEdit_email.text().strip()
        telephone = self.ui.lineEdit_telep.text().strip()
        uradress = self.ui.lineEdit_uradd.text().strip()
        inn = self.ui.lineEdit_inn.text().strip()
        rating = self.ui.lineEdit_rating.text().strip()

        # Проверка корректности данных
        if parttype not in ['ЗАО', 'ООО', 'ПАО', 'ОАО']:
            self.show_message("Ошибка", "Некорректный тип партнёра. Допустимые значения: ЗАО, ООО, ПАО, ОАО.")
            return

        if not partname:
            self.show_message("Ошибка", "Название партнёра не может быть пустым.")
            return

        if not directorname:
            self.show_message("Ошибка", "Имя директора не может быть пустым.")
            return

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            self.show_message("Ошибка", "Некорректный формат email.")
            return

        if not re.match(r"^\d{10}$", telephone):
            self.show_message("Ошибка", "Номер телефона должен содержать 10 цифр.")
            return

        if not uradress:
            self.show_message("Ошибка", "Юридический адрес не может быть пустым.")
            return

        if not re.match(r"^\d{12}$", inn):
            self.show_message("Ошибка", "ИНН должен содержать 12 цифр.")
            return

        if not rating.isdigit() or not (0 <= int(rating) <= 100):
            self.show_message("Ошибка", "Рейтинг должен быть целым числом от 0 до 100.")
            return

        # Если все проверки пройдены, добавляем партнёра в базу данных
        self.DB.add_partner_to_db(parttype, partname, directorname, email, telephone, uradress, inn, int(rating))

    def show_message(self, title, message):
        """Показывает всплывающее сообщение об ошибке."""
        QtWidgets.QMessageBox.warning(self, title, message)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon("D:/Py_Projects/Py-main/task and images/Мастер пол.ico")  # Путь к файлу иконки
    app.setWindowIcon(icon)
    start_app = AutorizationWindow()
    start_app.show()
    sys.exit(app.exec_())

