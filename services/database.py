import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


DATABASE_FILE = Path("data/ai_search.db")


RESULT_COLUMNS = [
    "run_date",
    "run_timestamp",
    "scan_id",
    "platform",
    "provider",
    "model",
    "prompt_id",
    "category",
    "prompt",
    "wake_tech_mentioned",
    "position",
    "competitors",
    "wake_tech_url",
    "competitor_urls",
    "score",
    "sentiment",
    "strengths",
    "weaknesses",
    "recommendations",
    "notes",
    "response",
    "latency_seconds",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "response_id",
]


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.
    """
    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_FILE,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    """
    Create the database and results table if they do not exist.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                run_date TEXT NOT NULL,
                run_timestamp TEXT NOT NULL,
                scan_id TEXT NOT NULL,

                platform TEXT NOT NULL,
                provider TEXT,
                model TEXT,

                prompt_id TEXT NOT NULL,
                category TEXT,
                prompt TEXT NOT NULL,

                wake_tech_mentioned TEXT,
                position INTEGER DEFAULT 0,
                competitors TEXT,
                wake_tech_url TEXT,
                competitor_urls TEXT,

                score INTEGER DEFAULT 0,
                sentiment TEXT,

                strengths TEXT,
                weaknesses TEXT,
                recommendations TEXT,
                notes TEXT,

                response TEXT,

                latency_seconds REAL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                response_id TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_results_scan_id
            ON results(scan_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_results_platform_prompt
            ON results(platform, prompt_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_results_timestamp
            ON results(run_timestamp)
            """
        )

        connection.commit()


def clean_database_value(value: Any) -> Any:
    """
    Convert values into types SQLite can store safely.
    """
    if value is None:
        return None

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass

    return value


def save_result(result: dict[str, Any]) -> int:
    """
    Save one AI search result and return its database ID.
    """
    initialize_database()

    cleaned_result = {
        column: clean_database_value(
            result.get(column)
        )
        for column in RESULT_COLUMNS
    }

    placeholders = ", ".join(
        ["?"] * len(RESULT_COLUMNS)
    )

    column_names = ", ".join(
        RESULT_COLUMNS
    )

    values = [
        cleaned_result[column]
        for column in RESULT_COLUMNS
    ]

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            INSERT INTO results (
                {column_names}
            )
            VALUES (
                {placeholders}
            )
            """,
            values,
        )

        connection.commit()

        return int(cursor.lastrowid)


def save_results(
    results: list[dict[str, Any]],
) -> int:
    """
    Save multiple results in a single database transaction.
    """
    if not results:
        return 0

    initialize_database()

    placeholders = ", ".join(
        ["?"] * len(RESULT_COLUMNS)
    )

    column_names = ", ".join(
        RESULT_COLUMNS
    )

    rows = []

    for result in results:
        cleaned_result = {
            column: clean_database_value(
                result.get(column)
            )
            for column in RESULT_COLUMNS
        }

        rows.append(
            [
                cleaned_result[column]
                for column in RESULT_COLUMNS
            ]
        )

    with get_connection() as connection:
        connection.executemany(
            f"""
            INSERT INTO results (
                {column_names}
            )
            VALUES (
                {placeholders}
            )
            """,
            rows,
        )

        connection.commit()

    return len(rows)


def load_results() -> pd.DataFrame:
    """
    Load all results from SQLite into a DataFrame.
    """
    initialize_database()

    query = """
        SELECT
            run_date,
            run_timestamp,
            scan_id,
            platform,
            provider,
            model,
            prompt_id,
            category,
            prompt,
            wake_tech_mentioned,
            position,
            competitors,
            wake_tech_url,
            competitor_urls,
            score,
            sentiment,
            strengths,
            weaknesses,
            recommendations,
            notes,
            response,
            latency_seconds,
            input_tokens,
            output_tokens,
            total_tokens,
            response_id
        FROM results
        ORDER BY id ASC
    """

    with get_connection() as connection:
        return pd.read_sql_query(
            query,
            connection,
        )


def result_exists(
    scan_id: str,
    platform: str,
    prompt_id: str,
) -> bool:
    """
    Check whether a particular result is already saved.
    """
    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM results
            WHERE scan_id = ?
              AND platform = ?
              AND prompt_id = ?
            LIMIT 1
            """,
            (
                scan_id,
                platform,
                prompt_id,
            ),
        ).fetchone()

    return row is not None


def get_result_count() -> int:
    """
    Return the number of saved results.
    """
    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM results
            """
        ).fetchone()

    return int(row["total"])