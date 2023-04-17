from yandex_tracker_client import TrackerClient
from yandex_tracker_client import exceptions
from enum import Enum
import argparse
import copy
import re

class TaskRelationType(Enum):
    PARENT_TASK_RELATION_TYPE = 2
    SUBTASK_RELATION_TYPE = 3

class TaskType(Enum):
    EPIC_TASK_TYPE = 1
    SIMPLE_TASK_TYPE = 2


class YandexTrackerClient(TrackerClient):
    def __init__(self, oath_token, org_id, lead_lastname):
        super(YandexTrackerClient, self).__init__(oath_token, org_id)
        self._default_user = self._get_default_user(lead_lastname)
        if self._default_user == None:
            raise Exception("Wrong lead lastname")
        self._garbage_queue = self._find_garbage_queue()
        if self._garbage_queue == None: 
            self._garbage_queue = self.create_queue(queue_name="garbage", lead = self._default_user)
    def _get_default_user(self, user_lastname):
        user_lastname = f"^{user_lastname}[a-z]*[1-9]*[-]*"
        for user in self.users:
            if re.search(user_lastname, user.login, re.IGNORECASE):
                return user.login
        else:
            return None
    def _find_garbage_queue(self):
        garbage_queue_key_pattern = 'garbage[a-z]*[1-9]*'
        for queue in self.queues:
            if re.search(garbage_queue_key_pattern, queue.key, re.IGNORECASE):
                return queue.key
        else:
            return None
    def create_project(self, project_name, queues, description=None, lead=None, start_date=None, end_date=None):
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
    def _generate_queue_key(self, queue_key_zero):
        queue_key = queue_key_zero.capitalize()
        queue_key = ''.join([i for i in queue_key if i.isalpha()])
        suffix = queue_key[-1]
        queue_key += suffix
        return queue_key
    def _get_default_workflow_id(self):
        _def_workflow_pattern = '^quickstart[a-z]*[1-9]*'
        for workflow in self.workflows:
            if re.search(_def_workflow_pattern, workflow.id, re.IGNORECASE):
                return workflow.id
        return None
    def _generate_issue_type_configs(self):
        def_workflow_id = self._get_default_workflow_id()
        issueTypesConfig = []
        resolutions_config = [res.key for res in self.resolutions]
        for issue_type in self.issue_types:
            cur_type_config = dict(issueType = issue_type.key, workflow = def_workflow_id, resolutions = resolutions_config)
            issueTypesConfig.append(cur_type_config)
        return issueTypesConfig
    def create_queue(self, queue_name, lead):
        queue_params = {}
        queue_params["name"] = queue_name
        queue_params["key"] = self._generate_queue_key(queue_name)
        queue_params["lead"] = lead if lead != None else self._default_user
        queue_params["defaultPriority"] = "normal"
        queue_params["defaultType"] = "task"
        queue_params["issueTypesConfig"] = self._generate_issue_type_configs()
        queue_was_created = False
        while queue_was_created == False:
            try:
                resp = self.queues.create(params=None, **queue_params)
                queue_was_created = True
            except exceptions.Conflict:
                queue_params["key"] = self._generate_queue_key(queue_params["key"])
        return resp.key   
    def delete_queue(self, key):
        queue = self.queues[key]
        queue.delete()
    def create_task(self, task_name, project_id, task_type, queue_name, notes, start_data=None, end_date=None, assignee=None):
        data = dict(summary=task_name, type=task_type, queue=queue_name, description=notes, start=start_data, dueDate=end_date, assignee=assignee, project=project_id)
        resp = self.issues.create(params=None, **data)
        return resp.id
    def get_task(self, task_key):
        return self.issues[task_key]
    def get_project(self, project_key):
        return self.projects[project_key]
    def delete_task(self, task_key):
        task = self.issues[task_key]
        if task:
            data = {"project":None}
            task.update(**data)
            task.move_to(self._garbage_queue)
    @staticmethod
    def _map_task_relation_type(relation_type_enum):
        _map_arr = {
            TaskRelationType.PARENT_TASK_RELATION_TYPE: "is parent task for",
            TaskRelationType.SUBTASK_RELATION_TYPE: "is subtask for",
        }
        for rel in _map_arr:
            if rel == relation_type_enum:
                return _map_arr[rel]
        else:
            return None
    @staticmethod
    def _find_link(links, link_task_key):
        for link in links:
            if link.object.key == link_task_key:
                return link.id
        else:
            return None
    def link_tasks(self, task_1_key, task_2_key, relations):
        task_1 = self.issues[task_1_key]
        relation_str = YandexTrackerClient._map_task_relation_type(relations)
        task_1.links.create(issue=task_2_key, relationship=relation_str)
    def unlink_tasks(self, task_1_key, task_2_key):
        task_1 = self.issues[task_1_key]
        link_id = YandexTrackerClient._find_link(task_1.links, task_2_key)
        if link_id:
            link = task_1.links[link_id]
            link.delete()
        
        

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str)
    arg_parser.add_argument('-org_id', dest='org_id', type=str)
    args = arg_parser.parse_args()

    yandex_tracker = YandexTrackerClient(oath_token=args.oauth_token, org_id=args.org_id, lead_lastname='starovoitov')
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
    queue_params["queue_name"] = "garbage"
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
    #task_params["task_type"] = yandex_tracker.get_issue_type_id("Задача")
    #task_params["queue_name"] = queues[0].key
    task_params["notes"] = "Just checking"
    #yandex_tracker.create_task(**task_params)
    #yandex_tracker.delete_task("MYLIFE-44")
    yandex_tracker.link_tasks("MYLIFE-45", "MYLIFE-46", TaskRelationType.PARENT_TASK_RELATION_TYPE)
    yandex_tracker.unlink_tasks("MYLIFE-45", "MYLIFE-46")

