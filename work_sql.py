#
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from pprint import pprint
import json
import time
import os
import subprocess
from datetime import datetime, timedelta

# DictCursor for json output from DataBase data
import pymysql
from pymysql.cursors import DictCursor

import logging
from logging.handlers import TimedRotatingFileHandler


class Configurator:
    """ Gather information from config files """

    def __init__(self, config_file, template_file):
        self.config_file = config_file
        self.template_file = template_file

        with open("baseconfig/{}".format(self.config_file)) as def_f:
            self.default_config = json.load(def_f)
        with open("dbtemplates/templates/{}".format(self.template_file)) as def_f:
            self.default_template = def_f.read()

        self.web_config = dict()
        self.web_template = str()
        self.update_date = None
        self.update_config()

    def update_config(self):
        if os.path.exists("webconf/{}".format(self.config_file)):
            with open("webconf/{}".format(self.config_file)) as web_f:
                self.web_config = json.load(web_f)
                # FIXME: self.default_config = json.load(f)
        else:
            with open("baseconfig/{}".format(self.config_file)) as def_f:
                self.default_config = json.load(def_f)

        if os.path.exists("webconf/templates/{}".format(self.template_file)):
            with open("webconf/templates/{}".format(self.template_file)) as web_f:
                self.web_template = web_f.read()
                # FIXME: self.default_template = f.read()
        else:
            with open("dbtemplates/templates/{}".format(self.template_file)) as def_f:
                self.default_template = def_f.read()

    def nested_get(self, input_dict, nested_key):
        internal_dict_value = input_dict
        for k in nested_key:
            internal_dict_value = internal_dict_value.get(k, "NoMatchOption")
            if internal_dict_value == "NoMatchOption":
                return "NoMatchOption"
        return internal_dict_value

    def config_get_param(self, *params):
        data = self.nested_get(self.web_config, params)
        # FIXME: self.nested2_get(self.web_template ??)
        if data == "NoMatchOption":
            data = self.nested_get(self.default_config, params)
        if data == "NoMatchOption":
            data = None
        return data

    def file_reader(self, filename):
        """
        Simple file reader

        :param filename: (path_to_file)
        :return: text
        """
        with open(filename, "r") as file_text:
            text = file_text.read()
        return text

    def set_update_date(self, now=None, hour=None, minute=None):
        """
        Set update Date to the next day.

        :param now: datetime.now()
        :param hour: integer:
        :param minute: integer:
        :return: date:  self.update_date
        """
        # if 1:00 < 3:00 AM
        if now < now.replace(hour=hour, minute=minute):
            # update_date = 3:00 18.01.2020
            self.update_date = now.replace(hour=hour, minute=minute)
        else:
            # update_date = 3:00 19.01.2020
            self.update_date = (now + timedelta(days=1)).replace(hour=hour, minute=minute)
        logging.info("Update date time: {}".format(self.update_date), extra=self.extra)

        return self.update_date


