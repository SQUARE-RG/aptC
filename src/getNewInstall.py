import os
import PackageInfo
import SpecificPackage
import SourcesListManager
def getSelfDist():
	with open("/etc/os-release") as f:
		data=f.readlines()
		for info in data:
			if info.startswith('VERSION_CODENAME='):
				return info.strip()[17:]	
	return ""
dist=getSelfDist()
def parseInstallInfo(info:str,sourcesListManager:SourcesListManager.SourcesListManager)->PackageInfo.PackageInfo:
	info=info.split(' ',2)
	name=info[1]
	additionalInfo=info[2][1:-2].split(' ')
	version_release=additionalInfo[0].split('-')
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=additionalInfo[1].split('/')[1]
	arch=additionalInfo[-1]
	sourcesListManager.getGitLink(name,dist,arch)
	packageInfo=PackageInfo.PackageInfo('Ubuntu',dist,name,version,release)
	return packageInfo
def getNewInstall(packageName:str,options,sourcesListManager:SourcesListManager.SourcesListManager):
	cmd="apt install -s "
	for option in options:
		cmd+=option+' '
	cmd+=packageName
	res=[]
	with os.popen(cmd) as f:
		data=f.readlines()
		for info in data:
			if info.startswith('Inst '):
				res.append(parseInstallInfo(info,sourcesListManager))
	return res