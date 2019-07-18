from __future__ import division

from __future__ import print_function
import six
import argparse
import sys
from flask import Flask, url_for, jsonify, render_template
import json
import re
import sys
import requests 
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
import subprocess

def init_arg_parser():
    arg_parser = argparse.ArgumentParser()

    #### General configuration ####
    arg_parser.add_argument('--cuda', action='store_true', default=False, help='Use gpu')
    arg_parser.add_argument('--config_file', type=str, required=True,
                            help='Config file that specifies model to load, see online doc for an example')
    arg_parser.add_argument('--port', type=int, required=False, default=8081)

    return arg_parser

if __name__ == '__main__':
    args = init_arg_parser().parse_args()
    config_dict = json.load(open(args.config_file))
    parser_id = config_dict["parser_id"]
    subprocess.Popen(["python2", "server/tranx_server.py","--config_file",args.config_file])
    subprocess.call(["python2", "server/micro_stream_client.py",parser_id])