from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from database import courses, trackers, submissions


def initialise():
    courses.create_table()
    trackers.create_table()
    submissions.create_table()


def main():
    initialise()


if __name__ == '__main__':
    main()
