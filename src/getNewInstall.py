# getNewInstall函数传入的packages参数是一个列表，表示同时指定安装不定数量的软件包，分析每个软件包的外部依赖

# 若getNewInstall函数的includeInstalled参数为False，则只调用apt进行模拟安装，获取软件名和版本号，从软件仓库元数据中查找对应元数据详细信息，从而获取未安装的外部依赖及其元数据
# 若getNewInstall函数的includeInstalled参数为True，则：
# 使用同样步骤获取未安装的外部依赖及其元数据
# 读取本地安装软件包的元数据
# 将获取的未安装外部依赖软件包的元数据和本地安装的软件包的元数据一起进行依赖图分析，找出未安装外部依赖软件包依赖了哪些本地安装的软件包
# 将被依赖的本地安装软件包加入外部依赖列表，作为结果返回

import os
import SpecificPackage
import SourcesListManager
from subprocess import PIPE, Popen
import osInfo
import RepoFileManager
from loguru import logger as log

def parseInstallInfo(info:str,sourcesListManager:SourcesListManager.SourcesListManager)->SpecificPackage.SpecificPackage:
	info=info.strip()
	while info.endswith(']'):
		info=info.rsplit('[',1)[0].strip()
	info=info.split(' ',2)
	name=info[1]
	additionalInfo=info[2].split(']')[-2].strip()[1:].split(' ')
	version_release=additionalInfo[0]
	version,release=RepoFileManager.splitVersionRelease(version_release)
	dist=additionalInfo[1].split('/')[1].split(',')[0]
	#arch=additionalInfo[-1][1:-1]
	#packageInfo=PackageInfo.PackageInfo('Ubuntu',dist,name,version,release,arch)
	#print(name,dist,version,release)
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release)
	specificPackage.status="willInstalled"

	return specificPackage
def getSpecificInstalledPackage(packageName,version_release):
	p = Popen(f"apt-cache show {packageName}={version_release}", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	package=RepoFileManager.parseDEBPackages(data,osInfo.OSName,osInfo.OSDist,None)[0]
	package.status="installed"
	return package
def getInstalledPackagesInfo(sourcesListManager):
	res=[]
	p = Popen("/usr/bin/apt list --installed", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data[1:]:
		if len(info)==0:
			continue
		packageName=info.split('/',1)[0]
		dists=info.split('/',1)[1].split(' ',1)[0].split(',')
		dist=None
		for d in dists:
			if d!="now":
				dist=d
				break
		if dist is None:
			res.append(getSpecificInstalledPackage(packageName,info.split(' ')[1]))
			continue
		version_release=info.split(' ')[1]
		version,release=RepoFileManager.splitVersionRelease(version_release)
		package=sourcesListManager.getSpecificPackage(packageName,dist,version,release)
		
		if package is not None:
			package.status="installed"
			res.append(package)
		else:
			res.append(getSpecificInstalledPackage(packageName,info.split(' ')[1]))
	return res
	

def getNewInstall(packages:list,options,sourcesListManager:SourcesListManager.SourcesListManager,includeInstalled=False):
	cmd="/usr/bin/apt-get reinstall -s "
	for option in options:
		if option.startswith('--genspdx'):
			continue
		if option.startswith('--gencyclonedx'):
			continue
		if option.startswith('-n'):
			continue
		cmd+=option+' '
	for packageName in packages:
		cmd+=packageName+' '
	willInstallPackages=[]
	#log.info('cmd is '+cmd)
	#actualPackageName=packageName
	p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data:
		# if info.startswith('Note, selecting '):
		# 	print(info)
		# 	actualPackageName=info.split('\'')[1]
		# 	log.info("Note, selecting \'"+actualPackageName+"\' instead of \'"+packageName+"\'")
		# it not work because in non-terminal, the info will show
		if info.startswith('Inst '):
			willInstallPackages.append(parseInstallInfo(info,sourcesListManager))
	if len(willInstallPackages)==0:
		print("warning: no package will install")
		return None
	resmap=dict()
	entryMap=SpecificPackage.EntryMap()
	if includeInstalled is True:
		installedPackages=getInstalledPackagesInfo(sourcesListManager)
		for package in installedPackages:
			package.registerProvides(entryMap)
	for p in willInstallPackages:
		p.registerProvides(entryMap)
	package_select=set()
	for packageName in packages:
		selectedPackage=None
		packageName=packageName.split('=',1)[0]
		for p in willInstallPackages:
			if p.fullName==packageName:
				selectedPackage=p
		if selectedPackage is None:
			for p in willInstallPackages:
				for provide in p.providesInfo:
					if provide.name==packageName:
						selectedPackage=p
						break
				if selectedPackage is not None:
					break
			if includeInstalled is True:
				for p in installedPackages:
					for provide in p.providesInfo:
						if provide.name==packageName:
							selectedPackage=p
							break
					if selectedPackage is not None:
						break

		if selectedPackage is None:
			continue
			
		#selectedPackage.findRequires(entryMap)
		#return None,[]
		SpecificPackage.getDependsPrepare(entryMap,selectedPackage)
		package_select.add(selectedPackage)
	for selectedPackage in package_select:
		depends=SpecificPackage.getDepends(entryMap,selectedPackage,set())
		res=list(depends)
		resmap[selectedPackage]=res
	return resmap
