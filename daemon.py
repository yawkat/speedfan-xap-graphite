#!/usr/bin/env python3

import re
import socket
import traceback

import graphitesend

import xap

graphitesend.init(graphite_server="192.168.1.3", prefix="xap", system_name="")

recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_socket.bind(('', 3639))

while True:
    buffer: bytes = recv_socket.recv(4096)
    # noinspection PyBroadException
    try:
        decoded = buffer.decode("ascii")
        data = xap.to_map(xap.parse_xAP(decoded))

        if "xAP-header" not in data:
            if "xAP-hbeat" not in data:
                print("xAP-header not present in %s" % (decoded,))
            continue

        source = data["xAP-header"]["source"]
        source_match = re.fullmatch(r"Almico\.SpeedFan\.(.+)", source)
        if source_match:
            dev_id = source_match.group(1)
            prefix = dev_id + '.speedfan.'
            collected_data = {}
            for sensor_id, values in data.items():
                if "curr" in values:
                    sensor_name = values["id"]
                    collected_data[prefix + sensor_id + "." + sensor_name] = values["curr"]
            if len(collected_data) > 0:
                graphitesend.send_dict(collected_data)
            else:
                print("Collected no data from xAP %s" % (decoded,))
        else:
            print("Received xAP from source %s, discarding" % (source,))
    except:
        traceback.print_exc()
