from enum import Enum
from yandex_client import YandexTrackerClient, YandexTaskType, TaskRelationType
from teamgantt import TeamganttTree, TeamGanttConverter, TaskType
import argparse
import pandas as pd
from datetime import datetime


class Teamgantt2YandexTrackerConverter:
    def __init__(self, oath_token, org_id, lead_lastname, tree_csv=None, tree_dump=None):
        if (tree_csv and tree_dump) or (not tree_csv and not tree_dump):
            raise Exception("You should pass either csv or dump file of Teamgantt Tree")
        
        if tree_csv:    
            converter = TeamGanttConverter(tree_csv)
            self.converter.process()
            self._tg_tree = self.converter.get_tree()
        elif tree_dump:
            self._tg_tree = TeamganttTree.load_tree(args.dump_file)

        self.tracker = YandexTrackerClient(oath_token, org_id, lead_lastname)
        self._queue_name = lead_lastname+"personal"
        self._queue_name = self._queue_name[0:10]
        self._queue_key = "MYLIFE"
        self._lead = self.tracker.get_lead()
    def _convert(self, node, parent_key=None, parent_type=None):
        node_task_type = node.get_task_type()
        if node_task_type == TaskType.PROJECT:
            #self._queue_key = self.tracker.create_queue(queue_name = self._queue_name, lead = self._lead)
            dates = node.get_dates()
            (self._project_key, self.project_id) = self.tracker.create_project(project_name = node.get_name(), 
                                                                               queues=self._queue_key, 
                                                                               description= node.get_notes(), 
                                                                               lead=self._lead, 
                                                                               start_date=dates[0].isoformat(), end_date=dates[1].isoformat())
            node_task_key = self._project_key
        elif node_task_type == TaskType.TASK or node_task_type == TaskType.GROUP:
            dates = node.get_dates()
            task_type_enum = YandexTaskType.EPIC_TASK_TYPE if parent_type == TaskType.PROJECT else YandexTaskType.SIMPLE_TASK_TYPE
            node_task_key = self.tracker.create_task(task_name = node.get_name(), 
                                                                   project_id=self._project_key, 
                                                                   task_type_enum=task_type_enum, 
                                                                   queue_name=self._queue_key, 
                                                                   notes = node.get_notes(), 
                                                                   start_date=dates[0].isoformat(), 
                                                                   end_date=dates[1].isoformat(), assignee=self._lead)
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
    
    converter = Teamgantt2YandexTrackerConverter(args.oauth_token, args.org_id, args.lead, args.csv_file, args.dump_file)
    converter.process()

        
            


