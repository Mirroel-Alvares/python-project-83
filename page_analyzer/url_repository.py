from datetime import datetime
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from psycopg2 import Error as Psycopg2Error
from contextlib import contextmanager


class DatabaseConnectionPool:
    def __init__(self, dsn, minconn=1, maxconn=10):
        self.dsn = dsn
        self.minconn = minconn
        self.maxconn = maxconn
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

    def check_connection(self):
        """
        Checks if the connection pool is healthy.
        """
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")  # Простой запрос для проверки соединения
            cursor.close()
            self.connection_pool.putconn(conn)
            return True
        except Psycopg2Error:
            return False

    def close_all_connections(self):
        """
        Closes all connections in the pool.
        """
        self.connection_pool.closeall()

    @contextmanager
    def cursor(self, cursor_factory=None):
        """
        A context manager for handling database cursors.
        """
        conn = None
        cursor = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor(cursor_factory=cursor_factory)
            yield cursor
        except Psycopg2Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.connection_pool.putconn(conn)


class UrlRepository:
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        if not self.connection_pool.check_connection():
            raise Psycopg2Error("Database connection is not available")

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
        with self.connection_pool.cursor(
                cursor_factory=cursor_factory
        ) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            if fetch_all:
                return cursor.fetchall()
            return None

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
        with self.connection_pool.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                cursor.connection.commit()
                return result[0]
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
        with self.connection_pool.cursor() as cursor:
            cursor.execute(query, params)
            cursor.connection.commit()

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