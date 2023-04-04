from yandex_tracker_client import TrackerClient
from enum import Enum

class TaskRealtionType(Enum):
    DEPENDENT_TASK_RELATION_TYPE = 1
    PARENT_TASK_RELATION_TYPE = 2
    SUBTASK_RELATION_TYPE = 3

class TaskType(Enum):
    EPIC_TASK_TYPE = 1
    SIMPLE_TASK_TYPE = 2


class YandexTrackerClinet(TrackerClient):
    def __init__(self, oath_token, org_id):
        super(TrackerClient, self).__init__(oath_token, org_id)
    def create_queue(self, queue_name):
        pass
    def delete_queue(self, queue_name):
        pass
    def create_project(self, project_name):
        pass
    def delete_project(self, project_name):
        pass
    def create_task(self, task_name, task_type, queue_name, start_data, end_date, assignee, notes):
        pass
    def delete_task(self, task_name, task_id, queue_name):
        pass
    def link_tasks(self, queue, task_1, task_2, relations):
        pass
    def unlink_tasks(self, queue, task_1, task_2):
        pass