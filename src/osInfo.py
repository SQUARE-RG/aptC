#获取操作系统信息

import os
OSName=""
OSDist=""
arch=""
with open("/etc/os-release") as f:
	data=f.readlines()
	for info in data:
		if info.startswith('ID='):
			OSName=info.strip()[3:]	
		if info.startswith('VERSION_CODENAME'):
			OSDist=info.strip().split('=')[1]
		#if info.startswith('VERSION_ID'):
		#	OSDist=info.strip()[12:-1]
with os.popen("dpkg --print-architecture") as f:
	arch=f.read().strip()