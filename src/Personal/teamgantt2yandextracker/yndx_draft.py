from yandex_tracker_client import TrackerClient
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

garbage_queue_key = 'GARBAGEEEE'
garbage_queue = yndx_tracker.queues[garbage_queue_key]

for issue in yndx_tracker.issues:
    issue.move_to(garbage_queue_key)

garbage_queue.delete()
