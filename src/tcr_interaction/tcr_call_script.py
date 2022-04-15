# coding=utf8
'''
Created on 01.02.2022
@author: starovoitov
@websocket package: websocket-client
'''

import websocket
import json
import argparse
import time
import string

def ws_wait_for_reply(ws=None, method=None, event=None):
    if not ws or (not method and not event) or (method and event):
        return -1
    reply_received = 0
    while not reply_received:
        result = json.loads(ws.recv())
        print(json.dumps(result))
        if event != None:
            if "event" in result and result["event"] == event:
                reply_received = 1
        else:
            if result["method"] == method:
                reply_received = 1
    return result

if __name__ =='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-room_ip", dest = "room_ip", type = str)
    parser.add_argument("-room_port", dest="room_port", type=str)
    parser.add_argument("-room_pin", dest="room_pin", type=str)
    parser.add_argument("-peerid", dest="peerid", type=str)
    parser.add_argument("-ndi_channel_type", dest="ndi_channel_type", type=str)
    parser.add_argument("-call_type", dest="call_type", type=str)
                    
    args = parser.parse_args()
    room_ip = args.room_ip
    room_port = args.room_port
    room_pin = args.room_pin
    peerid = args.peerid
    ndi_channel_type = args.ndi_channel_type
    call_type = args.call_type if args.call_type != None else "outgoing"

    uri = f"ws://{room_ip}:{room_port}"
    ws = websocket.WebSocket()
    ws.connect(uri)

   #authorization
    if room_pin == None:
        auth_cmd = { "method" : "auth",
                     "type" : "unsecured"
                    }
    else:
        auth_cmd = {
            "method" : "auth",
            "type" : "secured",
            "credentials": f"{room_pin}"
                    }
    ws.send(json.dumps(auth_cmd))
    result = ws_wait_for_reply(ws, method="auth", event=None)
    print(json.dumps(result))

    #turn on NDI Server
    command = {
            "method": "setNDIMediaSenderActiveStatus",
            "active": True
            }

    ws.send(json.dumps(command))
    result = ws_wait_for_reply(ws, method="setNDIMediaSenderActiveStatus", event=None)
    print(json.dumps(result))

    # make a call
    if call_type == "outgoing":
        command = {
            "method": "call",
            "peerId": f"{peerid}"
        }

    ws.send(json.dumps(command))
    result = json.loads(ws.recv())

    result = ws_wait_for_reply(ws, method=None, event="conferenceCreated")
    print(json.dumps(result))

    if ndi_channel_type == "peer":
        participants=[]
        while len(participants)==0:
            command = {
                "method": "getConferenceParticipants"
            }
            ws.send(json.dumps(command))
            result = ws_wait_for_reply(ws, method="getConferenceParticipants", event=None)
            print(json.dumps(result))
            participants = result["participants"]

        for participant in participants:
            command = {
                        "method" : "setNDIBroadcastingStatusForParticipant",
                        "peerId" : f'{participant["peerId"]}',
                        "active" : True
                      }
            ws.send(json.dumps(command))
            result = ws_wait_for_reply(ws, method="setNDIBroadcastingStatusForParticipant", event=None)
            print(json.dumps(result))
    elif ndi_channel_type == "mix":
        command = {
            "method": "allowRecord"
        }
        ws.send(json.dumps(command))
        result = ws_wait_for_reply(ws, method="allowRecord", event=None)
        print(json.dumps(result))

    # close connection
    ws.close()
