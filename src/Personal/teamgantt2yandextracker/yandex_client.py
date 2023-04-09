from yandex_tracker_client import TrackerClient
from enum import Enum
import argparse

class TaskRealtionType(Enum):
    DEPENDENT_TASK_RELATION_TYPE = 1
    PARENT_TASK_RELATION_TYPE = 2
    SUBTASK_RELATION_TYPE = 3

class TaskType(Enum):
    EPIC_TASK_TYPE = 1
    SIMPLE_TASK_TYPE = 2


class YandexTrackerClinet(TrackerClient):
    def __init__(self, oath_token, org_id):
        super(YandexTrackerClinet, self).__init__(oath_token, org_id)
    def create_project(self, project_name, queues, description, lead=None, start_date=None, end_date=None):
        create_params = dict(name = project_name, queues=queues, description = description, lead = lead, startDate=start_date, endDate = end_date)
        resp = self.projects.create(params=None, **create_params)
        return resp.id
    def delete_project(self, project_id):
        project = self.projects[project_id]
        if project:
            project.delete()
    def create_queue(self, queue_name, key, type, priority, lead, issueTypesConfig):
        data = dict(name=queue_name, key = key, defaultType=type, defaultPriority=priority, lead=lead, issueTypesConfig=issueTypesConfig)
        resp = self.queues.create(params=None, **data)
        return resp.id
    def _get_queue_id(self, queue_name):
        for queue in self.queues:
            if queue.name == queue_name:
                return queue
        return None
    def delete_queue(self, queue_name):
        queue = self._get_queue_id(queue_name)
        if queue:
            queue.delete()
    def get_issue_type_id(self, issue_name):
        for issue_type in self.issue_types:
            if issue_name == issue_type.name:
                return issue_type.id
        return None
    def create_task(self, task_name, task_type, queue_name, notes, start_data=None, end_date=None, assignee=None):
        data = dict(summary=task_name, type=task_type, queue=queue_name, description=notes, start=start_data, dueDate=end_date, assignee=assignee)
        resp = self.issues.create(params=None, **data)
        return resp.id
    def _get_task_id(self, task_name):
        for task in self.issues:
            if task.summary == task_name:
                return task.id
        return None
    def delete_task(self, task_name):
        task = self.issues[self._get_task_id(task_name)]
        if task:
            task.delete()
    def link_tasks(self, task_1_name, task_2_name, relations):
        task_1 = self.issues[task_1_name]
        #task_2 = self.issues[task_2_name]
        #self.issues.link(task_1, task_2, relations)
        task_1.links.create(issue=task_2_name, relationship=relations)
    def unlink_tasks(self, task_1_name, task_2_name):
        task_1 = self.issues[task_1_name]
        task_2 = self.issues[task_2_name]
        link = task_1.links[task_2.key]
        link.delete()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str)
    arg_parser.add_argument('-org_id', dest='org_id', type=str)
    args = arg_parser.parse_args()

    yandex_tracker = YandexTrackerClinet(oath_token=args.oauth_token, org_id=args.org_id)
    for project in yandex_tracker.projects:
        print(project['name'])
    
    print(type(yandex_tracker.queues))
    print(dir(yandex_tracker.queues))
    for queue in yandex_tracker.queues:
        print(queue.key)

    for issue_type in yandex_tracker.issue_types:
        print(issue_type.id)
    # project methods check
    queues = list(yandex_tracker.queues.get_all())
    project_params = {}
    project_params["project_name"] = "Fake Project" 
    project_params["description"] = "Test of Yandex Tracker"
    project_params["queues"] = queues[0].key
    project_id = yandex_tracker.create_project(**project_params)
    yandex_tracker.delete_project(project_id)
    
    #queue methods check
    users = list(yandex_tracker.users.get_all())
    priorities = list(yandex_tracker.priorities.get_all())
    issue_types = list(yandex_tracker.issue_types.get_all())
    workflows = list(yandex_tracker.workflows.get_all())
    resolutions = list(yandex_tracker.resolutions.get_all())
    queue_params = {}
    queue_params["queue_name"] = "fake_garbage"
    queue_params["key"] = "fake"
    queue_params["lead"] = users[0].uid
    queue_params["priority"] = priorities[0].id
    queue_params["type"] = "task"
    issueTypesConfig = []
    for issue_type in issue_types:
        cur_type_config = dict(issueType = issue_type.key, workflow = workflows[0].id, resolutions = [res.key for res in resolutions])
        issueTypesConfig.append(cur_type_config)
    queue_params["issueTypesConfig"] = issueTypesConfig
    #queue_id = yandex_tracker.create_queue(**queue_params)
    yandex_tracker.delete_queue(queue_params["queue_name"])

    # task methods check
    task_params = {}
    task_params["task_name"]="Dummy Task"
    task_params["task_type"] = yandex_tracker.get_issue_type_id("Задача")
    task_params["queue_name"] = queues[0].key
    task_params["notes"] = "Just checking"
    #yandex_tracker.create_task(**task_params)
    #yandex_tracker.delete_task(task_params["task_name"])

