# encoding: UTF-8
from __future__ import division
import os
import time
import sys
import logging
import requests
import datetime
import traceback
import hashlib
import copy
import re
import zlib

from .xtc_base import *

class XTC_STR_LOG(BaseLog):
    def init(self, conf):
        self.log_buff = []

    def clear(self):
        self.log_buff = []

    def log(self, level, info):
        msg = time.asctime() + ":\t" + format(info)
        print(msg, "\n")
        self.log_buff.append(msg)
                        