#对本地源码包进行分析

import osInfo
import loadConfig
import requests
import RepoFileManager
import SpecificPackage
import SourcesListManager
import normalize
import PackageInfo
from subprocess import PIPE, Popen
import shutil
import os
import tarfile
from spdx.sourcemain import srcmain
def postFile(file,aptConfigure:loadConfig.aptcConfigure):
	try:
		files = {'file': open(file, 'rb')}
		response = requests.post(aptConfigure.postfileURL,files=files)
	except requests.exceptions.ConnectionError as e:
		print("failed to upload file: Unable to connect: "+aptConfigure.postfileURL)
		return None
	except Exception as e:
		print(f'failed to upload file: {e}')
		return None
	if response.status_code == 200:
		data=response.json()
		if data['error']==0:
			return data['token']
		else:
			print("failed to upload file: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to upload file: Request failed with status code {response.status_code}')
		return None
	
def queryBuildInfo(srcFile,srcFile2,osType,osDist,arch,aptConfigure:loadConfig.aptcConfigure):
	src1token=postFile(srcFile,aptConfigure)
	if src1token is None:
		return None
	src2token=None
	if srcFile2 is not None:
		src2token=postFile(srcFile2,aptConfigure)
		if src2token is None:
			return None
	try:
		data={"srcFile":src1token,"srcFile2":src2token,"osType":osType,"osDist":osDist,"arch":arch}
		print("waiting build from server... It may take some time.")
		response = requests.post(aptConfigure.querybuildinfoURL, json=data)
	except requests.exceptions.ConnectionError as e:
		print("failed to query buildInfo: Unable to connect: "+aptConfigure.querybuildinfoURL)
		return None
	except Exception as e:
		print(f'failed to query buildInfo: {e}')
	if response.status_code == 200:
		data=response.json()
		if data['error']==0:
			return data['buildinfo']
		else:
			print("failed to query package info: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to query buildInfo: Request failed with status code {response.status_code}')
		return None
def getSpecificInstalledPackage(packageName,version_release):
	p = Popen(f"apt-cache show {packageName}={version_release}", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	package=RepoFileManager.parseDEBPackages(data,osInfo.OSName,osInfo.OSDist,None)[0]
	package.status="installed"
	return package
def setInstalledPackagesStatus(sourcesListManager:SourcesListManager.SourcesListManager):
	p = Popen("/usr/bin/apt list --installed", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	res=[]
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
		version_release=info.split(' ')[1].rsplit('-',1)
		version=version_release[0].split(':')[-1]
		release=None
		if len(version_release)>1:
			release=version_release[1]
		package=sourcesListManager.getSpecificPackage(packageName,dist,version,release)
		if package is not None:
			package.status="installed"
		else:
			res.append(getSpecificInstalledPackage(packageName,info.split(' ')[1]))
	return res
def unzip(zipfile,toPath):
	with tarfile.open(zipfile) as f:
		f.extractall(toPath)

def extractSrc(srcFile,srcFile2,distPath):
	if os.path.exists(distPath):
		shutil.rmtree(distPath)
	os.makedirs(distPath)
	unzip(srcFile,distPath)
	projectPath=None
	for item in os.listdir(distPath):
		if os.path.isdir(os.path.join(distPath,item)):
			nitem=normalize.normalReplace(item)
			if nitem!=item:
				shutil.move(os.path.join(distPath,item), os.path.join(distPath,nitem))
				item=nitem
			projectPath=os.path.join(distPath,item)
	if projectPath is None:
		print("error:unzip unknown error")
		return None
	if srcFile2:
		unzip(srcFile2,projectPath)
	return projectPath
def scanSrc(srcs,options):
	mode="merge"
	genSpdx=False
	spdxPath='.'
	genCyclonedx=False
	cyclonedxPath='.'
	for option in options:
		if option.startswith('-mode='):
			mode=option.split('=',1)[1]
		if option.startswith('--genspdx='):
			genSpdx=True
			spdxPath=option.split('=',1)[1]
		if option.startswith('--gencyclonedx='):
			genCyclonedx=True
			cyclonedxPath=option.split('=',1)[1]
	if genSpdx is False and genCyclonedx is False:
		genSpdx=True
	if len(srcs)==1:
		srcFile=srcs[0]
		srcFile2=None
	elif len(srcs)==2:
		srcFile=srcs[0]
		srcFile2=srcs[1]
	else:
		print("usage: apt scansrc <src> [-mode=merge|split] or apt scansrc <orig> <patch> [-mode=merge|split]")
		return 0
	osType=osInfo.OSName
	osDist=osInfo.OSDist
	arch=osInfo.arch
	aptConfigure=loadConfig.loadConfig()
	if aptConfigure is None:
		print('ERROR: cannot load config file in /etc/aptC/config.json, please check config file ')
		return 1
	buildInfo=queryBuildInfo(srcFile,srcFile2,osType,osDist,arch,aptConfigure)
	if buildInfo is None:
		return 1
	buildInfo=buildInfo.split('\n')
	packages=RepoFileManager.parseDEBPackages(buildInfo,osType,osDist,"")
	if len(packages)==0:
		print("ERROR::failed to get package info: unknown fail")
		return 1
	sourcesListManager=SourcesListManager.SourcesListManager()
	entryMap=SpecificPackage.EntryMap()
	repoPackages=sourcesListManager.getAllPackages()
	repoPackages.extend(setInstalledPackagesStatus(sourcesListManager))
	skipPackages=dict()
	for package in packages:
		package.status="willInstalled"
		package.registerProvides(entryMap)
		skipPackages[package.fullName]=package
	for package in repoPackages:
		if package.fullName in skipPackages:
			if package.status=="installed":
				skipPackages[package.fullName].status="installed"
			continue
		package.registerProvides(entryMap)
	# for package in packages:
	# 	package.findRequires(entryMap)
	# return 0
	srcPath=extractSrc(srcFile,srcFile2,"/tmp/aptC/extract/")
	if srcPath is None:
		return 1
	if mode=="merge":
		for package in packages:
			SpecificPackage.getDependsPrepare(entryMap,package)
		depset=set()
		for package in packages:
			SpecificPackage.getDepends(entryMap,package,depset)
		depends=dict()
		for p in depset:
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
		dependsList=list(depends.values())
		name=os.path.basename(srcPath)
		if genSpdx is True:
			srcmain(normalize.normalReplace(name),srcPath,dependsList,'spdx',spdxPath)
		if genCyclonedx is True:
			srcmain(normalize.normalReplace(name),srcPath,dependsList,'cyclonedx',cyclonedxPath)

		print("generate SBOM for: "+name)
	else:
		for package in packages:
			SpecificPackage.getDependsPrepare(entryMap,package)
		for package in packages:
			depset=SpecificPackage.getDepends(entryMap,package,set())
			depends=dict()
			for p in depset:
				p.setDscLink()
				depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
			dependsList=list(depends.values())
			if genSpdx is True:
				srcmain(normalize.normalReplace(package.fullName),srcPath,dependsList,'spdx',spdxPath)
			if genCyclonedx is True:
				srcmain(normalize.normalReplace(package.fullName),srcPath,dependsList,'cyclonedx',cyclonedxPath)
			print("generate SBOM for: "+package.fullName)
	return 0
