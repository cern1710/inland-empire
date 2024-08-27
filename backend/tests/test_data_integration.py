import sys
import os
import asyncio

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PARENT_DIR)

from utils import write_to_csv, save_user_data_to_db, get_user_movie_data

if __name__ == "__main__":
    username = "mscorsese"
    user_movie_data = asyncio.run(get_user_movie_data(username))
    write_to_csv(username, user_movie_data)