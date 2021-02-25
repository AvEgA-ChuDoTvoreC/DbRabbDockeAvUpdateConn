import sqlite3
from pprint import pprint
import re
import os
from time import time

from MY_SCRIPTS.decorators import my_timer


class SQLite:
    def __init__(self, database_name: str):
        self.db_name = database_name
        self.cursor = None


    def create_connection(self):
        """Function create connection to database

        :return: connection
        """
        connection = sqlite3.connect(self.db_name)
        return connection, self.db_name


    def write_data_to_db(self, connection, query, data, verbose=False):
        """
        Функция ожидает аргументы:
            * connection - соединение с БД
            * query - запрос, который нужно выполнить
            * data - данные, которые надо передать в виде списка кортежей
        Функция пытается записать все данные из списка data.

        Если данные удалось записать успешно, изменения сохраняются в БД
            :return: True.
        Если в процессе записи возникла ошибка, транзакция откатывается
            :return: False.
        """
        for row in data:
            try:
                with connection:
                    connection.execute(query, row)
            except sqlite3.IntegrityError as e:
                if verbose:
                    print("При записи данных '{}' возникла ошибка".format(
                        ', '.join(row), e))
            else:
                if verbose:
                    print("Запись данных '{}' прошла успешно".format(', '.join(row)))
        # try:
        #     with connection:
        #         connection.executemany(query, data)
        # except sqlite3.IntegrityError as e:
        #     print('Error occurred: ', e)
        #     return False
        # else:
        #     print('Запись данных прошла успешно')
        #     return True


    def get_all_from_db(self, connection, query):
        """
        Функция ожидает аргументы:
            * connection - соединение с БД
            * query - запрос, который нужно выполнить

        :return: данные полученные из БД.
        """

        result = [row for row in connection.execute(query)]
        return result


    def create_table(self, table_name: str, template_name: str):
        pass

    def insert_data(self, data):
        self.data = data


if __name__ == "__main__":
    sql_db = SQLite("sw_inventory3.db")
    conn, dbname = sql_db.create_connection()

    print("Создание таблицы...")
    with open("dbtemplates/templates/dhcp_snooping_schema.sql", "r") as f:
        schema = f.read()
        schema_name = os.path.basename("dbtemplates/templates/dhcp_snooping_schema.sql")
        conn.execute(schema)

    print(f"Таблица создана по схеме: {schema_name}")

    query_insert = 'INSERT into dhcp values (?, ?, ?, ?)'
    query_get_all = 'SELECT * from dhcp'

    regex = re.compile('(\S+) +(\S+) +\d+ +\S+ +(\d+) +(\S+)')
    result = []
    with open("dhcp_snooping.txt", "r") as data:
        for line in data:
            match = regex.search(line)
            if match:
                result.append(match.groups())

    print(f"Запись данных в БД: {dbname}")

    start_time = time()  # 1
    sql_db.write_data_to_db(conn, query_insert, data=result)
    end_time = time()  # 2
    run_time = end_time - start_time  # 3
    print(f"Finished ql_db.write_data_to_db() in {run_time:.4f} sec")

    print(f"\nПроверка содержимого БД: {dbname}")
    pprint(sql_db.get_all_from_db(conn, query_get_all))

    conn.close()

# connection = sqlite3.connect('sw_inventory.db')
# cursor = connection.cursor()
#
# cursor.execute("create table switch (mac text not NULL primary key, hostname text, model text, location text)")
#
# data = [
#     ('0000.AAAA.CCCC', 'sw1', 'Cisco 3750', 'London, Green Str'),
#     ('0000.BBBB.CCCC', 'sw2', 'Cisco 3780', 'London, Green Str'),
#     ('0000.AAAA.DDDD', 'sw3', 'Cisco 2960', 'London, Green Str'),
#     ('0011.AAAA.CCCC', 'sw4', 'Cisco 3750', 'London, Green Str')]
#
# data2 = [
#     ('0000.1111.0001', 'sw5', 'Cisco 3750', 'London, Green Str'),
#     ('0000.1111.0002', 'sw6', 'Cisco 3750', 'London, Green Str'),
#     ('0000.1111.0003', 'sw7', 'Cisco 3750', 'London, Green Str'),
#     ('0000.1111.0004', 'sw8', 'Cisco 3750', 'London, Green Str')]
#
# query = "INSERT into switch values (?, ?, ?, ?)"
# for row in data:
#     cursor.execute(query, row)
#
# connection.commit()
#
# cursor.executemany(query, data2)
# connection.commit()
#
# cursor.executescript('''
#     create table switches(
#         hostname     text not NULL primary key,
#         location     text
#     );
#
#     create table dhcp(
#         mac
#         ip
#         vlan
#         interface    text,
#         switch       text not null references switches(hostname)
#     );
# ''')
# connection.commit()
#
# result = cursor.execute('select * from switch')
# for row in result:
#     print(row)
