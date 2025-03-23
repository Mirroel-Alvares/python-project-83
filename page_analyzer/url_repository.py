from datetime import datetime
from psycopg2.extras import RealDictCursor
from .db_connection import DatabaseConnection


class UrlRepository:
    def __init__(self, dsn):
        self.dsn = dsn

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

        :param query: SQL query to execute.
        :param params: Parameters for the query.
        :param fetch_one: If True, fetches a single row.
        :param fetch_all: If True, fetches all rows.
        :param cursor_factory: Cursor factory (e.g., RealDictCursor).
        :return: A dictionary, list of dictionaries, or None.
        """
        with DatabaseConnection(
                self.dsn,
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
        Retrieves a URL by its name.

        :param name: The name of the URL.
        :return: A dictionary containing the URL data or None if not found.
        """
        query = "SELECT * FROM urls WHERE name = %s"
        return self._execute_query(
            query, (name,), fetch_one=True, cursor_factory=RealDictCursor
        )

    def get_url_by_id(self, url_id):
        """
        Retrieves a URL by its ID.

        :param url_id: The ID of the URL.
        :return: A dictionary containing the URL data or None if not found.
        """
        query = "SELECT * FROM urls WHERE id = %s"
        return self._execute_query(
            query, (url_id,), fetch_one=True, cursor_factory=RealDictCursor
        )

    def save_url(self, normalized_url):
        """
        Saves a URL to the database and returns its ID.

        :param normalized_url: The normalized URL to save.
        :return: The ID of the saved URL or None if the operation failed.
        """
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s)
            RETURNING id
        """
        params = (normalized_url, datetime.now())
        with DatabaseConnection(self.dsn) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                cursor.connection.commit()
                return result[0]
            return None

    def save_url_check(self, url_check_data):
        """
        Saves the result of a URL check to the database.

        :param url_check_data: A dictionary containing URL check data.
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
        with DatabaseConnection(self.dsn) as cursor:
            cursor.execute(query, params)
            cursor.connection.commit()

    def get_url_checks(self, url_id):
        """
        Retrieves all checks for a specific URL.

        :param url_id: The ID of the URL.
        :return: A list of dictionaries containing URL check data.
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
        Retrieves all URLs with information about their last check.

        :return: A list of dictionaries containing URL data
        and last check information.
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