import os
import SpecificPackage
import SourcesListManager
from loguru import logger as log
def getSelfDist():
	with open("/etc/os-release") as f:
		data=f.readlines()
		for info in data:
			if info.startswith('VERSION_CODENAME='):
				return info.strip()[17:]	
	return ""
dist=getSelfDist()
def parseInstallInfo(info:str,sourcesListManager:SourcesListManager.SourcesListManager)->SpecificPackage.SpecificPackage:
	info=info.strip().split(' ',2)
	name=info[1]
	additionalInfo=info[2].split(']')[-2].strip()[1:].split(' ')
	version_release=additionalInfo[0].split('-')
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=additionalInfo[1].split('/')[1].split(',')[0]
	#arch=additionalInfo[-1][1:-1]
	#packageInfo=PackageInfo.PackageInfo('Ubuntu',dist,name,version,release,arch)
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release)
	specificPackage.setGitLink()
	return specificPackage
def getInstalledPackageInfo(packageName,sourcesListManager):
	#abandon
	log.warning("it's a abandon function")
	with os.popen("/usr/bin/apt list --installed") as f:
		data=f.readlines()
		tmp=packageName+'/'
		for info in data:
			if info.startswith(tmp):
				dist=info.split(',')[0].split('/')[1]
				version_release=info.split(',')[1].split('-')
				version=version_release[0]
				release=None
				if len(version_release)>1:
					release=version_release[1]
				return sourcesListManager.getSpecificPackage(packageName,dist,version,release)
	print("error")
	return None

def getNewInstall(packageName:str,options,sourcesListManager:SourcesListManager.SourcesListManager):
	cmd="apt-get reinstall -s "
	for option in options:
		cmd+=option+' '
	cmd+=packageName
	res=[]
	#log.info('cmd is '+cmd)
	#actualPackageName=packageName
	with os.popen(cmd) as f:
		data=f.readlines()
		for info in data:
			# if info.startswith('Note, selecting '):
			# 	print(info)
			# 	actualPackageName=info.split('\'')[1]
			# 	log.info("Note, selecting \'"+actualPackageName+"\' instead of \'"+packageName+"\'")
			# it not work because in non-terminal, the info will show
			if info.startswith('Inst '):
				res.append(parseInstallInfo(info,sourcesListManager))
	selectedPackage=None
	for p in res:
		if p.fullName==packageName:
			selectedPackage=p
	if selectedPackage is None:
		for p in res:
			for provide in p.providesInfo:
				if provide.name==packageName:
					selectedPackage=p
	if selectedPackage is None:
		log.warning("unknown error")
	return selectedPackage,res