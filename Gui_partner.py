from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
from Main_bd import BdApi
import sys
from Gui_win.products_table import Ui_Dialog_products_table
from Gui_win.Partner_win import Ui_Partner_win
from Gui_win.order_history import Ui_Dialog_order_history
from decimal import Decimal
from PyQt5.QtGui import QIntValidator




class Partner_win(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Partner_win()
        self.ui.setupUi(self)

        self.db = BdApi()

        self.load_product_types()
        self.load_company_names()

        self.ui.pushButton_exit_p.clicked.connect(self.open_aut_win)
        self.ui.lineEdit_total_amount.textChanged.connect(self.update_price_labels)
        self.ui.lineEdit_total_amount.setValidator(QIntValidator(0, 99999))
        self.ui.comboBox_show_products.currentIndexChanged.connect(self.load_product_names)
        self.ui.comboBox_select_product.currentIndexChanged.connect(self.show_product_price_with_discount)
        self.ui.comboBox_company_name.currentIndexChanged.connect(self.show_product_price_with_discount)
        self.ui.pushButton_products_table.clicked.connect(self.open_table)
        self.ui.pushButton_products_table_2.clicked.connect(self.open_order_history)
        self.ui.pushButton_form_order.clicked.connect(self.on_pushButton_form_order_clicked)


    def open_aut_win(self):
        from Gui import AutorizationWindow

        self.aut_win = AutorizationWindow()
        self.aut_win.show()
        self.close()



    def add_order(self, selected_partner_id, selected_partner_name, product_type, product_name, total_price,
                  total_amount):
        """Добавляет заказ в базу данных."""
        order_id = self.db.add_order(selected_partner_id, selected_partner_name, product_type, product_name,
                                     total_price, total_amount)
        if order_id:
            QtWidgets.QMessageBox.information(self, "Успех", f"Заказ добавлен успешно! ID: {order_id}")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить заказ.")

    def open_table(self):
        self.o_t = products_table_win()
        self.o_t.show()

    def open_order_history(self):
        self.o_o_h = order_history()
        self.o_o_h.show()

    def load_product_types(self):
        """Загружает типы продуктов в comboBox_show_products."""
        product_types = self.db.fetch_product_types()
        if product_types:
            self.ui.comboBox_show_products.clear()
            self.ui.comboBox_show_products.addItems(product_types)

    def load_product_names(self):
        """Загружает имена продуктов, соответствующие выбранному типу, в comboBox_select_product."""
        selected_type = self.ui.comboBox_show_products.currentText()
        product_names = self.db.fetch_product_names_by_type(selected_type)

        if product_names:
            self.ui.comboBox_select_product.clear()
            self.ui.comboBox_select_product.addItems(product_names)

    def show_product_price_with_discount(self):
        """Выводит цену продукта с учетом скидки для выбранного партнера в label_price_with_discount."""
        selected_name = self.ui.comboBox_select_product.currentText()
        selected_partner = self.ui.comboBox_company_name.currentText()

        # Получаем цену со скидкой
        discounted_price = self.db.fetch_discounted_price(selected_name, selected_partner)

        # Обновляем лейбл для отображения цены со скидкой
        self.update_price_labels(discounted_price)

    def update_price_labels(self, discounted_price):
        """Обновляет метки цены с учетом введенного количества товара."""
        total_amount_text = self.ui.lineEdit_total_amount.text()

        try:
            total_amount = int(total_amount_text) if total_amount_text else 0
        except ValueError:
            total_amount = 0

        # Расчет цены по количеству
        if discounted_price is not None and isinstance(discounted_price, (int, float, Decimal)):
            # Преобразуем discounted_price в float, если он Decimal
            if isinstance(discounted_price, Decimal):
                discounted_price = float(discounted_price)

            # Вычисляем итоговые цены
            total_price_with_discount = discounted_price * total_amount
            base_price = self.db.fetch_product_price(self.ui.comboBox_select_product.currentText())

            # Преобразуем base_price в float, если он Decimal
            if isinstance(base_price, Decimal):
                base_price = float(base_price)

            total_price_without_discount = base_price * total_amount if base_price else 0

            # Преобразуем к float, если значения строковые
            if isinstance(total_price_with_discount, str):
                total_price_with_discount = float(total_price_with_discount)
            if isinstance(total_price_without_discount, str):
                total_price_without_discount = float(total_price_without_discount)

            # Обновляем метки
            self.ui.label_price_with_discount.setText(f"{total_price_with_discount:.2f} руб.")
            self.ui.label_main_price.setText(f"{total_price_without_discount:.2f} руб.")
        else:
            self.ui.label_price_with_discount.setText("0.00 руб.")
            self.ui.label_main_price.setText("0.00 руб.")

    def load_company_names(self):
        """Загружает имена компаний в comboBox_company_name."""
        company_names = self.db.fetch_company_names()
        self.ui.comboBox_company_name.addItems(company_names)

    def on_pushButton_form_order_clicked(self):
        """Обрабатывает нажатие кнопки для формирования заказа."""
        selected_name = self.ui.comboBox_select_product.currentText()
        selected_partner = self.ui.comboBox_company_name.currentText()
        total_amount_text = self.ui.lineEdit_total_amount.text()
        total_amount = float(total_amount_text) if total_amount_text else 0

        print(f"Запрашиваем ID партнера: {selected_partner}")  # Отладочный вывод
        selected_partner_id = self.db.fetch_partner_id(selected_partner)  # Получаем ID партнера

        if selected_partner_id is None:
            self.show_message("Ошибка", "Партнер не найден.")
            return  # Прерываем выполнение, если партнер не найден

        # Получаем тип продукта и цену
        product_type = self.ui.comboBox_show_products.currentText()
        discounted_price = self.db.fetch_discounted_price(selected_name, selected_partner)

        # Если цена не найдена, выводим сообщение об ошибке
        if discounted_price is None:
            self.show_message("Ошибка", "Не удалось получить цену со скидкой.")
            return

        # Преобразуем discounted_price в float, если он Decimal
        if isinstance(discounted_price, Decimal):
            discounted_price = float(discounted_price)

        total_price = discounted_price * total_amount

        # Добавляем заказ в базу данных
        order_id = self.db.add_order(selected_partner_id, selected_partner, product_type, selected_name, total_price,
                                     total_amount)

        if order_id:
            self.show_message("Успех", f"Заказ оформлен. ID: {order_id}")
        else:
            self.show_message("Ошибка", "Не удалось оформить заказ.")


    def fetch_partner_id(self, partner_name):
        partner_name = partner_name.strip().lower()
        query = "SELECT id FROM Partners WHERE LOWER(partner_name) = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (partner_name,))
        result = cursor.fetchone()

    def show_message(self, title, message):
        """Отображает сообщение пользователю."""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()



class order_history(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_order_history()
        self.ui.setupUi(self)

        # Подключение к базе данных
        self.db = BdApi()

        # Загрузка партнеров в comboBox
        self.load_partners()

        # Подключение сигналов
        self.ui.comboBox_name_change.currentTextChanged.connect(self.on_partner_selected)
        self.ui.pushButton_cancel_order.clicked.connect(lambda: self.update_order_status("canceled"))
        self.ui.pushButton_buy.clicked.connect(lambda: self.update_order_status("paid"))

    def load_partners(self):
        """Загружает партнеров в comboBox_name_change."""
        partners = self.db.get_partners()
        self.ui.comboBox_name_change.clear()
        self.ui.comboBox_name_change.addItems(partners)

    def on_partner_selected(self):
        """Загружает заказы выбранного партнера и ID заказов в comboBox_change_order."""
        partner_name = self.ui.comboBox_name_change.currentText()
        if partner_name:
            self.load_orders(partner_name)
            self.load_order_ids(partner_name)

    def load_orders(self, partner_name):
        """Загружает и отображает заказы партнера в tableWidget_orders_output с динамическими столбцами."""
        # Получаем данные и названия столбцов из базы данных
        orders, column_names = self.db.get_orders_by_partner(partner_name)

        if not orders:
            print("Нет доступных заказов для данного партнера.")
            return

        # Очистка содержимого, но оставляем заголовки
        self.ui.tableWidget_orders_output.clearContents()

        # Устанавливаем количество столбцов и заголовки только один раз
        self.ui.tableWidget_orders_output.setColumnCount(len(column_names))
        self.ui.tableWidget_orders_output.setHorizontalHeaderLabels(column_names)

        # Устанавливаем количество строк
        self.ui.tableWidget_orders_output.setRowCount(len(orders))

        # Заполняем таблицу данными из базы данных
        for row_idx, order in enumerate(orders):
            for col_idx, value in enumerate(order):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.ui.tableWidget_orders_output.setItem(row_idx, col_idx, item)

    def load_order_ids(self, partner_name):
        """Загружает ID заказов партнера в comboBox_change_order."""
        order_ids = self.db.get_order_ids_by_partner(partner_name)
        self.ui.comboBox_change_order.clear()
        self.ui.comboBox_change_order.addItems([str(order_id) for order_id in order_ids])

    def update_order_status(self, status):
        """Обновляет статус выбранного заказа."""
        order_id_text = self.ui.comboBox_change_order.currentText()
        if order_id_text:
            order_id = int(order_id_text)
            success = self.db.update_order_status(order_id, status)
            if success:
                self.show_message("Успех", f"Статус заказа {order_id} обновлен на '{status}'")
                self.on_partner_selected()  # Обновляем список заказов после изменения
            else:
                self.show_message("Ошибка", "Не удалось обновить статус заказа.")

    def show_message(self, title, message):
        """Показывает сообщение пользователю."""
        QtWidgets.QMessageBox.information(self, title, message)







class products_table_win(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog_products_table()
        self.ui.setupUi(self)
        # Подключение к базе данных
        self.db = BdApi()

        # Заполняем comboBox_company_name именами компаний
        self.load_products_data()


    def load_products_data(self):
        """Вывод данных из таблицы products в виджет tableWidget_products_output."""
        products = self.db.fetch_products()

        if products:
            self.ui.tableWidget_products_output.setRowCount(len(products))
            self.ui.tableWidget_products_output.setColumnCount(len(products[0]))
            self.ui.tableWidget_products_output.setHorizontalHeaderLabels(products[0].keys())

            for row_idx, product in enumerate(products):
                for col_idx, (key, value) in enumerate(product.items()):
                    self.ui.tableWidget_products_output.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon("D:/Py_Projects/Py-main/task and images/Мастер пол.ico")
    app.setWindowIcon(icon)
    start_app = Partner_win()
    start_app.show()
    sys.exit(app.exec_())
