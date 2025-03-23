import time
import psycopg2
from psycopg2 import Error as Psycopg2Error


class DatabaseConnection:
    def __init__(self, dsn, cursor_factory=None, autocommit=True):
        """
        Initializes a database connection.

        :param dsn: Database connection string.
        :param cursor_factory: Cursor factory (e.g., RealDictCursor).
        :param autocommit: If True, automatically commits transactions.
        """
        self.dsn = dsn
        self.cursor_factory = cursor_factory
        self.autocommit = autocommit
        self.conn = None

    def __enter__(self):
        """
        Opens a connection and returns a cursor.
        """
        self.conn = self._connect_with_retries()
        self.conn.autocommit = self.autocommit
        if self.cursor_factory:
            return self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the connection and handles exceptions.
        """
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
            self.conn = None

    def _handle_error(self, error):
        """
        Handles database-related errors.
        """
        print(f"Database error occurred: {error}")

    def _connect_with_retries(self, max_retries=5, delay=2):
        """
        Attempts to connect to the database with retries.

        :param max_retries: Maximum number of retry attempts.
        :param delay: Delay between retries in seconds.
        :return: A database connection object.
        """
        retries = 0
        while retries < max_retries:
            try:
                conn = psycopg2.connect(self.dsn)
                return conn
            except Psycopg2Error as e:
                print(f"Connection attempt {retries + 1} failed: {e}")
                retries += 1
                time.sleep(delay)
        raise Psycopg2Error("Database connection is not available")

    def check_connection(self):
        """
        Checks if the database connection is active.
        """
        try:
            with self as cursor:
                cursor.execute("SELECT 1")
            return True
        except Psycopg2Error:
            return False

    def reconnect(self):
        """
        Reconnects to the database.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
        return self.__enter__()