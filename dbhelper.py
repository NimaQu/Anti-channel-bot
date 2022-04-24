import sqlite3
import logging


class DBHelper:
    def __init__(self, dbname="data.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = ('''
        CREATE TABLE IF NOT EXISTS group_config
        (
        group_id INTEGER PRIMARY KEY NOT NULL,
        operate TEXT,
        message TEXT,
        silent_mode INTEGER
        );
        ''')
        try:
            self.conn.executescript(stmt)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(str(e))

    def get_group_config(self, group_id, field: str = 'all'):
        """
        获取群配置，默认返回所有配置，可以指定返回某个配置
        field: 值为 challenge_failed_action,
        challenge_timeout_action,
        challenge_timeout,
        challenge_type,
        enable_global_blacklist,
        enable_third_party_blacklist

        return: 如果指定了 field，返回指定的配置，否则返回所有配置

        """

        stmt = "SELECT * FROM group_config WHERE group_id == (?)"
        args = group_id
        cur = self.conn.cursor()
        try:
            cur.execute(stmt, (args,))
            result = cur.fetchone()
            if result is None:
                return None
            elif field == 'all':
                group_config = {'operate': result[1], 'message': result[2], 'silent_mode': result[3]}
                # remove None value
                null_key = [i for i in group_config if group_config[i] is None]
                for key in null_key:
                    group_config.pop(key)
                return group_config
            else:
                return None
        except sqlite3.Error as e:
            logging.error(str(e))
            return None

    def new_group_config(self, group_id):
        stmt = "INSERT OR REPLACE INTO group_config (group_id) VALUES (?)"
        args = (group_id,)
        try:
            self.conn.execute(stmt, args)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(str(e))
            return False

    def set_group_config(self, group_id, key, value):
        if self.get_group_config(group_id) is None:
            self.new_group_config(group_id)
        value_type = 'str'
        if key == 'operate':
            if value != 'ban' and value != 'del' and value != 'all':
                return False
            stmt = "UPDATE group_config SET operate = (?) WHERE group_id = (?)"
        elif key == 'message':
            stmt = "UPDATE group_config SET message = (?) WHERE group_id = (?)"
        elif key == 'silent_mode':
            stmt = "UPDATE group_config SET silent_mode = (?) WHERE group_id = (?)"
            value_type = 'bool'
        else:
            return False

        if value_type == 'int':
            try:
                value = int(value)
            except ValueError:
                return False
        if value_type == 'bool':
            try:
                value = int(value)
                if value != 0 and value != 1:
                    return False
            except ValueError:
                return False

        args = (value, group_id)
        cur = self.conn.cursor()
        try:
            cur.execute(stmt, args)
            rows = cur.rowcount
            self.conn.commit()
            if rows == 0:
                return False
            else:
                return True
        except sqlite3.Error as e:
            logging.error(str(e))
