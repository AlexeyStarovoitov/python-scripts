import requests
import json
from teamgantt import TeamGanttNode, TeamganttTree, TeamGanttNodeSchema, TaskType
from marshmallow import fields, Schema
from datetime import datetime, timedelta


def _generate_task_node_params(parent_id, layer_id, nodes_in_layer, task_type):
    params = {}
    node_id = nodes_in_layer+1
    params["task_id"] = f"{layer_id}.{node_id}"
    params["parent_id"] = parent_id
    params["task_type"] = task_type
    params["task_name"] = f"task_{params['task_id']}"
    now = datetime.now()
    delta = timedelta(days=layer_id+nodes_in_layer+1)
    params["start_date"] = now + delta
    params["end_date"] =  params["start_date"] + delta
    return params



tree = TeamganttTree("Fake project", project_id="1")
layers = 3
prev_layer_arr = []
nodes_per_parent = 2
for i in range(0,layers+1):
    cur_layer_arr = []
    #nodes_per_layer = nodes_per_parent**i
    if i == 0:
        prev_layer_arr.append(tree.get_root_node())
        continue
    cur_nodes_per_layer = 0
    for parent_node in prev_layer_arr:
        for j in range(0, nodes_per_parent):
            cur_node_params = _generate_task_node_params(parent_node.get_id(), i, cur_nodes_per_layer, TaskType.GROUP if i < layers else TaskType.TASK)
            cur_node = TeamGanttNode(**cur_node_params)
            cur_layer_arr.append(cur_node)
            tree.add_node(cur_node)
            cur_nodes_per_layer += 1

    prev_layer_arr = cur_layer_arr

schema = TeamGanttNodeSchema()
tree_dump = schema.dump(tree.get_root_node())
dump_file_path = "out_folder/dump_tree.json"
with open(dump_file_path, "w") as write_file:
    json.dump(tree_dump, write_file)
    write_file.close()

load_tree_json = None
with open(dump_file_path, "r") as read_file:
    load_tree_json = json.load(read_file)
    read_file.close()

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
pass

