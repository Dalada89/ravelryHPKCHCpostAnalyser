from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from database import courses, trackers, turn_ins


def initialise():
    courses.create_table()
    trackers.create_table()
    turn_ins.create_table()


def main():
    initialise()


if __name__ == '__main__':
    main()
