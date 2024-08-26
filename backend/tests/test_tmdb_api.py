import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

if __name__ == "__main__":
    init_tmdb()
    movies = [1730, 104871, 31414, 76819]
    info = [get_tmdb_data(movie) for movie in movies]
    print(info)