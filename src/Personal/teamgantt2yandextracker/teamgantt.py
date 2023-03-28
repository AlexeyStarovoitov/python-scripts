from pandas.api.types import is_object_dtype
import pandas as pd
import numpy as np
import re
from enum import Enum
import datetime
import copy
import argparse

class TaskType(Enum):
    NONE = 0
    PROJECT = 1
    GROUP = 2
    SUBGROUP = 3
    TASK = 4


class TeamGanttNode:
    _task_name = None
    _task_type = TaskType.NONE
    _start_date = None
    _end_date = None
    _parent_name = None 
    _notes = None
    _assignee = None
    _children = []
    def __init__(self, task_name, task_type, start_date=None, end_date=None, notes=None, assignee=None, parent_name = None):
        self._task_name = task_name
        self._task_type = task_type
        self._start_date = start_date
        self._end_date = end_date
        self._notes = notes
        self._assignee = assignee
        self._parent_name = parent_name
    
    def get_name(self):
        return self._task_name
    def set_name(self, task_name):
        self._task_name = task_name
    def get_parent_name(self):
        return self._parent_name
    def set_parent_name(self, parent_name):
        self._parent_name = parent_name
    def get_notes(self):
        return self._notes
    def set_notes(self, notes):
        self._notes = notes
    def get_task_type(self):
        return self._task_type
    def set_task_type(self, task_type):
        self._task_type = task_type
    def get_assignee(self):
        return self._assignee
    def set_assignee(self, assignee):
        self._assignee = assignee
    def set_dates(self, start_date=None, end_date=None):
        if start_date != None:
            self._start_date = start_date
        if end_date != None:
            self._end_date = end_date
    def get_dates(self):
        return [self._start_date, self._end_date]
    def add_child(self, node):
        self._children.append(node)
    def remove_child(self, node):
        if node in self._children: self._children.remove(node)
    def find_child(self, child_name):
        child = None
        if(self._task_name == child_name):
            return self
        for child in self._children:
            if(child.get_name() == child_name):
                return child
        else:
             for child in self._children:
                res_child = child.find_child(child_name)
                if res_child:
                    return res_child
        return None
    


class TeamganttTree:
    _root = None
    def __init__(self, projectname, start_date=None, end_date=None, notes=None, assignee=None):
        self._root = TeamGanttNode(projectname, TaskType.PROJECT, start_date=start_date, end_date=end_date, notes=notes, assignee=assignee)
    def _find_node(self, node_name):
        return self._root.find_child(node_name)
    def add_node(self, node):
        if node.get_parent_name() == None:
            self._root.add_child(node)
        else:
            parent_node = self._root.find_child(node.get_parent_name())
            if(parent_node != None):
                parent_node.add_child(node)
    def remove_node(self, node_name):
        node = self._root.find_child(node_name)
        if node == None:
            return
        parent_node = self._root.find_child(node.get_parent_name())
        if(parent_node == None):
            self._root.remove_child(node)
        else:
            parent_node._root.remove_child(node)
    def move_node(self, node_name, newparent_name):
        node = self._root.find_child(node_name)
        if node == None:
            return
        new_parent_node = self._root.find_child(newparent_name)
        if new_parent_node == None:
            return
        if node.get_parent_name() == None:
            self._root.remove_child(node)
        else:
            old_parent_node = self._root.find_child(node.get_parent_name())
            if(old_parent_node != None):
                old_parent_node.remove_child(node)

        new_parent_node.add_child(node)
    
# Pandas Dataframe to Tree
class TeamGanttConverter:
    pass

class TeamganttLoader:
    _teamgantt_db = None
    def __init__(self, teamgantt_db, *args, **kwargs):
        self._teamgantt_db = teamgantt_db
    def _entry_is_mapped(self, entry, templates):
        for template in templates:
            if re.search(template, entry, re.IGNORECASE):
                return True
        return False
    def _map_column_names(self):
        map_arr = {
            "name": ['^name[a-z]*[1-9]*'],
            "type": ['^type[a-z]*[1-9]*'],
            "index": ['^index[a-z]*[1-9]*', "WBS #[a-z]*[1-9]*"],
            "start_date":["^start date[a-z]*[1-9]*"],
            "end_date":["^end date[a-z]*[1-9]*"],
            "notes": ["^notes[a-z]*[1-9]*"],
            "assignee": ["^resources[a-z]*[1-9]*"],
        }
        _teamgantt_db = self._teamgantt_db.copy()
        columns = list(_teamgantt_db.columns)
        for column in columns:
            for key,value in map_arr.items():
                if(self._entry_is_mapped(column, value)):
                    _teamgantt_db.rename(columns={column:key}, inplace=True)
                    break
            else:
                _teamgantt_db.drop(column, inplace=True, axis = 1)
        
        self._teamgantt_db = _teamgantt_db
    def _revise_types(self):
        _teamgantt_db = self._teamgantt_db.copy()
        for column in _teamgantt_db.columns:
            if is_object_dtype(_teamgantt_db[column]):
                if column in ["start_date", "end_date"]:
                    _teamgantt_db[column] = pd.to_datetime(_teamgantt_db[column])
                else:
                     _teamgantt_db[column] = _teamgantt_db[column].astype(str)
    def process_database(self):
        self._map_column_names()
        self._revise_types()
    def get_database(self):
        return self._teamgantt_db


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str)

    args = arg_parser.parse_args()
    team_gantt_db = pd.read_csv(args.csv_file)
    print(team_gantt_db.describe())
    print(team_gantt_db.info())
    print(team_gantt_db.axes[1])

    tmgloader = TeamganttLoader(team_gantt_db)
    tmgloader.process_database()
    team_gantt_db = tmgloader.get_database()
    print(team_gantt_db.describe())
    print(team_gantt_db.info())
    print(team_gantt_db.axes[1])
    print(team_gantt_db)