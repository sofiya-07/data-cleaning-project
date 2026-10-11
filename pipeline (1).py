"""
Data Processing Pipeline
Reads CSV data, cleans missing values, converts data types,
creates a processed output file, and logs pipeline activity.
"""
import csv
import json
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"

logging.basicConfig(
    filename=BASE_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_config():
    """Load settings from config.json; use safe defaults if unavailable."""
    defaults = {
        "input_file": "sample_input.csv",
        "output_file": "cleaned_output.csv",
        "missing_name": "Unknown",
        "missing_age": 0,
        "missing_city": "Unknown"
    }
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            defaults.update(json.load(file))
    except FileNotFoundError:
        logger.warning("config.json not found; using default settings")
    except json.JSONDecodeError:
        logger.warning("config.json is invalid; using default settings")
    return defaults


def to_int(value, default=0):
    """Convert a value to an integer, safely handling blanks/invalid text."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def process_data():
    config = load_config()
    input_path = BASE_DIR / config["input_file"]
    output_path = BASE_DIR / config["output_file"]

    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path.name}")

    cleaned_rows = []
    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            required = {"name", "age", "city"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise ValueError("CSV must contain these columns: name, age, city")

            for row_number, row in enumerate(reader, start=2):
                name = (row.get("name") or "").strip() or config["missing_name"]
                age = to_int((row.get("age") or "").strip(), config["missing_age"])
                city = (row.get("city") or "").strip() or config["missing_city"]

                cleaned_rows.append({"name": name, "age": age, "city": city})
                logger.info("Processed row %s", row_number)

        with open(output_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "age", "city"])
            writer.writeheader()
            writer.writerows(cleaned_rows)

        logger.info("Finished. %s rows written to %s", len(cleaned_rows), output_path.name)
        print(f"Success! Cleaned {len(cleaned_rows)} rows.")
        print(f"Output saved to: {output_path.name}")
        print("Preview:")
        for row in cleaned_rows:
            print(row)
        return cleaned_rows

    except (OSError, csv.Error, ValueError) as error:
        logger.exception("Pipeline failed: %s", error)
        raise


if __name__ == "__main__":
    process_data()
