from yandex_tracker_client import TrackerClient
from enum import Enum
import argparse
import copy

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
        self._garbage_queue = "garbage"
    def create_project(self, project_name, queues, description, lead=None, start_date=None, end_date=None):
        create_params = dict(name = project_name, queues=queues, description = description, lead = lead, startDate=start_date, endDate = end_date)
        resp = self.projects.create(params=None, **create_params)
        return resp.id
    def delete_project(self, project_id):
        project = self.projects[project_id]
        if project:
            project.delete()
    def get_workflows(self):
        workflows = list(yandex_tracker.workflows.get_all())
        new_workflows = []
        for workflow in workflows:
            new_workflow = dict(name=workflow.name, id=workflow.id, steps=[])
            for step in workflow.steps:
                new_step = {}
                new_step['actions'] = []
                for action in step['actions']:
                    new_step['actions'].append(dict(id=action['id'], name=action['name']))
                new_workflow['steps'].append(new_step)
            new_workflows.append(new_workflow)
        return new_workflows
    def get_issue_types(self):
        issue_types = list(self.issue_types.get_all())
        new_issue_types = []
        for issue_type in issue_types:
            new_issue_type = dict(id=issue_type.id, key=issue_type.key, name=issue_type.name)
            new_issue_types.append(new_issue_type)
        return new_issue_types
    def get_resolutions(self):
        resolutions = list(yandex_tracker.resolutions.get_all())
        new_resolutions = []
        for resolution in resolutions:
            new_resolution = dict(id=resolution.id, key=resolution.key, name=resolution.name)
            new_resolutions.append(new_resolution)
        return new_resolutions
    def create_queue(self, queue_name, key, type, priority, lead, issueTypesConfig):
        data = dict(name=queue_name, key = key, defaultType=type, defaultPriority=priority, lead=lead, issueTypesConfig=issueTypesConfig)
        resp = self.queues.create(params=None, **data)
        return resp.id
    def _get_queue_id(self, key):
        for queue in self.queues:
            if queue.key == key:
                return queue
        return None
    def delete_queue(self, key):
        queue = self._get_queue_id(key)
        if queue:
            queue.delete()
    def get_issue_type_id(self, issue_name):
        for issue_type in self.issue_types:
            if issue_name == issue_type.name:
                return issue_type.id
        return None
    def create_task(self, task_name, project_id, task_type, queue_name, notes, start_data=None, end_date=None, assignee=None):
        data = dict(summary=task_name, type=task_type, queue=queue_name, description=notes, start=start_data, dueDate=end_date, assignee=assignee, project=project_id)
        resp = self.issues.create(params=None, **data)
        return resp.id
    def _get_task_id(self, task_name):
        for task in self.issues:
            if task.summary == task_name:
                return task.id
        return None
    def delete_task(self, task_id):
        task = self.issues[task_id]
        if task:
            data = {"project":None, "queue":self._garbage_queue}
            task.update(**data)
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
    issue_types = yandex_tracker.get_issue_types()
    resolutions = yandex_tracker.get_resolutions()
    queues = list(yandex_tracker.queues.get_all())
    
    print("Queues:")
    for queue in yandex_tracker.queues:
        print(queue.id)
        print(queue.key)
        print(queue.name)
        print(queue.lead)
    
    for priority in priorities:
        print(priority.id)
        print(priority.key)
        print(priority.name)
    '''
    print("Resolutions:")
    for resolution in resolutions:
        print(resolution)
    
    print("Issue types:")
    for issue_type in issue_types:
        print(issue_type)

    workflows = yandex_tracker.get_workflows()
    print("Modified Workflows:")
    for workflow in workflows:
        print(workflow['id'])
        print(workflow['name'])
        print('Steps:')
        for step in workflow['steps']:
            print(step)

    print("Users:")
    for user in users:
        print('')
        print(user.uid)
        print(user.login)
    
    queue_params = {}
    queue_params["queue_name"] = "fake_garbage"
    queue_params["key"] = "FAKEGARBAGEEE"
    queue_params["lead"] = "starovoitov-rep"
    queue_params["priority"] = "normal"
    queue_params["type"] = "task"
    issueTypesConfig = []
    resolutions_config = [res['key'] for res in resolutions]
    for issue_type in issue_types:
        cur_type_config = dict(issueType = issue_type['key'], workflow = "quickStartV2PresetWorkflow", resolutions = resolutions_config)
        issueTypesConfig.append(cur_type_config)
    queue_params["issueTypesConfig"] = issueTypesConfig
    yandex_tracker.create_queue(**queue_params)
    yandex_tracker.delete_queue(queue_params["key"])
    '''
    
    # task methods check
    task_params = {}
    task_params["task_name"]="Dummy Task"
    task_params["task_type"] = yandex_tracker.get_issue_type_id("Задача")
    task_params["queue_name"] = queues[0].key
    task_params["notes"] = "Just checking"
    #yandex_tracker.create_task(**task_params)
    #yandex_tracker.delete_task(task_params["task_name"])
    

