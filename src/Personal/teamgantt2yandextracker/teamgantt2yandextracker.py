from enum import Enum
from yandex_client import YandexTrackerClient, YandexTaskType, TaskRelationType
from teamgantt import TeamGanttNode, TeamganttTree, TeamGanttConverter, TaskType
from yandex_tracker_client.collections import Issues 
import argparse
import pandas as pd
from datetime import datetime


class Teamgantt2YandexTrackerConverter:
    def __init__(self, oath_token, org_id, lead_lastname, tree_csv=None, tree_dump=None):
        if (tree_csv and tree_dump) or (not tree_csv and not tree_dump):
            raise Exception("You should pass either csv or dump file of Teamgantt Tree")
        
        if tree_csv:    
            converter = TeamGanttConverter(tree_csv)
            converter.process()
            self._tg_tree = self.converter.get_tree()
        elif tree_dump:
            self._tg_tree = TeamganttTree.load_tree(args.dump_file)

        self.tracker = YandexTrackerClient(oath_token, org_id, lead_lastname)
        self._queue_name = lead_lastname+"personal"
        self._queue_name = self._queue_name[0:10]
        self._queue_key = "MYLIFE"
        self._lead = self.tracker.get_lead()
    @staticmethod
    def _get_dates(node):
        dates = node.get_dates()
        dates[0] = None if not dates[0] else dates[0].isoformat()
        dates[1] = None if not dates[1] else dates[1].isoformat()
        return dates
    def _get_project_key_id(self, project_name):
        for project in self.tracker.projects:
            if project.name == project_name:
                return (project.key, project.id)
        else:
            return None
    def _parent_task_link_is_valid(self, task, parent_name):
        for link in task.links:
            if link.direction == "inward" and link.type == "subtask" and link.object.summary == parent_name:
                return True
        else:
            return False
    def _task_is_already_in_project(self, node):
       parent_node = self._tg_tree.find_node(node.get_parent_id())
       task_type_enum = YandexTaskType.EPIC_TASK_TYPE if parent_node.get_task_type() == TaskType.PROJECT else YandexTaskType.SIMPLE_TASK_TYPE
       
       for task in self.tracker.issues:
           if task.summary == node.get_name and task.type == self.tracker.get_task_type_key(task_type_enum):
               if parent_node == None:
                   return task.key
               else:
                   if self._parent_task_link_is_valid(task, parent_node.get_name()) and self._task_is_already_in_project(parent_node):
                       return task.key
       else:
           return None
    def _convert(self, node, parent_key=None, parent_type=None):
        node_task_type = node.get_task_type()
        if node_task_type == TaskType.PROJECT:
            project_params = self._get_project_key_id(node.get_name())
            if project_params == None:
                dates = Teamgantt2YandexTrackerConverter._get_dates(node)
                (self._project_key, self.project_id) = self.tracker.create_project(project_name = node.get_name(), 
                                                                                queues=self._queue_key, 
                                                                                description= node.get_notes(), 
                                                                                lead=self._lead, 
                                                                                start_date=dates[0], end_date=dates[1])
            else:
                (self._project_key, self.project_id) = project_params
            node_task_key = self._project_key
        elif node_task_type == TaskType.TASK or node_task_type == TaskType.GROUP:
            node_task_key = self._task_is_already_in_project(node)
            if node_task_key == None:
                dates = Teamgantt2YandexTrackerConverter._get_dates(node)
                task_type_enum = YandexTaskType.EPIC_TASK_TYPE if parent_type == TaskType.PROJECT else YandexTaskType.SIMPLE_TASK_TYPE
                node_task_key = self.tracker.create_task(task_name = node.get_name(), 
                                                                    project_id=self._project_key, 
                                                                    task_type_enum=task_type_enum, 
                                                                    queue_name=self._queue_key, 
                                                                    notes = node.get_notes(), 
                                                                    start_date=dates[0], 
                                                                    end_date=dates[1], assignee=self._lead)
                if  parent_type == TaskType.GROUP:
                    self.tracker.link_tasks(parent_key, node_task_key, TaskRelationType.PARENT_TASK_RELATION_TYPE)
        
            node_children = node.get_children()
            if len(node_children) != 0:
                for child in node_children:
                    self._convert(child, node_task_key, node_task_type)
    def process(self):
        tree_root = self._tg_tree.get_root_node()
        self._convert(tree_root, None, None)


if __name__ == '__main__':
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str)
    arg_parser.add_argument('-org_id', dest='org_id', type=str)
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str, required=False)
    arg_parser.add_argument('-dump_file', dest='dump_file', type=str, required=False)
    arg_parser.add_argument('-lead', dest='lead', type=str)
    arg_parser.add_argument('-cmd', dest='cmd', type=str, required=False)


    args = arg_parser.parse_args()
    
    converter = Teamgantt2YandexTrackerConverter(args.oauth_token, args.org_id, args.lead, None, args.dump_file)
    converter.process()

        
            


