from psycopg2.extras import RealDictCursor


class URLError(Exception):
    pass


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_url_by_name(self, name):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s", (name,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_url_by_id(self, url_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def save_url(self, normalized_url):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                (normalized_url, )
            )
            url_id = cur.fetchone()[0]
        self.conn.commit()
        return url_id

    def save_url_check(self, url_check_data):
        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO url_checks (
                url_id,
                response_code,
                h1,
                title,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
            """, (
                url_check_data['url_id'],
                url_check_data['response_code'],
                url_check_data['h1'],
                url_check_data['title'],
                url_check_data['description']
            )
        )
        self.conn.commit()

    def get_url_checks(self, url_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT
                id,
                response_code,
                h1,
                title,
                description,
                created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY created_at DESC
            """, (url_id,))
            rows = cur.fetchall()
            return rows
