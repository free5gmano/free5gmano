import os

from free5gmano import settings

if not os.path.exists('/data/'):
    os.mkdir('/data/')

if not os.path.exists(settings.DATA_DIR):
    os.mkdir(settings.DATA_DIR)
