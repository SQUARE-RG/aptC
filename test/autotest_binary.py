import sys
import os
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import normalize
import aptC
def autotest_binary(projectName,infos,checkExist=True):
	if checkExist:
		for info in infos:
			if os.path.isfile(f"./binary/{projectName}/"+normalize.normalReplace(f"{info[0]}.spdx.json")):
				return 0
	# for name,version,release in infos:
	# 	if "~" in version or (release is not None and "~" in release):
	# 		return 0
	print("-------")
	packages=["genspdx"]
	for name,version,release in infos:
		print(name,version,release)
		if release is not None:
			packages.append(f"{name}={version}-{release}")
		else:
			packages.append(f"{name}={version}")
	if not os.path.isdir(f"./binary/{projectName}"):
		os.mkdir(f"./binary/{projectName}")
	packages.append(f"binary/{projectName}")
	#for info in packages:
	#	print(info,end=' ')
	#print("")
	return aptC.user_main("apt",packages, exit_code=False)

if __name__ == "__main__":
	with open("jammyinfo.txt") as f:
		data=f.readlines()
	nameMap=dict()
	for info in data:
		if info.startswith("#"):
			continue
		info=info.split(' ')
		name=info[0].strip()
		fullName=info[1].strip()
		version=info[2].strip()
		if len(info)>3:
			release=info[3].strip()
		else:
			release=None
		if name not in nameMap:
			nameMap[name]=[]
		nameMap[name].append((fullName,version,release))
	for name,infos in nameMap.items():
		if autotest_binary(name,infos)!=0:
			print(infos)
			break
		
		#autotest_src(name,version,release)
