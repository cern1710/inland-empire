"""Scrape a Letterboxd user's films.

Usage:
    python scripts/scrape_user.py cern1710
    python scripts/scrape_user.py cern1710 --to db
    python scripts/scrape_user.py cern1710 --out-dir data/followers
"""

import argparse

from inland_empire.utils import save_user_data_to_db, scrape_user_to_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("username", help="Letterboxd username, e.g. cern1710")
    parser.add_argument(
        "--to",
        choices=["csv", "db"],
        default="csv",
        help="where to write the results (default: csv)",
    )
    parser.add_argument(
        "--out-dir",
        default="data",
        help="directory to write the CSV into, when --to csv (default: data)",
    )
    args = parser.parse_args()

    if args.to == "db":
        save_user_data_to_db(args.username)
    else:
        scrape_user_to_csv(args.username, output_dir=args.out_dir)


if __name__ == "__main__":
    main()
