from yandex_tracker_client import TrackerClient, exceptions
from yandex_tracker_client.collections import Issues 
from datetime import datetime
import argparse


def find_project(projects, project_name):
     for project in projects:
          if project.name == project_name:
               return project
     else:
          return None

def find_status(statuses, status_key):
     for status in statuses:
          if status.key == status_key:
               return status
     else:
          return None


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




if __name__ == "__main__":

     arg_parser = argparse.ArgumentParser()
     arg_parser.add_argument('-oauth_token', dest='oauth_token', type=str)
     arg_parser.add_argument('-org_id', dest='org_id', type=str)
     arg_parser.add_argument('-csv_file', dest='csv_file', type=str, required=False)
     arg_parser.add_argument('-dump_file', dest='dump_file', type=str, required=False)
     arg_parser.add_argument('-lead', dest='lead', type=str, required=False)
     arg_parser.add_argument('-cmd', dest='cmd', type=str, required=False)
     args = arg_parser.parse_args()

     yndx_tracker = TrackerClient(args.oauth_token, args.org_id)
     closed_status = find_status(yndx_tracker.statuses, "closed")
     now = datetime.now()
     for res in yndx_tracker.resolutions:
          pass
     for task in yndx_tracker.issues:
          if not task.deadline:
               continue 
          deadline = datetime.fromisoformat(task.deadline)
          if now > deadline and task.status.key != closed_status.key:
               task.update(resolution="fixed")
               task.transitions['close'].execute()
               #data = {"status":closed_status.key}
               #task.update(**data)
               

 