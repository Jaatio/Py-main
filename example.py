import pymysql
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableWidgetItem

import sys
from Main_bd import BdApi
from Gui_win.Autorization_win import Ui_Autorization_win
from Gui_win.Registration_win import Ui_Registration_win
from Gui_win.Manager_win import Ui_Manager_win
from Gui_win.Partner_win import Ui_Partner_win
from Gui_win.add_partner import Ui_Add_partner_def
from Gui_win.Data_edit import Ui_Data_edit
from Gui_win.realisation_partner_products import Ui_Dialog_realistaio_products_table

class PartnerManager:
    def __init__(self, db_connection, ui):
        self.connection = db_connection
        self.ui = ui
        self.setup_ui()

    def setup_ui(self):
        # Установка иконки и логотипа
        self.ui.setWindowIcon(QIcon('path_to_icon.png'))
        self.ui.logo_label.setPixmap('path_to_logo.png')

        # Настройка таблицы партнёров
        self.ui.tableWidget_partners.setColumnCount(4)
        self.ui.tableWidget_partners.setHorizontalHeaderLabels(['ID', 'Название', 'Тип', 'Скидка'])

        # Загрузка данных
        self.load_partners_data()

    def load_partners_data(self):
        """Загружает список партнеров и выводит их в таблицу с учетом скидки"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                SELECT id, partner_name, partner_type, total_sales 
                FROM Partners
                """
                cursor.execute(query)
                partners = cursor.fetchall()

                self.ui.tableWidget_partners.setRowCount(len(partners))
                for row_idx, partner in enumerate(partners):
                    discount = self.calculate_discount(partner['total_sales'])
                    self.ui.tableWidget_partners.setItem(row_idx, 0, QTableWidgetItem(str(partner['id'])))
                    self.ui.tableWidget_partners.setItem(row_idx, 1, QTableWidgetItem(partner['partner_name']))
                    self.ui.tableWidget_partners.setItem(row_idx, 2, QTableWidgetItem(partner['partner_type']))
                    self.ui.tableWidget_partners.setItem(row_idx, 3, QTableWidgetItem(f"{discount}%"))
        except pymysql.MySQLError as e:
            print(f"Ошибка при загрузке данных: {e}")

    def calculate_discount(self, total_sales):
        """Вычисляет скидку на основе общего объема продаж"""
        if total_sales < 10000:
            return 0
        elif 10000 <= total_sales < 50000:
            return 5
        elif 50000 <= total_sales < 300000:
            return 10
        else:
            return 15

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon("C:/pWork/P4-question/task and images/Мастер пол.ico")  # Путь к файлу иконки
    app.setWindowIcon(icon)
    start_app = PartnerManager()
    start_app.show()
    sys.exit(app.exec_())
