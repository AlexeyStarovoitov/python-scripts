from yandex_tracker_client import TrackerClient, exceptions
from yandex_tracker_client.collections import Issues 
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str)
arg_parser.add_argument('-org_id', dest='org_id', type=str)
arg_parser.add_argument('-csv_file', dest='csv_file', type=str, required=False)
arg_parser.add_argument('-dump_file', dest='dump_file', type=str, required=False)
arg_parser.add_argument('-lead', dest='lead', type=str, required=False)
arg_parser.add_argument('-cmd', dest='cmd', type=str, required=False)
args = arg_parser.parse_args()

yndx_tracker = TrackerClient(args.oauth_token, args.org_id)

task_keys = ["MYLIFE-851"]
project_name = "Финансы"
queue_key = 'PROFESSION'
queue = yndx_tracker.queues[queue_key]

def find_project(projects, project_name):
     for project in projects:
          if project.name == project_name:
               return project
     else:
          return None

project = find_project(yndx_tracker.projects, project_name)


def move_task_with_subtasks_to_queue_project(task, queue_key, project_id):
    try:
        if queue_key != None:
            task.move_to(queue_key)
    except exceptions.UnprocessableEntity:
         pass
    if project_id != None:
         data = {"project":project_id}
         task.update(**data)
    for link in task.links:
            if link.direction == "outward" and link.type.id == "subtask":
                 move_task_with_subtasks_to_queue_project(link.object, queue_key, project_id)

for task_key in task_keys:
    issue = yndx_tracker.issues[task_key]
    move_task_with_subtasks_to_queue_project(issue, queue_key, None)


#queue.delete()


print("Projects")
for project in yndx_tracker.projects:
    print(project.name)

 