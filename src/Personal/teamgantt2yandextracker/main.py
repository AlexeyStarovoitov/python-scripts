
import numpy as np
import pandas as pd
import argparse
import teamgantt

def team_gantt_rename_columns(team_gantt_db):
    column_name_map = {
        "name": ['Name'],
        "type": ['Type'],
        "index": ["WBS #"] ,
        "start_date":["Start Date"],
        "end_date":["End Date"],
        "notes": ["notes"]
    }


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str)

    args = arg_parser.parse_args()
    team_gantt_db = pd.read_csv(args.csv_file)
    print(team_gantt_db.describe())
    print(team_gantt_db.info())
    print(team_gantt_db.axes[1])

    for i in team_gantt_db.index:
        print(team_gantt_db.iloc[i]['Resources'])