from pandas.api.types import is_object_dtype
import pandas as pd
import numpy as np
import re
from enum import Enum
import datetime
import copy

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
    _parent = None 
    _notes = None
    _assignee = None
    _children = []
    def __init__(self, task_name, task_type, start_date=None, end_date=None, notes=None, assignee=None, parent = None):
        self._task_name = None
        self._task_type = task_type
        self._start_date = start_date
        self._end_date = end_date
        self._notes = notes
        self._assignee = assignee
        self._parent = parent
    def add_child(self, node):
        self._children.append(node)
    def remove_child(self, node):
        if node in self._children: self._children.remove(node)
    def find_child(self, child_name):
        return_child = None
        if(self._task_name == child_name):
            return self
        for return_child in self._children:
            if(return_child.get_name() == child_name):
                return copy.deepcopy(return_child)
        else:
             for child in self._children:
                return_child = child.find_child(child_name)
                if return_child:
                    return copy.deepcopy(return_child)
        return None
    def pop_child(self):
        node = self._children.pop()
        return node
    def get_children(self):
        children = copy.deepcopy(self.get_children)
        return children
    def get_name(self):
        return self._task_name
    def get_parent(self):
        return self._parent


class TeamganttTree:
    _root = None
    def __init__(self, projectname, start_date=None, end_date=None, notes=None, assignee=None):
        self._root = TeamGanttNode(projectname, TaskType.PROJECT, start_date=start_date, end_date=end_date, notes=notes, assignee=assignee)
    def _find_node(self, node_name):
        return self._root.find_child(node_name)
    def add_node(self, node, parent_name):
        if parent_name == None:
            self._root.add_child(node)
        else:
            parent_node = self._root.find_child(parent_name)
            if(parent_node != None):
                parent_node.add_child(node)
    def remove_node(self, node_name):
        node = self._root.find_child(node_name)
        parent = node.get_parent()
        parent.remove_child(node)
    def move_node(self,node_name, newparent_name):
        node = self._root.find_child(node_name)
        oldparent = node.get_parent()
        oldparent.remove_child(node)
        newparent = self._root.find_child(node_name)
        newparent.add_child(node)
    
# Pandas Dataframe to Tree
class TeamGanttConverter:
    pass

class TeamganttLoader:
    _teamgantt_db = None
    def __init__(teamgantt_db, *args, **kwargs):
        self._teamgantt_db = teamgantt_db
    def _entry_is_mapped(entry, *templates):
        results = [lambda entry, template: re.search(template.upper(), entry.upper(), re.IGNORECASE) != None  for template in templates]
        return True in results
    def _map_column_names(self):
        map_arr = {
            "name": ['^name[a-z]*[1-9]*'],
            "type": ['^type[a-z]*[1-9]*'],
            "index": ['^index[a-z]*[1-9]*', "WBS #[a-z]*[1-9]*"],
            "start_date":["^start date[a-z]*[1-9]*"],
            "end_date":["^end date[a-z]*[1-9]*"],
            "notes": ["^notes[a-z]*[1-9]*"]
        }
        _teamgantt_db = self._teamgantt_db.copy()
        for column in _teamgantt_db.columns:
            for key,value in map_arr:
                if(self._entry_is_mapped(column, *value)):
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
