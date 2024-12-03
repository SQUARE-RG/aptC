# 读取aptC的配置文件

import json
import os
class aptcConfigure:
	def __init__(self,configObj):
		self.querycveURL=configObj['server']['querycve']
		self.postfileURL=configObj['server']['postfile']
		self.querybuildinfoURL=configObj['server']['querybuildinfo']


def checkConfig(configObj)->bool:
	if 'server' not in configObj:
		return False
	server=configObj['server']
	if 'querycve' not in server:
		return False
	if 'postfile' not in server:
		return False
	if 'querybuildinfo' not in server:
		return False
	return True
def loadConfig():
	if not os.path.isfile('/etc/aptC/config.json'):
		return None
	with open('/etc/aptC/config.json',"r") as f:
		configObj=json.load(f)
	if checkConfig(configObj) is False:
		return None
	return aptcConfigure(configObj)