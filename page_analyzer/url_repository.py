from datetime import datetime
import logging
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from psycopg2 import Error as Psycopg2Error


class DatabaseConnectionPool:
    def __init__(self, dsn, minconn=1, maxconn=10):
        self.dsn = dsn
        self.connection_pool = pool.SimpleConnectionPool(
            minconn, maxconn, dsn
        )

    def get_cursor(self, cursor_factory=None):
        """
        Returns a cursor with the specified cursor factory.
        """
        conn = self.connection_pool.getconn()
        return conn.cursor(cursor_factory=cursor_factory)

    def put_cursor(self, cursor):
        """
        Returns the connection to the pool.
        """
        if cursor and cursor.connection:
            self.connection_pool.putconn(cursor.connection)


class UrlRepository:
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool

    def _execute_query(
            self,
            query,
            params=None,
            fetch_one=False,
            fetch_all=False,
            cursor_factory=None
    ):
        """
        A general-purpose method for executing SQL queries.
        Returns one row, all rows, or None depending on the parameters.
        """
        cursor = None
        try:
            cursor = self.connection_pool.get_cursor(
                cursor_factory=cursor_factory
            )
            cursor.execute(query, params)
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            if fetch_all:
                return cursor.fetchall()
            return None
        except Psycopg2Error as e:
            logging.error(
                f"Ошибка при выполнении запроса: "
                f"{str(e)}. Запрос: {query}, Параметры: {params}"
            )
            raise
        finally:
            if cursor:
                self.connection_pool.put_cursor(cursor)

    def get_url_by_name(self, name):
        """
          Gets a URL by its name.
        """
        query = "SELECT * FROM urls WHERE name = %s"
        return self._execute_query(
            query, (name,), fetch_one=True, cursor_factory=RealDictCursor
        )

    def get_url_by_id(self, url_id):
        """
        Gets a URL by its ID.
        """
        query = "SELECT * FROM urls WHERE id = %s"
        return self._execute_query(
            query, (url_id,), fetch_one=True, cursor_factory=RealDictCursor
        )

    def save_url(self, normalized_url):
        """
        Saves a URL to the database and returns its ID.
        """
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s)
            RETURNING id
        """
        params = (normalized_url, datetime.now())
        try:
            cursor = self.connection_pool.get_cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                cursor.connection.commit()
                return result[0]
        except Psycopg2Error as e:
            logging.error(f"Ошибка при сохранении URL: {str(e)}")
            if cursor and cursor.connection:
                cursor.connection.rollback()
        finally:
            if cursor:
                self.connection_pool.put_cursor(cursor)
        return None

    def save_url_check(self, url_check_data):
        """
        Saves the URL check result to the database.
        """
        query = """
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            url_check_data["url_id"],
            url_check_data["status_code"],
            url_check_data["h1"],
            url_check_data["title"],
            url_check_data["description"],
            datetime.now(),
        )
        try:
            cursor = self.connection_pool.get_cursor()
            cursor.execute(query, params)
            cursor.connection.commit()
        except Psycopg2Error as e:
            logging.error(f"Ошибка при сохранении проверки URL: {str(e)}")
            if cursor and cursor.connection:
                cursor.connection.rollback()
        finally:
            if cursor:
                self.connection_pool.put_cursor(cursor)

    def get_url_checks(self, url_id):
        """
        Gets all checks for the specified URL.
        """
        query = """
            SELECT
                id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        return self._execute_query(
            query, (url_id,), fetch_all=True, cursor_factory=RealDictCursor
        )

    def get_all_urls(self):
        """
        Gets all URLs with last check information.
        """
        query = """
            SELECT
                u.id AS url_id,
                u.name AS name,
                uc.created_at AS url_check_created_at,
                uc.status_code AS last_check_status_code
            FROM
                urls u
            LEFT JOIN (
                SELECT
                    url_id,
                    status_code,
                    created_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY url_id ORDER BY id DESC
                    ) AS rn
                FROM
                    url_checks
            ) uc
            ON u.id = uc.url_id AND uc.rn = 1
            ORDER BY
                u.id DESC
        """
        return self._execute_query(
            query, fetch_all=True, cursor_factory=RealDictCursor
        )
