#!/usr/bin/python3

import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client

separator = "##"
touchosc_pages_range = range(1, 2)
overall_loop_range = range(-3, 4)
loop_range = range(0, 3)

#######################
### Events handlers ###
#######################


def receive_from_touchosc(addr, *args):
    (touchosc_page, msg) = convert_to_sooperlooper_compatible(addr, *args)
    if msg is None:
        return
    sooperlooper_client.send(msg)
    if "/sl/-1/set" in msg.address and "wet" in msg.params:
        request_wet_for_all(touchosc_page)


def receive_from_sooperlooper(addr, *args):
    touchosc_page = addr[1]
    args = list(args)
    msg = osc_message_builder.OscMessageBuilder(address="/{}/{}_{}".format(touchosc_page, args[0], args[1]))
    msg.add_arg(args[2])
    print_msg(msg)
    touchosc_client.send(msg.build())


###################
##### Various #####
###################


def convert_to_sooperlooper_compatible(addr, *args):
    args = list(args)
    args = handle_hit(addr, args)
    if args is None:
        return (None, None)
    if debug:
        print("Matched: {} with args: {}".format(addr, args))

    splitted_address = addr.split(separator)
    send_addr = addr
    touchosc_page = 1

    if len(splitted_address) > 1:
        touchosc_page = splitted_address[0][1]
        send_addr = splitted_address[1]
        args = splitted_address[2:] + args

    msg = osc_message_builder.OscMessageBuilder(address=send_addr)
    for arg in args:
        msg.add_arg(arg)

    print_msg(msg)
    return (touchosc_page, msg.build())


def handle_hit(addr, args):
    if "hit" in addr:
        if 0 in args:
            return []
        else:
            return None
    else:
        return args


def request_wet_for_all(touchosc_page):
    for loop in loop_range:
        msg = osc_message_builder.OscMessageBuilder(address="/sl/{}/get".format(loop))
        msg.add_arg("wet")
        msg.add_arg("osc.udp://{}:{}".format(argv.server_ip, argv.server_port))
        msg.add_arg("/{}/touchosc".format(touchosc_page))
        msg = msg.build()
        print("Matched wet for all! Requesting values to send to TouchOSC: {} || {}".format(msg.address, msg.params))
        sooperlooper_client.send(msg)

def print_msg(msg):
    print("Sending to: {} with args: {}".format(msg.address, msg.args))

############
### MAIN ###
############


if __name__ == "__main__":
    hit_args = ['record', 'overdub', 'multiply', 'insert', 'replace', 'reverse', 'mute', 'undo', 'redo', 'oneshot',
                'trigger', 'substitute', 'undo_all', 'redo_all', 'mute_on', 'mute_off', 'solo', 'pause', 'solo_next',
                'solo_prev', 'record_solo', 'record_solo_next', 'record_solo_prev', 'set_sync_pos', 'reset_sync_pos']

    set_args = ['rec_thresh', 'feedback', 'dry', 'wet', 'input_gain', 'rate', 'scratch_pos', 'delay_trigger',
                'quantize',
                'round', 'redo_is_tap', 'sync', 'playback_sync', 'use_rate', 'fade_samples', 'use_feedback_play',
                'use_common_ins', 'use_common_outs', 'relative_sync', 'use_safety_feedback', 'pan1', 'pan2', 'pan3',
                'pan4', 'input_latency', 'output_latency', 'trigger_latency', 'autoset_latency', 'mute_quantized',
                'overdub_quantized']

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action='store_true', help="Debug mode")
    parser.add_argument("--server-ip", default="0.0.0.0", help="Server ip")
    parser.add_argument("--server-port", type=int, default=8000, help="The port the OSC server is listening to")
    parser.add_argument("--touchosc-ip", required=True, help="Touch OSC client ip")
    parser.add_argument("--touchosc-port", type=int, default=9000, help="Touch OSC port to send messages to")
    parser.add_argument("--sooperlooper-ip", default="0.0.0.0", help="SooperLooper client ip")
    parser.add_argument("--sooperlooper-port", type=int, default=9951, help="SooperLooper port to send messages to")
    argv = parser.parse_args()

    debug = argv.d

    sooperlooper_client = udp_client.UDPClient(argv.sooperlooper_ip, argv.sooperlooper_port)
    touchosc_client = udp_client.UDPClient(argv.touchosc_ip, argv.touchosc_port)

    dispatcher = dispatcher.Dispatcher()

    sooperlooper_urls = []
    for touchosc_page in touchosc_pages_range:
        url = "/{}/touchosc".format(touchosc_page)
        dispatcher.map(url, receive_from_sooperlooper)
        if debug:
            print("Registered url: {}".format(url))

        for loop in overall_loop_range:
            for hit_arg in hit_args:
                sooperlooper_urls.append("/{}{}/sl/{}/hit{}{}".format(touchosc_page, separator, loop, separator, hit_arg))

            for set_arg in set_args:
                sooperlooper_urls.append("/{}{}/sl/{}/set{}{}".format(touchosc_page, separator, loop, separator, set_arg))

    for url in sooperlooper_urls:
        dispatcher.map(url, receive_from_touchosc)
        if debug:
            print("Registered url: {}".format(url))

    server = osc_server.ThreadingOSCUDPServer((argv.server_ip, argv.server_port), dispatcher)

    print("################")
    print("Serving on {}".format(server.server_address))
    print("SooperLooper on {}:{}".format(argv.sooperlooper_ip, argv.sooperlooper_port))
    print("TouchOSC on {}:{}".format(argv.touchosc_ip, argv.touchosc_port))
    server.serve_forever()
