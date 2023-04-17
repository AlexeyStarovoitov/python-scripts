from enum import Enum
from yandex_client import YandexTrackerClient, TaskRelationType
from teamgantt import TeamGanttConverter, TaskType
import argparse
import pandas as pd

class ParentType(Enum):
    PROJECT_PARENT_TYPE = 2
    TASK_PARENT_TYPE = 3

class Teamgantt2YandexTrackerConverter(TeamGanttConverter, YandexTrackerClient):
    def __init__(self, team_gantt_db, oath_token, org_id, lead_lastname):
        super(Teamgantt2YandexTrackerConverter, self).__init__(team_gantt_db)
        super(TeamGanttConverter, self).__init__(oath_token, org_id, lead_lastname)
    def _convert(self, node, parent_key, parent_type):
        if node.get_type() == TaskType.PROJECT:
            self._queue_name = node.get_name()
            self._queue_key = super(TeamGanttConverter, self).create_queue(queue_name = self._queue_name, lead = self._default_user)
            dates = node.get_dates()
            self._project_key = task_key = super(TeamGanttConverter, self).create_project(project_name = node.get_name(), 
                                                                               queues=self._queue_key, 
                                                                               description= node.get_notes(), 
                                                                               lead=self._default_user, 
                                                                               start_date=dates[0], end_date=dates[1])
            task_type = ParentType.PROJECT_PARENT_TYPE
            
        elif node.get_type() == TaskType.TASK:
            dates = node.get_dates()
            task_key = super(TeamGanttConverter, self).create_task(task_name = node.get_name(), 
                                                                   project_id=self._project_key, 
                                                                   task_type="task", 
                                                                   queue_name=self._queue_key, 
                                                                   notes = node.get_notes(), 
                                                                   start_data=dates[0], 
                                                                   end_date=dates[1], assignee=None)
            task_type = ParentType.TASK_PARENT_TYPE
            if parent_type == ParentType.TASK_PARENT_TYPE:
                super(TeamGanttConverter, self).link_tasks(parent_key, task_key, TaskRelationType.PARENT_TASK_RELATION_TYPE)
        
        node_children = node.get_children()
        if len(node_children) != 0:
            for child in node_children:
                self._convert(child, task_key, task_type)

    def process(self):
        super(Teamgantt2YandexTrackerConverter, self).process()
        tree_root = super(Teamgantt2YandexTrackerConverter, self).get_tree_root()
        self._convert(tree_root, None, TaskType.PROJECT)


if __name__ == '__main__':
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str)
    arg_parser.add_argument('-org_id', dest='org_id', type=str)
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str)
    arg_parser.add_argument('-lead', dest='lead', type=str)


    args = arg_parser.parse_args()
    
    team_gantt_db = pd.read_csv(args.csv_file)
    converter = Teamgantt2YandexTrackerConverter(team_gantt_db, args.oauth_token, args.org_id, lead_lastname=args.lead)
    converter.process()

        
            


