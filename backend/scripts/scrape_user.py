"""Scrape a Letterboxd user's films.

Usage:
    python scripts/scrape_user.py cern1710
    python scripts/scrape_user.py cern1710 --to db
"""

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import save_user_data_to_db, scrape_user_to_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("username", help="Letterboxd username, e.g. cern1710")
    parser.add_argument(
        "--to",
        choices=["csv", "db"],
        default="csv",
        help="where to write the results (default: csv)",
    )
    args = parser.parse_args()

    if args.to == "db":
        save_user_data_to_db(args.username)
    else:
        scrape_user_to_csv(args.username)


if __name__ == "__main__":
    main()
