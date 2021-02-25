import sqlite3

import pika
import pika.exceptions
import os
import sys
import subprocess
import json
import os.path
import time
from datetime import datetime, timedelta
import requests
import docker
from pprint import pprint

# Threads and Processes
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

# Logging
import logging
from logging.handlers import TimedRotatingFileHandler

# My modules
from work_sql import DataBaseSQL


"""
Описание вакансии: https://hh.ru/vacancy/37770187
Информация о НИЦ АО «Швабе» в МФТИ:
https://mipt.ru/science/labs/shvabe.ai/
Информация об iPavlov: http://ipavlov.ai/
Реализовать rest сервис. Aiohttp или FastApi.
- Методом POST отправлять данные в json формате. Распарсить данные и
сохранить в БД.
- Методом GET получать все данные из БД, Формат json. Желательно с
реализацией в запросе limit offset.
- Сделать отдельный метод для запроса POST методом или PUT для
изменения данных для конкретной записи в БД (по id или uuid к примеру).
- Сделать отдельный метод для запроса методом GET. Необходимо, чтобы
было возможно получать данные в формате xml и json. Например: url вида
localhost:8080/product/1/json/ и получать данные по id=1 в формате json или
localhost:8080/product/1/xml/ - соответственно в формате xml
*БД использовать postgres.

if io_bound:
    if io_very_slow:
        print("Use Asyncio")
    else:
       print("Use Threads")
else:
    print("Multi Processing")

CPU Bound => Multi Processing
I/O Bound, Fast I/O, Limited Number of Connections => Multi Threading
I/O Bound, Slow I/O, Many connections => Asyncio
"""


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DockerCC:
    def __init__(self, requests_config=None, update_time=None):
        self.dockerClient = docker.from_env(timeout=600)

    def connection(self):
        pass

    def build_new_cont(self):
        pass

    def check_containers(self):
        pass


class SomeClassForDB:
    def __enter__(self):
        self.con = sqlite3.connect('/data/Oops')
        self.con.row_factory = dict_factory
        self.cursor = self.con.cursor()
        return self.cursor

    def __exit__(self, type, value, tb):
        try:
            if not tb:
                self.con.commit()
            self.cursor.close()
            self.con.close()
        except Exception as e:
            logging.exception(e)


class REQController:
    def __init__(self, requests_config, update_time=None):
        self.request_config = requests_config
        self.update_time = update_time

        # TODO ┌=========================== TIME SET =============================┐
        if update_time:
            self.hour = int(self.update_time.split(":")[0])                      # 03
            self.minutes = int(self.update_time.split(":")[1])                   # 00
            now = datetime.now()
            self.set_update_date(now=now, hour=self.hour, minute=self.minutes)
        # TODO └=========================== TIME SET =============================┘

    def monitor(self, request_type, webid):
        if webid:
            logging.warning("MONITOR: COMMAND FROM FLASK")
        else:
            logging.warning("MONITOR: TEST START")

    def post_data(self, request_type, webid):
        if webid:
            logging.warning("POST_DATA: COMMAND FROM FLASK")
            for id in range(1, 20):
                db.insert_execute(insert_data=(id, "SOME TEXT HERE", db.get_timestamp(), "KOTOPES"))
        else:
            logging.warning("POST_DATA: TEST START")

    def get_data(self, request_type, webid):
        if webid:
            logging.warning("GET_DATA: COMMAND FROM FLASK")
            data = db.select_execute()
            logging.info(data)
        else:
            logging.warning("GET_DATA: TEST START")

    def update_token(self, request_type, webid):
        if webid:
            logging.warning("UPDATE_TOKEN: COMMAND FROM FLASK")
        else:
            logging.warning("UPDATE_TOKEN: TEST START")

    def start_scan(self, request_type, webid):
        if webid:
            logging.warning("START_SCAN: COMMAND FROM FLASK")
        else:
            logging.warning("START_SCAN: TEST START")

    def set_update_date(self, now, hour, minute):
        logging.info("SET_UPDATE_DATE")


