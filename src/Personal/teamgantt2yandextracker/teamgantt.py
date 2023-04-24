from pandas.api.types import is_object_dtype
import pandas as pd
import numpy as np
from numpy import nan
import re
import json
from enum import Enum
import datetime
import copy
import argparse
import pickle
from pathlib import Path
from marshmallow import fields, Schema, post_load, pre_dump, pre_load


class TaskType(Enum):
    NONE = 0
    PROJECT = 1
    GROUP = 2
    TASK = 4

class ColumnName(Enum):
    NONE = 0
    TASK_NAME = 1
    TASK_INDEX = 2
    TASK_TYPE = 3
    START_DATE = 4
    END_DATE = 5
    ASSIGNEE = 6
    NOTES = 7


def _object_is_invalid(obj):
    return obj == nan or not obj or obj=="nan" or obj == "null" or obj == "None" or obj == "NaT" or obj == pd.Timestamp('NaT').to_pydatetime()


class TeamganttLoader:
    def __init__(self, teamgantt_db, *args, **kwargs):
        self._teamgantt_db = teamgantt_db
    def _entry_is_mapped(self, entry, templates):
        for template in templates:
            if re.search(template, entry, re.IGNORECASE):
                return True
        return False
    def _map_column_names(self):
        map_arr = {
            ColumnName.TASK_NAME: ['^name[a-z]*[1-9]*'],
            ColumnName.TASK_TYPE: ['^type[a-z]*[1-9]*'],
            ColumnName.TASK_INDEX: ['^index[a-z]*[1-9]*', "WBS #[a-z]*[1-9]*"],
            ColumnName.START_DATE:["^start date[a-z]*[1-9]*"],
            ColumnName.END_DATE:["^end date[a-z]*[1-9]*"],
            ColumnName.NOTES: ["^notes[a-z]*[1-9]*"],
            ColumnName.ASSIGNEE: ["^resources[a-z]*[1-9]*"],
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
    def _convert_task_type(self, type_column):
        task_type_map_dict = {
            TaskType.PROJECT: ['^project[a-z]*[1-9]*'],
            TaskType.GROUP: ['^group[a-z]*[1-9]*', '^subgroup[a-z]*[1-9]*'],
            TaskType.TASK: ['^task[a-z]*[1-9]*', '^milestone[a-z]*[1-9]*']
        }
        for i in type_column.index:
            cur_type = type_column.iloc[i]
            for key,value in task_type_map_dict.items():
                if(self._entry_is_mapped(cur_type, value)):
                    type_column.iloc[i] = key
                    break
            else:
                print(cur_type + '\n')   
        #type_column.astype(TaskType)
        return type_column
        #type_column.astype(TaskType)    
    def _revise_types(self):
        _teamgantt_db = self._teamgantt_db
        for column in _teamgantt_db.columns:
            if is_object_dtype(_teamgantt_db[column]):
                if column in [ColumnName.START_DATE, ColumnName.END_DATE]:
                    _teamgantt_db[column] = pd.to_datetime(_teamgantt_db[column])
                elif column in [ColumnName.TASK_TYPE]:
                    return_column = self._convert_task_type(type_column = _teamgantt_db[column].copy(deep = True))
                    _teamgantt_db.loc[:, column] = return_column
                else:
                     _teamgantt_db[column] = _teamgantt_db[column].astype(str)
    def process_database(self):
        self._map_column_names()
        self._revise_types()
    def get_database(self):
        return self._teamgantt_db
    def get_project_entry(self):
        project_entry = self._teamgantt_db[self._teamgantt_db[ColumnName.TASK_TYPE] == TaskType.PROJECT].iloc[0, :]
        for i in self._teamgantt_db.index.values:
            if list(project_entry.values) == list(self._teamgantt_db.iloc[i, :].values):
                break
        project_entry_index = i
        return [project_entry, project_entry_index]

class TeamGanttNode:
    def __init__(self, task_name, task_id, task_type, start_date=None, end_date=None, notes=None, assignee=None, parent_id = None):
        self._task_name = task_name
        self._task_id = task_id
        self._task_type = task_type

        self._start_date = None if _object_is_invalid(start_date) else start_date
        self._end_date = None if _object_is_invalid(end_date) else end_date 
        self._notes = None if _object_is_invalid(notes) else notes
        self._assignee = None if _object_is_invalid(assignee) else assignee
        self._parent_id = None if _object_is_invalid(parent_id) else parent_id 
        
        '''
        self._start_date = start_date
        self._end_date = end_date
        self._notes = notes
        self._assignee = assignee
        self._parent_id = parent_id 
        '''
        self._children = []
        #print(f'Creating {self._task_name} node')
    def __del__(self):
        pass
        #print(f'Destroying {self._task_name} node')
    def get_id(self):
        return self._task_id
    def set_id(self, task_id):
        self._task_id = task_id
    def get_name(self):
        return self._task_name
    def set_name(self, task_name):
        self._task_name = task_name
    def get_parent_id(self):
        return self._parent_id
    def set_parent_id(self, parent_id):
        self._parent_id = parent_id
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
        pass
    def remove_child(self, node):
        if node in self._children: self._children.remove(node)
    def find_child(self, child_id):
        child = None
        if(self._task_id == child_id):
            return self
        for child in self._children:
            if(child.get_id() == child_id):
                return child
        else:
             for child in self._children:
                res_child = child.find_child(child_id)
                if res_child != None:
                    return res_child
        return None
    def get_children(self):
        return self._children

def date_validator(date):
        if date == None:
            print(date)
        return True

def name_validator(name):
        print(name)
        return True

class TeamGanttNodeSchema(Schema):
    _task_name = fields.Str()
    _task_id = fields.Str()
    _task_type = fields.Enum(TaskType)
    _start_date = fields.DateTime(format= "iso", allow_none = True)
    _end_date = fields.DateTime(format= "iso", allow_none = True)
    _notes = fields.Str(allow_none = True)
    _assignee = fields.Str(allow_none = True)
    _parent_id = fields.Str(allow_none = True)
    _children = fields.Nested("self", many=True)
    @staticmethod
    def get_node_parameters(data):
        node_par = {}
        for (key,val) in data.items():
            if key == "_children":
                continue
            new_key = key.lstrip('_')
            node_par[new_key] = val
        return node_par
    @pre_load
    def _pre_proc(self, data, **kwargs):
        if data['_start_date'] == "NaT":
            data['_start_date'] = None
        if data['_end_date'] == "NaT":
            data['_end_date'] = None
        return data
    @post_load
    def create_node(self, data, **kwargs):
        node_par = TeamGanttNodeSchema.get_node_parameters(data)
        node = TeamGanttNode(task_name=node_par["task_name"], 
                             task_id = node_par["task_id"], 
                             task_type = node_par["task_type"],
                             start_date = node_par["start_date"],
                             end_date = node_par["end_date"],
                             notes = node_par["notes"],
                             assignee = node_par["assignee"],
                             parent_id = node_par["parent_id"])
        load_children = data['_children']
        if len(load_children) != 0:
            for load_child in load_children:
                node.add_child(load_child)
        return node


class TeamganttTree:
    def __init__(self, projectname, project_id, start_date=None, end_date=None, notes=None, assignee=None):
        self._root = TeamGanttNode(projectname, project_id, TaskType.PROJECT, start_date=start_date, end_date=end_date, notes=notes, assignee=assignee)
    def get_root_node(self):
        return self._root
    def add_node(self, node):
        #print(f"node: {node.get_name()}")
        #print(f"parent_node: {node.get_parent_name()}")
        if node.get_parent_id() == None:
            self._root.add_child(node)
        else:
            parent_node = self._root.find_child(node.get_parent_id())
            if(parent_node != None):
                #print(f"found parent node: {parent_node.get_name()}")
                parent_node.add_child(node)
                pass
    def remove_node(self, node_id):
        node = self._root.find_child(node_id)
        if node == None:
            return
        parent_node = self._root.find_child(node.get_parent_id())
        if(parent_node == None):
            self._root.remove_child(node)
        else:
            parent_node.remove_child(node)
    def move_node(self, node_id, newparent_id):
        node = self._root.find_child(node_id)
        if node == None:
            return
        new_parent_node = self._root.find_child(newparent_id)
        if new_parent_node == None:
            return
        old_parent_node = self._root.find_child(node.get_parent_id())
        if(old_parent_node != None):
            old_parent_node.remove_child(node)

        new_parent_node.add_child(node)
    def _print_node(self, node, file, indent_symbol_num):
        indent_string = indent_symbol_num*'\t'
        link_symbol = f'{indent_string}|\n{indent_string}---'
        if file != None:
            file.write(f'{link_symbol}{node.get_name()}\n')
        else:
            print(f'{link_symbol}{node.get_name()}')
        node_children = node.get_children()
        if len(node_children) == 0:
            return
        for child in node_children:
            self._print_node(child, file, indent_symbol_num+1)
    def print_tree(self, file_path):
        abs_file_path = str(Path(file_path).resolve())
        with open(abs_file_path, "w") as file:
            self._print_node(self._root, file, 0)
            file.close()
    def _print_node2(self, node):
        print(f'{node.get_name()}')
        node_children = node.get_children()
        if len(node_children) != 0:
            print(f'{node.get_name()} children:')
            for child in node_children:
                self._print_node2(child)
    def print_tree2(self):
        self._print_node2(self._root)
    def dump_tree(self, dump_file_path):
        abs_dump_file_path = str(Path(dump_file_path).resolve())
        schema = TeamGanttNodeSchema()
        tree_dump = schema.dump(self._root)
        with open(abs_dump_file_path, "w") as write_file:
            json.dump(tree_dump, write_file)
            write_file.close()
    
    @staticmethod
    def load_tree(load_file_path):
        abs_load_file_path = str(Path(load_file_path).resolve())
        load_tree_json = None
        with open(abs_load_file_path, "r") as read_file:
            load_tree_json = json.load(read_file)
            read_file.close()
        schema = TeamGanttNodeSchema()
        load_tree_root = schema.load(data=load_tree_json)
        dates = load_tree_root.get_dates()
        load_tree = TeamganttTree(projectname = load_tree_root.get_name(),
                                project_id = load_tree_root.get_id(), 
                                start_date=dates[0], 
                                end_date = dates[1],
                                notes = load_tree_root.get_notes(),
                                assignee=load_tree_root.get_assignee())
        children = load_tree_root.get_children()
        for child in children:
            load_tree.add_node(child)
        return load_tree

        
# Pandas Dataframe to Tree
class TeamGanttConverter:
    def __init__(self, team_gantt_db_csv):
        team_gantt_db = pd.read_csv(team_gantt_db_csv)
        self._teamgantt_loader = TeamganttLoader(team_gantt_db)
        self._dump_file = "C:\\Users\\Алексей\\python-scripts\\out\\dump_tree.json"
    def _init_tree(self):
        project_entry, project_entry_index = self._teamgantt_loader.get_project_entry()
        if project_entry.empty:
            raise Exception('There is no project info in user provided dataframe')
        
        self._teamgantt_tree = TeamganttTree(project_entry[ColumnName.TASK_NAME], 
                                             project_entry[ColumnName.TASK_INDEX], 
                                             project_entry[ColumnName.START_DATE], 
                                             project_entry[ColumnName.END_DATE],
                                             project_entry[ColumnName.NOTES],
                                             project_entry[ColumnName.ASSIGNEE])
        '''
        self._teamgantt_tree = TeamganttTree(project_entry[ColumnName.TASK_NAME], 
                                             project_entry[ColumnName.TASK_INDEX])
        '''
    def _is_child_parent_relation(self, child_entry, parent_entry):
        child_index = child_entry[ColumnName.TASK_INDEX]
        parent_index = parent_entry[ColumnName.TASK_INDEX]
        if parent_index.rfind(".") != (len(parent_index)-1):
            parent_index = parent_index + "."
        res = child_index.find(parent_index) == 0 and (len(child_index.split('.')) - len(parent_index.split('.')) == 0)
        return res
    def _build_tree(self, parent_index):
        teamgantt_db = self._teamgantt_db
        parent_entry = teamgantt_db.iloc[parent_index, :]
        cur_entry_index = parent_index+1
        while cur_entry_index < len(teamgantt_db):
            cur_entry = teamgantt_db.iloc[cur_entry_index, :]
            if cur_entry[ColumnName.TASK_TYPE] == TaskType.PROJECT or self._is_child_parent_relation(cur_entry, parent_entry) != True:
                cur_entry_index += 1
                continue
            #print(cur_entry[ColumnName.TASK_TYPE])
            for i in cur_entry.index:
                if i not in [ColumnName.TASK_NAME, ColumnName.TASK_INDEX, ColumnName.TASK_TYPE]:
                    continue
                if _object_is_invalid(cur_entry[i]):
                    raise Exception(f"{i} is empty")
                if i == ColumnName.TASK_INDEX and _object_is_invalid(parent_entry[i]):
                    raise Exception(f"{i} is empty")
            cur_entry_node = TeamGanttNode(cur_entry[ColumnName.TASK_NAME],
                                           cur_entry[ColumnName.TASK_INDEX], 
                                           cur_entry[ColumnName.TASK_TYPE], 
                                           cur_entry[ColumnName.START_DATE], 
                                           cur_entry[ColumnName.END_DATE],
                                           cur_entry[ColumnName.NOTES],
                                           cur_entry[ColumnName.ASSIGNEE],
                                           parent_entry[ColumnName.TASK_INDEX])
            
            '''
            cur_entry_node = TeamGanttNode(task_name = cur_entry[ColumnName.TASK_NAME],
                                           task_id = cur_entry[ColumnName.TASK_INDEX], 
                                           task_type = cur_entry[ColumnName.TASK_TYPE], 
                                           parent_id = parent_entry[ColumnName.TASK_INDEX])
            '''
            self._teamgantt_tree.add_node(cur_entry_node)
            if cur_entry[ColumnName.TASK_TYPE] == TaskType.GROUP:
                self._build_tree(cur_entry_index)
            teamgantt_db.drop(index = cur_entry.name, inplace=True, axis = 0)
            #self._teamgantt_tree.dump_tree(self._dump_file)
    def process(self):
        self._teamgantt_loader.process_database()
        self._init_tree()
        project_entry, project_entry_index = self._teamgantt_loader.get_project_entry()
        self._teamgantt_db = self._teamgantt_loader.get_database()
        self._teamgantt_db = self._teamgantt_db.copy(deep=True)
        self._build_tree(project_entry_index)
    def get_tree_root(self):
        return self._teamgantt_tree.get_root_node()
    def get_tree(self):
        return self._teamgantt_tree
    def print_tree(self, file_path):
        return self._teamgantt_tree.print_tree(file_path)
    def dump_tree(self, file_path):
        return self._teamgantt_tree.dump_tree(file_path)
   
        

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-cmd', dest='cmd', type=str)
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str)
    arg_parser.add_argument('-dump_file', dest='dump_file', type=str)
    arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str, required=False)
    arg_parser.add_argument('-org_id', dest='org_id', type=str, required=False)
    arg_parser.add_argument('-lead', dest='lead', type=str, required=False)
    
    args = arg_parser.parse_args()
    cmd = args.cmd
    if cmd == 'csv2tree':
        abs_csv_file_path = str(Path(args.csv_file).resolve())
        tmgconverter = TeamGanttConverter(abs_csv_file_path)
        tmgconverter.process()
        dump_file = args.dump_file
        tmgconverter.dump_tree(dump_file)
    elif cmd == 'dump2tree':
        team_gantt_tree = TeamganttTree.load_tree(args.dump_file)
        pass
        #team_gantt_tree.print_tree(args.out_file)
        