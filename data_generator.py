from faker import Faker
import time
import random
import os
import numpy as np
from datetime import datetime, timedelta

LINE = """{},{},{},{}"""

def generate_log_line(timestamp, device):
    
    temp =  status = np.random.choice([80, 81, 213,205], p = [0.45, 0.45, 0.05, 0.05])
    visc =  np.random.uniform(0,1)

    log_line = LINE.format(timestamp,visc,temp,device)

    return log_line 

def generate_log_lines():
    log_lines = []
    now = datetime.now()
    time_local = now.strftime('%Y%m%d:%H:%M:%S')
    devices = ["device_1", "device_2", "device_3"]
    for device in devices:
        log_lines.append(generate_log_line(time_local, device))
        
    return log_lines
    
