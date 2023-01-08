import numpy as np
import pandas as pd
import argparse

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str)

    args = arg_parser.parse_args()
    team_gantt_db = pd.read_csv(args.csv_file)
    print(team_gantt_db.describe())