class DataBaseSQL(Configurator):
    """
    SQL DataBase class. Controls input/output data.
    Inherits from Configurator().
    """

    def __init__(self, config_file, db_template):
        super().__init__(config_file, db_template)

        self.db_config = self.config_get_param("DataBase")
        self.db_name = self.config_get_param("DataBase", "database")
        self.db_hostname = self.config_get_param("DataBase", "host")
        self._db_port = self.config_get_param("DataBase", "port")
        self._db_user = self.config_get_param("DataBase", "user")
        self._db_pass = self.config_get_param("DataBase", "password")

        self.conn = None
        self.cursor = None

        self.db_create_schema = self.file_reader(self.config_get_param("DB_extra", "create_schema_file"))
        self.db_insert_schema = self.file_reader(self.config_get_param("DB_extra", "insert_schema_file"))
        self.db_select_schema = self.file_reader(self.config_get_param("DB_extra", "select_schema_file"))
        self.db_table_template = self.file_reader(self.config_get_param("DB_extra", "table_template_file"))
        self.table_name = self.config_get_param("DB_extra", "table_name")

        self.times_b4_data_lost = self.config_get_param("DB_extra", "times_before_lost")
        self.timestamp = self.get_timestamp()

        self.create_connection()

    def get_timestamp(self):
        # timestamp = datetime.utcnow().isoformat()
        # timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return timestamp

    def create_connection(self):
        time.sleep(1)
        while True:
            try:

                logging.info(f"Trying to connect DataBase: '{self.db_name}'")
                self.conn = pymysql.connect(**self.db_config, cursorclass=DictCursor)
                self.conn.autocommit = True

            except pymysql.err.InterfaceError as exc:
                logging.error(exc)
                time.sleep(3)
            except Exception as e:
                logging.error("While connecting DB error occurred: '{}'".format(e))
                time.sleep(3)
            else:
                logging.info("Connected to DataBase")
                break

    def execute(self, query, data=None):
        """
        Execute() function allow execute any DataBase command
        No schemas used here. """
        data_from_db = None
        for _ in range(self.times_b4_data_lost):
            try:
                self.cursor = self.conn.cursor()
                logging.info("Try {}, {}".format(query, data))
                if data:
                    self.cursor.execute(query, data)
                else:
                    self.cursor.execute(query)
                if query.startswith("SELECT"):
                    data_from_db = self.cursor.fetchall()
                self.cursor.close()
            except Exception as e:
                logging.exception(e)
                self.create_connection()
            else:
                break
            # TODO: check if this useful or not (cursor.close() + conn.close())
            # finally:
            #     self.conn.close()
            #     if self.cursor:
            #         self.cursor.close()
        return data_from_db

    def insert_execute(self, insert_data):
        """
        Insert_execute() function uses schema for INSERT request to DB.
        All schemas are set in configuration files. """
        self.execute(query=self.db_insert_schema.format(self.table_name), data=insert_data)

    def select_execute(self, where_condition=None):
        """
        Select_execute() function uses schema for SELECT request to DB.
        All schemas are set in configuration files. """
        if where_condition:
            data_from_db = self.execute(query=self.db_select_schema.format(self.table_name), data=where_condition)
        else:
            data_from_db = self.execute(query=self.db_select_schema.format(self.table_name))
        return data_from_db

    def create_table_execute(self):
        """
        Create_table_execute() function uses schema for CREATE request to DB.
        All schemas are set in configuration files. """
        self.execute(query=self.default_template.format(self.table_name), data=None)

    def create_db_execute(self):
        """
        Create_db_execute() function uses template for CREATE DataBase request.
        All schemas are set in configuration files. """
        self.execute(query=self.db_create_schema.format(self.db_name))

    # TODO: function to control docker containers. Stucked containers need to be removed.
    def select_execute2(self):
        """
        Select_execute() function uses schema template for SELECT request to DataBase.
        All schemas are set in configuration files. """
        for _ in range(self.times_b4_data_lost):
            try:
                cursor = self.conn.cursor()
                # execute(text, 700sec)
                cursor.execute(
                    "SELECT containerID FROM `StaticModule-Files`.ContainersTasks WHERE timestamp < NOW() - INTERVAL %s SECOND;",
                    (cf.config_get_param("Script", "container_timeout_to_kill_sec"),))

                # extract all remaining strings from response
                res = cursor.fetchall()
                if res:
                    commands = ["docker", "rm", "-f"]
                    for container in res:
                        # commands == docker rm -f cowrie ntp dns
                        commands.append(container[0])
                    try:
                        # run command and return output (res; CalledProcessError if exitcode != 0) -> then strip output
                        output = subprocess.check_output(commands, universal_newlines=True,
                                                         stderr=subprocess.STDOUT).strip()
                    except subprocess.CalledProcessError as e:
                        logging.error(e)
                        output = e.output.strip()
                    logging.error("Stucked containers was deleted: " + output)
                    # output = ", ".join(["'{}'".format(i) for i in output.splitlines()])
                    # re.findall(r"Error: No such container: (.*)")
                # execute(text, 700sec * 3)
                cursor.execute(
                    "DELETE FROM `StaticModule-Files`.ContainersTasks WHERE timestamp < NOW() - INTERVAL %s SECOND;",
                    (cf.config_get_param("Script", "container_timeout_to_kill_sec") * 3,))
                cursor.close()
            except Exception as e:
                logging.exception(e)
                self.create_connection()
            else:
                break
            finally:
                time.sleep(5)
                # queue.put("chkcontainers")

    # TODO: write executeall function. This one is example from the book.
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
                with self.conn.cursor():
                    self.conn.execute(query, row)
            except pymysql.err.IntegrityError as e:
                if verbose:
                    print("While inserting data '{}' error occurred".format(
                        ', '.join(row), e))
            else:
                if verbose:
                    print("Data insertion '{}' pass successfully".format(', '.join(row)))

    # TODO: check exceptions from example (OperationalError, InterfaceError). Are cursor.close() + conn.close() useless?
    def _run_query(self, query_command):
        while True:
            cursor = None
            logging.info("Run Query %s", query_command)
            try:
                datas = []
                conn = self.get_conn()
                cursor = conn.cursor()
                cursor.execute(query_command)
                for row in cursor:
                    datas.append(row)
                conn.commit()

            except mysql.connector.errors.OperationalError as err:
                logging.error(err)
                self.connect()
            except mysql.connector.errors.InterfaceError as err:
                logging.exception(err)
                self.connect()
            except Exception as err:
                logging.exception(err)
            else:
                logging.info("Result of Query - %s", datas)
                return datas
            finally:
                conn.close()
                if cursor:
                    cursor.close()

    # FIXME: You still do not have text search
    def search_text(self, text):
        data = self._run_query(
            f"""SELECT
                    *
                FROM {self.table}
                WHERE
                     text  LIKE '%{text}%'
                ORDER BY created_date
                LIMIT 20;
            """)
        return data

    # FIXME: reformat function to 'delete rows from tables by id'
    def delete_row(self, row_id):
        """ Delete row from table """
        data = self._run_query(
            f"""SELECT id
                FROM {self.table}
                WHERE id = {row_id}
            """)
        if data:
            self._run_query(
                f"""DELETE
                    FROM {self.table}
                    WHERE id = {row_id}
                """)
            exit_code = 0
        else:
            exit_code = 1

        return exit_code


# TODO: test before production (Initialisation)
# cfg_file = "config.json"
# cfg_template = "posts_template.sql"
# cf = DataBaseSQL(cfg_file, cfg_template)


# TODO: test before production (Use Constructions Below)
# cf.create_db_execute()
# cf.create_table_execute()
# for id in range(10, 20):
#     cf.insert_execute(insert_data=(id, "SOME TEXT HERE", cf.get_timestamp(), "KOTOPES"))
#
# datas = cf.select_execute()
# pprint(datas)

# cf.insert_execute(insert_data={"id": 1, "text": "gg", "created_date": cf.get_timestamp(), "rubrics": "ff"})


# TODO: Choose Your Destiny...Flawless Victory!
try:
    contid = subprocess.check_output('cut -c9-20 < /proc/1/cpuset', shell=True, universal_newlines=True)[:-1]
except Exception as e:
    print("You are using not docker container build! contid in logs will be set as NotContainer")
    contid = "NotContainer"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : [' + contid + '] :[%(filename)s.%(lineno)d]: %(levelname)s : %(message)s',
    handlers=[TimedRotatingFileHandler("/logs/PostgreSQL_{}.log".format(contid), when="midnight")])


if __name__ == "__main__":
    logging.info("STArt Work_sql.py")