class RabbitMQ:
    def __init__(self):
        self.extra = {"queue": "rabbit" + ((15 - len("rabbit")) * " ")}
        self.connection = None
        self.channel = None
        self.connect_to_rabmq()

    def connect_to_rabmq(self):
        try:
            while True:
                try:
                    logging.getLogger("pika").propagate = False
                    credentials = pika.PlainCredentials(username=db.config_get_param("RabbitMQ", "login"),
                                                        password=db.config_get_param("RabbitMQ", "pass"))
                    connection_parameters = pika.ConnectionParameters(
                        host=db.config_get_param("RabbitMQ", "server"),
                        port=int(db.config_get_param("RabbitMQ", "port")),
                        credentials=credentials
                    )
                    self.connection = pika.BlockingConnection(connection_parameters)
                    self.channel = self.connection.channel()
                    self.channel.queue_declare(queue="REQController", durable=True)  # 'Static_controller'
                                                                    # durable - устойчивая, сообщения не потеряются
                    break
                except Exception as exc:
                    logging.error(exc, extra=self.extra)
                    time.sleep(3)
            logging.info("Connect to RabbitMQ successful", extra=self.extra)
        except Exception as e:
            logging.error(e, extra=self.extra)

    def chkmessage(self):
        # {"command": "POST", "webid": command["id"], "target": antivr["name"]}
        # TODO: test main_img building -> send to GUI rabbit:  {"command": "updatelic", "webid": "", "target": "avira"}
        try:
            method_frame, header_frame, body = self.channel.basic_get('REQController')  # 'Static_controller'
            if method_frame:
                logging.info((method_frame, header_frame, body), extra=self.extra)
                db.update_config()
                try:
                    data = json.loads(body.decode())
            # FIXME: ┌=====================================================================┐
                    if data["command"].split("_")[0] == "POST":
                        logging.info(data["command"], extra=self.extra)

                        some_list = list()
                        if data["target"] not in some_list:
                            queue.put("POST_json:{}:{}".format(data["target"], data.get("webid")))
                        else:
                            postresp = requests.post('None')

                    elif data["command"].split("_")[0] == "GET":
                        some_list = list()
                        if data["target"] not in some_list:
                            queue.put("GET_json:{}:{}".format(data["target"], data.get("webid")))
            # FIXME: └=====================================================================┘
                except Exception as exc:
                    logging.exception(exc, extra=self.extra)
                try:
                    self.channel.basic_ack(method_frame.delivery_tag)
                except pika.exceptions.ConnectionClosed as e:
                    logging.exception(e, extra=self.extra)
                    self.connect_to_rabmq()
                logging.info('Waiting for messages', extra=self.extra)
        except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed) as e:
            logging.error(e, extra=self.extra)
            self.connect_to_rabmq()
        except Exception as e:
            # FIXME: pass? self.channel.basic_ack(method_frame.delivery_tag)?
            # logging.error(type(e), extra=self.extra)
            # logging.error(f"pika duplicate get ok status: {e}", extra=self.extra)
            pass
        finally:
            queue.put("chkmessage")

    def send_torabbit(self, value, queue):
        while True:
            try:
                logging.info("Send to: {}, {}".format(queue, value), extra=self.extra)
                self.channel.basic_publish(exchange='',
                                           routing_key=queue,
                                           body=value,
                                           properties=pika.BasicProperties(delivery_mode=2, content_type='text/plain'))
            except pika.exceptions.ConnectionClosed as e:
                logging.exception(e, extra=self.extra)
                self.connect_to_rabmq()
            else:
                break


def monitor():
    pass


