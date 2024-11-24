import pymysql.cursors
import pymysql
import sys
from decimal import Decimal

class BdApi:

    def __init__(self):
        # Создание соединения с базой данных
        try:
            self.connection = pymysql.connect(host='localhost',
                                              user='root',
                                              password='',
                                              database='p4_question',
                                              cursorclass = pymysql.cursors.DictCursor)

            print("Соединение с базой данных установлено")
        except pymysql.MySQLError as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            sys.exit()

    def get_product_types(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, `Тип продукции` FROM product_type_import")
            return cursor.fetchall()

    def get_material_types(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, material_type, the_marriage_percentage FROM material_type_import")
            return cursor.fetchall()

    def calculate_material(self, product_id, material_id, product_quantity, param1, param2):
        # Получение коэффициентов из базы данных
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT `Коэффициент типа продукции` FROM product_type_import WHERE id = %s", (product_id,))
            product_coeff = float(cursor.fetchone()['Коэффициент типа продукции'].replace(',', '.'))

            cursor.execute("SELECT the_marriage_percentage FROM material_type_import WHERE id = %s", (material_id,))
            material_waste = float(cursor.fetchone()['the_marriage_percentage'].replace(',', '.'))

        # Проверка на положительные значения параметров
        if param1 <= 0 or param2 <= 0:
            raise ValueError("Параметры продукции должны быть положительными числами.")

        # Выполнение расчета
        base_material_needed = product_quantity * product_coeff * param1 * param2
        total_material_needed = base_material_needed * (1 + material_waste)

        return int(total_material_needed)

    def fetch_data(self):
        try:
            with self.connection.cursor() as cursor:
                # Выполнение SQL-запроса
                cursor.execute("SELECT * FROM p4_question.Partners;")
                results = cursor.fetchall()  # Получаем все данные
                return results
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def update_partner_rating(self, partner_id, new_rating):
        try:
            with self.connection.cursor() as cursor:
                # Замените 'partner_id' на реальное название столбца, содержащего идентификатор партнера
                sql = "UPDATE p4_question.partners SET rating = %s WHERE id = %s"
                cursor.execute(sql, (new_rating, partner_id))
                self.connection.commit()
                print(f"Рейтинг обновлен для партнера с ID {partner_id}")
        except pymysql.MySQLError as e:
            print(f"Ошибка при обновлении рейтинга: {e}")
            raise

    def combobox_fetch_data(self):
        try:
            with self.connection.cursor() as cursor:
                # Выполняем SQL-запрос для выборки имени и рейтинга
                cursor.execute("SELECT Partners, rating FROM p4_question.Partners;")
                results = cursor.fetchall()  # Получаем все данные
                return results
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None


    def authorization(self, login, password):
        try:
            with self.connection.cursor() as cursor:
                # Выполнение SQL-запроса для проверки логина и пароля
                sql_query = "SELECT role_log FROM user_info WHERE login=%s AND password=%s"
                cursor.execute(sql_query, (login, password))
                result = cursor.fetchone()  # fetchone вернёт результат в виде словаря

                if result:
                    return result['role_log']  # Можно безопасно обращаться через строковые индексы
                else:
                    return None
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    #поменять данные для добавления клиента
    def add_partner_to_db(self, parttype, partname, directorname, email, telephone, uradress, inn, rating):
        try:
            with self.connection.cursor() as cursor:
                # SQL-запрос для вставки данных о партнёре
                sql_query = """
                   INSERT INTO partners (partner_type, partner_name, director_name, email, partner_phone, ur_adress, inn, rating)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   """
                cursor.execute(sql_query, (parttype, partname, directorname, email, telephone, uradress, inn, rating))
                self.connection.commit()  # Подтверждение изменений
                print("Партнёр успешно добавлен в базу данных")
        except pymysql.MySQLError as e:
            print(f"Ошибка при добавлении партнёра: {e}")

    def fetch_usernames(self):
        try:
            with self.connection.cursor() as cursor:
                sql_query = "SELECT partner_name FROM p4_question.Partners"
                cursor.execute(sql_query)
                result = cursor.fetchall()

                return [row['partner_name'] for row in result]
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def get_user_data(self, username, field):
        try:
            with self.connection.cursor() as cursor:
                sql = f"SELECT {field} FROM Partners WHERE partner_name = %s"
                cursor.execute(sql, (username,))
                result = cursor.fetchone()
                if result:
                    return result[field]
        except pymysql.MySQLError as e:
            print(f"Ошибка при получении данных: {e}")
            return None

    def update_user_data(self, username, field, new_value):
        try:
            with self.connection.cursor() as cursor:
                # Защита от SQL-инъекций
                sql = f"UPDATE Partners SET {field} = %s WHERE partner_name = %s"
                cursor.execute(sql, (new_value, username))
                self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"Ошибка при обновлении данных: {e}")
            raise

    def get_table_columns(self, table_name="Partners"):
        """Возвращает список столбцов для указанной таблицы"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = cursor.fetchall()
                return [column["Field"] for column in columns if column["Field"] != "id"]
        except pymysql.MySQLError as e:
            print(f"Ошибка при получении столбцов таблицы {table_name}: {e}")
            return []

    def fetch_realisation_products_partners(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM p4_question.partners_products;")
                results = cursor.fetchall()
                return results
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_products(self):
        """Получает все данные из таблицы products."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                results = cursor.fetchall()
                return results
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_product_types(self):
        """Получает уникальные типы продуктов из таблицы products."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT product_type FROM products")
                results = cursor.fetchall()
                return [row['product_type'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_product_names_by_type(self, product_type):
        """Получает имена продуктов по их типу."""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT product_name FROM products WHERE product_type = %s"
                cursor.execute(sql, (product_type,))
                results = cursor.fetchall()
                return [row['product_name'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def get_partner_names(self):
        """Возвращает список имен всех партнеров."""
        query = "SELECT DISTINCT partner_name FROM Partners"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [row['partner_name'] for row in cursor.fetchall()]

    def fetch_product_price(self, product_name):
        """Получает цену продукта по его имени."""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT min_price FROM products WHERE product_name = %s"
                cursor.execute(sql, (product_name,))
                result = cursor.fetchone()
                if result:
                    return result['min_price']
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_company_names(self):
        try:
            with self.connection.cursor() as cursor:
                # Запрос для получения списка имен компаний
                cursor.execute("SELECT partner_name FROM Partners")
                results = cursor.fetchall()
                return [row['partner_name'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при получении имен компаний: {e}")
            return []

    def fetch_company_names(self):
        try:
            with self.connection.cursor() as cursor:
                # Запрос для получения списка имен компаний
                cursor.execute("SELECT partner_name FROM Partners")
                results = cursor.fetchall()
                return [row['partner_name'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при получении имен компаний: {e}")
            return []

    def fetch_product_price(self, product_name):
        """Возвращает цену продукта по имени."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT min_price FROM products WHERE product_name = %s", (product_name,))
            result = cursor.fetchone()
            return result['min_price'] if result else None

    def fetch_partner_discount(self, partner_name):
        """Вычисляет скидку для партнера на основе количества реализованной продукции."""
        with self.connection.cursor() as cursor:
            # Получаем общее количество продукции для указанного партнера
            cursor.execute(
                "SELECT SUM(product_quantity) AS total_quantity FROM Partners_products WHERE partner_name = %s",
                (partner_name,))
            result = cursor.fetchone()

            # Если данных нет, устанавливаем total_quantity в 0
            total_quantity = result['total_quantity'] if result['total_quantity'] is not None else 0

            # Определяем скидку на основе общего количества
            if total_quantity > 300000:
                return 0.15  # 15% скидка
            elif total_quantity > 50000:
                return 0.10  # 10% скидка
            elif total_quantity > 10000:
                return 0.05  # 5% скидка
            else:
                return 0.0  # Без скидки


    def fetch_discounted_price(self, product_name, partner_name):
        """Возвращает цену продукта с учетом скидки для партнера."""
        base_price = self.fetch_product_price(product_name)
        discount = self.fetch_partner_discount(partner_name)

        # Отладка: Выводим базовую цену и скидку
        print(f"Base price: {base_price}, Discount: {discount}")

        # Если скидки нет или базовая цена не найдена, возвращаем None для корректного отображения
        if base_price is None:
            return None

        # Преобразуем discount в Decimal, если он float
        if isinstance(discount, float):
            discount = Decimal(discount)

        discounted_price = base_price * (1 - discount)
        print(f"Discounted price: {discounted_price}")  # Отладка: Проверяем расчет цены со скидкой
        return discounted_price if discount > 0 else base_price

    def fetch_data(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM p4_question.Partners;")
                results = cursor.fetchall()  # Получаем все данные
                return results
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def add_order(self, partner_id, partner_name, product_type, product_name, total_price, total_amount):
        """Добавляет заказ в базу данных."""
        query = """
            INSERT INTO Orders (partner_id, partner_name, product_type, product_name, total_price, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'created')
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (partner_id, partner_name, product_type, product_name, total_price, total_amount))
            self.connection.commit()
            return cursor.lastrowid  # Возвращаем ID последнего добавленного заказа
        except Exception as e:
            print(f"Ошибка при добавлении заказа: {str(e)}")
            return None

    """    def close(self):
        self.cursor.close()
        self.connection.close()"""

    def fetch_product_types(self):
        """Получает уникальные типы продуктов из таблицы products."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT product_type FROM products")
                results = cursor.fetchall()
                return [row['product_type'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_product_names_by_type(self, product_type):
        """Получает имена продуктов по их типу."""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT product_name FROM products WHERE product_type = %s"
                cursor.execute(sql, (product_type,))
                results = cursor.fetchall()
                return [row['product_name'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_product_price(self, product_name):
        """Получает цену продукта по его имени."""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT min_price FROM products WHERE product_name = %s"
                cursor.execute(sql, (product_name,))
                result = cursor.fetchone()
                if result:
                    return result['min_price']
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def fetch_company_names(self):
        """Получает имена компаний из таблицы Partners."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT partner_name FROM Partners")
                results = cursor.fetchall()
                return [row['partner_name'] for row in results]
        except pymysql.MySQLError as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None


    def create_order(self, product_id, quantity):
        """Создает заказ для определенного продукта."""
        query = "INSERT INTO orders (product_id, quantity) VALUES (%s, %s)"  # Запрос с двумя местозаполнителями
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (product_id, quantity))  # Передаем оба аргумента
                self.connection.commit()
                print("Заказ успешно создан.")
        except pymysql.MySQLError as e:
            print(f"Ошибка при создании заказа: {e}")

    def fetch_partner_id(self, partner_name):
        """Возвращает ID партнера по его имени."""
        partner_name = partner_name.strip().lower()

        query = "SELECT id FROM Partners WHERE LOWER(partner_name) = %s"
        cursor = self.connection.cursor()

        print(f"Выполняется запрос: {query} с параметром: '{partner_name}'")
        cursor.execute(query, (partner_name,))

        # Получаем первую строку результата
        result = cursor.fetchone()

        print(f"Результат запроса: {result}")

        if result is None:
            print(f"Партнер с именем '{partner_name}' не найден.")
            return None

            # Используем доступ по ключу для словаря
        try:
            return result['id']  # Возвращаем ID партнера
        except KeyError:
            print(f"Ошибка: результат не содержит ожидаемого ключа 'id'. Результат: {result}")
            return None


#_-------
    def get_partners(self):
        """Возвращает список имен партнеров."""
        query = "SELECT DISTINCT partner_name FROM Orders"
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = [row['partner_name'] for row in cursor.fetchall()]
        return result

    def get_orders_by_partner(self, partner_name):
        """Возвращает заказы партнера и названия столбцов."""
        query = """
            SELECT id, partner_id, partner_name, product_type, product_name,
                   total_price, total_amount, order_date, status
            FROM Orders
            WHERE partner_name = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (partner_name,))

        # Получаем данные и названия столбцов
        data = cursor.fetchall()

        # Проверка на наличие данных
        if not data:
            print(f"Нет заказов для партнера: {partner_name}")  # Отладка: выводим сообщение, если нет данных
        else:
            print(f"Найдено заказов для партнера {partner_name}: {len(data)}")  # Отладка: выводим количество заказов

        column_names = [desc[0] for desc in cursor.description]
        print("Названия столбцов:", column_names)  # Отладка: выводим названия столбцов

        # Возвращаем данные как список списков для совместимости с QTableWidget
        return [list(row) for row in data], column_names

    def get_order_ids_by_partner(self, partner_name):
        """Возвращает ID заказов для выбранного партнера."""
        query = "SELECT id FROM Orders WHERE partner_name = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (partner_name,))
        return [row['id'] for row in cursor.fetchall()]

    def update_order_status(self, order_id, status):
        """Обновляет статус заказа по его ID."""
        query = "UPDATE Orders SET status = %s WHERE id = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (status, order_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении статуса заказа: {str(e)}")
            return False



    def get_order_by_id(self, order_id):
        """Получает детали заказа по его ID."""
        query = """
            SELECT id, partner_id, partner_name, product_type, product_name, total_price, total_amount, order_date, status 
            FROM Orders WHERE id = %s
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (order_id,))
                order = cursor.fetchone()  # Получаем одну запись (детали заказа)
                return order
        except Exception as e:
            print(f"Ошибка при получении заказа с ID {order_id}: {e}")
            return None

    def check_login_unique(self, login):
        """Проверяет уникальность логина в базе данных."""
        query = "SELECT COUNT(*) AS count FROM user_info WHERE login = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (login,))
        result = cursor.fetchone()  # fetchone() возвращает словарь, если используется DictCursor

        # Проверяем, что результат существует и количество пользователей с таким логином равно 0
        if result and result.get('count', 0) == 0:
            return True  # Логин уникален
        return False  # Логин уже существует

    def register_new_user(self, role, login, password):
        """Регистрирует нового пользователя в базе данных."""
        try:
            query = """
                INSERT INTO user_info (role_log, login, password)
                VALUES (%s, %s, %s)
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (role, login, password))
            self.connection.commit()
            return True
        except pymysql.MySQLError as e:
            print(f"Ошибка при регистрации пользователя: {e}")
            return False

    def get_all_orders(self):
        """Возвращает все заказы из таблицы Orders и названия столбцов."""
        query = """
            SELECT id, partner_id, partner_name, product_type, product_name,
                   total_price, total_amount, order_date, status
            FROM Orders
        """
        cursor = self.connection.cursor()
        cursor.execute(query)

        # Получаем данные и названия столбцов
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        return [list(row) for row in data], column_names
DB = BdApi()
