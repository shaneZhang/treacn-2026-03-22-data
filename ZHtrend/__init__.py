# -*- coding: utf-8 -*-
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.txt")
    with open(config_path, 'r', encoding='ascii') as f:
        return f.read()