def main(thread_limit):
    """
        Update containers in thread_limit threads
    TODO:
        1. monitor()                    -- monitoring container work ( check all container status, restart if needed )
        2. build_new_cont("lic")        -- update Antivirus license
        3. build_new_cont("updatedb")   -- update Antivirus DataBase
    """
    i = 0
    with ThreadPoolExecutor(thread_limit) as executor:
        while True:
            i += 1
            if i > 100:
                db.update_config()
                i = 0

            mission = queue.get()
            # Docker commands
            # TODO ┌================================= DOCKER =======┐
            if mission in docker_controllers:
                # set to thread -> monitor()
                executor.submit(docker_controllers[mission].monitor)
            # TODO └================================= DOCKER =======┘

            # RabbitMQ commands
            # TODO ┌================================= POST ===================================┐
            elif mission.startswith("POST_json"):
                splited = mission.split(":")    # {command}:{target}:{webid}" -> POST_json:json:555
                if config["Requests"][splited[1]]["type"] == "json":
                    # set to thread -> (controllers["POST_json"].post_data, "json", "555")
                    executor.submit(request_controllers[splited[1]].post_data, "json",
                                    splited[2] if splited[2] != "None" else None)
            elif mission.startswith("POST_uuid"):
                splited = mission.split(":")
                if config["Requests"][splited[1]]["type"] == "uuid":
                    executor.submit(request_controllers[splited[1]].post_data, "uuid",
                                    splited[2] if splited[2] != "None" else None)
            # TODO └================================= POST ===================================┘

            # TODO ┌================================= GET ===========================┐
            elif mission.startswith("GET_json"):
                splited = mission.split(":")
                if config["Requests"][splited[1]]["type"] == "json":
                    executor.submit(request_controllers[splited[1]].get_data, "json",
                                    splited[2] if splited[2] != "None" else None)
            elif mission.startswith("GET_xml"):
                splited = mission.split(":")
                if config["Requests"][splited[1]]["type"] == "xml":
                    executor.submit(request_controllers[splited[1]].get_data, "xml",
                                    splited[2] if splited[2] != "None" else None)
            # TODO └================================= GET ===========================┘

            # TODO ┌================================= OTHER =============================┐
            elif mission.startswith("TOKEN"):
                splited = mission.split(":")
                if config["Requests"][splited[1]]["type"] == "json":
                    executor.submit(request_controllers[splited[1]].update_token, "json",
                                    splited[2] if splited[2] != "None" else None)
            elif mission.startswith("SCAN"):
                splited = mission.split(":")
                if config["Requests"][splited[1]]["type"] == "json":
                    executor.submit(request_controllers[splited[1]].start_scan, "json",
                                    splited[2] if splited[2] != "None" else None)
            # TODO └================================= OTHER =============================┘

            # (3) at start queue get 2 messages: "chkmessage" and "chkcontainers" -> check loop
            # "chkmessage"    -> checks rabbit cmds -> "chkmessage"
            # "chkcontainers" -> db.select_execute  -> delete expired containers -> "chkcontainers"
            # TODO ┌========== RESTART ============┐
            elif mission == "chkmessage":
                executor.submit(rbmq.chkmessage)
            # elif mission == "chkcontainers":
            #     executor.submit(db.select_execute)
            time.sleep(0.1)
            # TODO └========== RESTART ============┘


try:
    contid = subprocess.check_output('cut -c9-20 < /proc/1/cpuset', shell=True, universal_newlines=True)[:-1]
except Exception as e:
    print("You are using not docker container build! contid in logs will be set as NotContainer")
    contid = "NotContainer"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : [' + contid + '] :[%(filename)s.%(lineno)d]: %(levelname)s : %(message)s',
    handlers=[TimedRotatingFileHandler("/logs/PostgreSQL_{}.log".format(contid), when="midnight")])

#


logging.info("STArt Main.py")
cfg_file = "config.json"
cfg_template = "posts_template.sql"

db = DataBaseSQL(cfg_file, cfg_template)
lock = threading.Lock()
rbmq = RabbitMQ()
queue = Queue()

thread_number = db.config_get_param("Threads", "thread_limit")
db.create_db_execute()
db.create_table_execute()

config = db.default_config

# for id in range(1, 11):
#     db.insert_execute(insert_data=(id, "SOME TEXT HERE", db.get_timestamp(), "KOTOPES"))
# datas = db.select_execute()
# logging.info(datas)
# pprint(datas)
#

# TODO ======= Just for TEST that all is ok in tasks from queue, other tasks comes from RabbitMQ server ==========
# TODO ┌========================================== QUEUE SET UP ==================================================┐
request_controllers = dict()
docker_controllers = dict()
for request in config["Requests"]:

    if request == "TOKEN" or request == "SCAN":
        request_controllers[config["Requests"][request]["queue"]] = REQController(
            config["Requests"][request],
            config["Requests"][request]["update_time"])
        queue.put(config["Requests"][request]["queue"] + f":{request}:")

    else:
        # controllers["POST_json"] = REQController("POST_json")
        request_controllers[config["Requests"][request]["queue"]] = REQController(config["Requests"][request])
        # queue.put("POST_json")
        queue.put(config["Requests"][request]["queue"] + f":{request}:")
        # queue = ["TOKEN", "SCAN", "POST_json", "POST_uuid", "GET_json", "GET_xml", "chkmessage"]
        # request_controllers = {"TOKEN": REQController(requests_config=dict(Requests), update_time=None), ... }
# TODO └========================================== QUEUE SET UP ==================================================┘


# This queue is for RabbitMQ (Activator)
# TODO ┌=========== START =============┐
queue.put("chkmessage")
# This queue is for DataBase
# queue.put("chkcontainers")
# TODO └=========== START =============┘


if __name__ == "__main__":
    # order:
    # 1. QUEUE SET UP
    # 2. START (threads)
    # 3. DOCKER, POST, GET, OTHER
    # 4. launch RESTART listener (rabbit)




    # Threads:
    main(thread_number)





