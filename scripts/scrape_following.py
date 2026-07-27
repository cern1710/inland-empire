"""Scrape the ratings CSVs of everyone a Letterboxd user follows.

Fetches the target user's following list, then runs the same per-user CSV
scrape used by scrape_user.py against each user in turn. Safe to
interrupt and re-run: usernames that already have a CSV in --out-dir are
skipped, and a failure on one user is logged and doesn't stop the rest.

Usage:
    python scripts/scrape_following.py cern1710
    python scripts/scrape_following.py cern1710 --out-dir data/following
"""

import argparse
import asyncio
import os

from inland_empire.utils import scrape_following, scrape_user_to_csv


def scrape_user(username: str, output_dir: str, error_log_path: str) -> None:
    try:
        scrape_user_to_csv(username, output_dir=output_dir)
    except Exception as e:
        print(f"{username}: FAILED - {e}")
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"{username}: {e}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "username", help="Letterboxd username whose followed users to scrape"
    )
    parser.add_argument(
        "--out-dir",
        help="directory to write each followed user's <username>.csv into "
        "(default: data/<username>_following)",
    )
    args = parser.parse_args()

    out_dir = args.out_dir or f"data/{args.username}_following"
    os.makedirs(out_dir, exist_ok=True)
    error_log_path = os.path.join(out_dir, "errors.log")

    # Check if targeted user's data exists and scrape if necessary
    if not os.path.exists(f"data/{args.username}.csv"):
        print(f"{args.username}'s CSV not found; scraping...")
        scrape_user(args.username, "data/", error_log_path)

    followed = asyncio.run(scrape_following(args.username))
    print(f"Found {len(followed)} followed_users for {args.username}.")

    for i, follow in enumerate(followed, start=1):
        csv_path = os.path.join(out_dir, f"{follow}.csv")
        if os.path.exists(csv_path):
            print(f"[{i}/{len(followed)}] {follow}: already scraped, skipping")
            continue

        print(f"[{i}/{len(followed)}] {follow}: scraping...")
        scrape_user(follow, out_dir, error_log_path)

    print(f"Done. CSVs written to {out_dir}/")


if __name__ == "__main__":
    main()
