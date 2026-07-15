from datetime import datetime
from pathlib import Path

import pandas as pd

from services.database import (
    get_result_count,
    initialize_database,
    save_results,
)


RESULTS_FILE = Path("data/results.csv")


def prepare_results(results: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare legacy CSV rows for the SQLite database.
    """
    prepared = results.copy()

    # Ensure run_date exists.
    if "run_date" not in prepared.columns:
        prepared["run_date"] = datetime.now().strftime(
            "%Y-%m-%d"
        )

    prepared["run_date"] = prepared["run_date"].fillna(
        datetime.now().strftime("%Y-%m-%d")
    )

    # Older CSV rows may not have a timestamp.
    if "run_timestamp" not in prepared.columns:
        prepared["run_timestamp"] = prepared["run_date"]

    prepared["run_timestamp"] = prepared[
        "run_timestamp"
    ].fillna(
        prepared["run_date"]
    )

    # Convert date-only values into valid timestamps.
    prepared["run_timestamp"] = pd.to_datetime(
        prepared["run_timestamp"],
        errors="coerce",
    )

    fallback_timestamp = pd.to_datetime(
        prepared["run_date"],
        errors="coerce",
    )

    prepared["run_timestamp"] = prepared[
        "run_timestamp"
    ].fillna(
        fallback_timestamp
    )

    prepared["run_timestamp"] = prepared[
        "run_timestamp"
    ].fillna(
        pd.Timestamp.now()
    )

    prepared["run_timestamp"] = prepared[
        "run_timestamp"
    ].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Ensure scan_id exists.
    if "scan_id" not in prepared.columns:
        prepared["scan_id"] = ""

    for index in prepared.index:
        current_scan_id = prepared.at[
            index,
            "scan_id",
        ]

        if (
            pd.isna(current_scan_id)
            or not str(current_scan_id).strip()
        ):
            prepared.at[
                index,
                "scan_id",
            ] = (
                "legacy-"
                f"{index + 1:05d}"
            )

    # Ensure required text fields exist.
    required_text_fields = {
        "platform": "Unknown",
        "prompt_id": "legacy",
        "prompt": "Legacy imported result",
    }

    for column, fallback in required_text_fields.items():
        if column not in prepared.columns:
            prepared[column] = fallback

        prepared[column] = prepared[column].fillna(
            fallback
        )

        prepared[column] = prepared[column].replace(
            "",
            fallback,
        )

    return prepared


def migrate_csv_to_sqlite() -> None:
    """
    Copy the existing results.csv data into SQLite.
    """
    if not RESULTS_FILE.exists():
        print(
            f"No CSV file was found at "
            f"{RESULTS_FILE}."
        )
        return

    try:
        results = pd.read_csv(
            RESULTS_FILE,
        )
    except pd.errors.EmptyDataError:
        print(
            "The CSV file is empty. "
            "Nothing was migrated."
        )
        return

    if results.empty:
        print(
            "The CSV file contains no results."
        )
        return

    initialize_database()

    existing_count = get_result_count()

    if existing_count > 0:
        print(
            "The SQLite database already contains "
            f"{existing_count} results."
        )
        print(
            "Migration stopped to prevent duplicates."
        )
        return

    prepared_results = prepare_results(
        results
    )

    records = prepared_results.where(
        pd.notna(prepared_results),
        None,
    ).to_dict(
        orient="records",
    )

    migrated_count = save_results(
        records
    )

    print(
        f"Successfully migrated "
        f"{migrated_count} results."
    )

    print(
        "Database created at: "
        "data/ai_search.db"
    )


if __name__ == "__main__":
    migrate_csv_to_sqlite()