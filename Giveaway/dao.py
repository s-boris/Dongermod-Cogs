import logging

import random
import datetime
import json
import os
import pymysql

from pymysql import MySQLError

log = logging.getLogger(__name__)


class DAO:
    """Custom Dongermod DAO"""

    def __init__(self):
        self.sql_schema_file = "../Activitytracker/dongermod_schema.sql"
        self.server_default_config_file = (
            "../Activitytracker/default_server_config.json"
        )
        self.member_stats_default_config_file = (
            "../Activitytracker/default_member_stats.json"
        )
        self.connection = self.create_connection()
        self.giveaway_path = "data/giveaway.json"

    def create_connection(self):
        con = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="user",
            password="pw",
            db="dongermod",
            autocommit=True,
        )
        return con

    def get_server_config_template(self):
        with open(self.server_default_config_file, "r") as json_template_file:
            defaut_conf = json.load(json_template_file)
        return defaut_conf

    def get_member_stats_template(self):
        with open(self.member_stats_default_config_file, "r") as json_template_file:
            defaut_conf = json.load(json_template_file)
        return defaut_conf

    def add_new_server(self, server_id):
        try:
            with self.connection.cursor() as cursor:
                default_config = self.get_server_config_template()
                sql1 = "INSERT INTO queue VALUES ();"
                cursor.execute(sql1)
                created_queue_id = cursor.lastrowid

                config_as_string = json.dumps(default_config)
                sql2 = "INSERT INTO server (server_discord_id,queue_fk, server_configuration_json) VALUES (%s, %s, %s);"
                cursor.execute(sql2, (server_id, created_queue_id, config_as_string))
            self.connection.commit()
        finally:
            print("added new server")

    def get_server_config(self, server_id):
        config = None
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT server_configuration_json FROM server WHERE server_discord_id = %s;"
                cursor.execute(sql, (server_id,))
                c = cursor.fetchone()
                if c:
                    if isinstance(c[0], dict):
                        config = c[0]
                    else:
                        config = json.loads(c[0])
        except MySQLError as e:
            print("MYSQL error: {!r}, errno is {}".format(e, e.args[0]))
        return config

    def update_member_stats(self, server_id, member_id, j_stats):
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT stats_json FROM member_stats WHERE member_fk=%s AND server_fk=%s;"
                cursor.execute(sql, (member_id, server_id))
                c = cursor.fetchone()
                found_data = None
                if c:
                    found_data = c[0]
                if found_data:
                    js_stats = json.dumps(j_stats)
                    sql2 = "UPDATE member_stats SET stats_json = %s WHERE server_fk= %s AND member_fk = %s;"
                    cursor.execute(sql2, (js_stats, server_id, member_id))
                else:
                    js_stats = json.dumps(j_stats)
                    sql3 = "INSERT INTO member_stats (member_fk, server_fk, stats_json) VALUES (%s, %s, %s);"
                    cursor.execute(sql3, (member_id, server_id, js_stats))
            self.connection.commit()
        finally:
            pass

    def get_member_stats(self, server_id, member_id):
        found_data = self.get_member_stats_template()
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT stats_json FROM member_stats WHERE member_fk=%s AND server_fk=%s;"
                cursor.execute(sql, (member_id, server_id))
                c = cursor.fetchone()
                if c:
                    found_data = c[0]
        finally:
            pass
            if isinstance(found_data, dict):
                return found_data
            else:
                return json.loads(found_data)

    # ---------- Giveaway --------------

    def get_sub_in_giveaway(self, user_id):
        list = []
        try:
            with open(self.giveaway_path) as data_file:
                lines = data_file.readlines()
                for l in lines:
                    list.append(l)
        except FileNotFoundError:
            print("File not found...")
        if user_id + "\n" in list:
            return True
        else:
            return False

    def wipe_giveaway(self):
        if os.path.exists(self.giveaway_path):
            os.rename(
                self.giveaway_path,
                "data/giveaway_"
                + str(datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
                + ".json",
            )
        open(self.giveaway_path, "w+").close()

    def append_sub_to_giveaway(self, user_id, tickets):
        with open(self.giveaway_path, "a") as myfile:
            for _ in range(entries):
                myfile.write(user_id + "\n")

    def get_random_sub_from_giveaway(self):
        list = []
        try:
            with open(self.giveaway_path) as data_file:
                lines = data_file.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    if line:
                        list.append(line)
        except FileNotFoundError:
            print("File not found...")
        if list:
            winner = random.choice(list)
            return winner
        else:
            return None
