#对本地二进制包进行分析

import osInfo
import RepoFileManager
import SourcesListManager
import SpecificPackage
import scanSrc
import os
import subprocess
import shutil
from spdx.spdxmain import spdxmain
def querypackageInfo(filePaths):
	res=[]
	for filePath in filePaths:
		if not os.path.isfile(filePath):
			print("cannot open file: "+filePath)
			return []
		if not os.path.exists("/tmp/aptC/packages"):
			os.makedirs("/tmp/aptC/packages")
		filePath=shutil.copy(filePath,"/tmp/aptC/packages")
		p = subprocess.Popen(f"dpkg -I '{filePath}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = p.communicate()
		package=RepoFileManager.parseDEBPackages(stdout.decode().split('\n'),osInfo.OSName,osInfo.OSDist,"")[0]
		package.fileName=filePath
		res.append(package)
	return res

def scanBin(binFiles,options):
	#mode="merge"
	genSpdx=False
	spdxPath='.'
	genCyclonedx=False
	cyclonedxPath='.'
	for option in options:
		# if option.startswith('-mode='):
		# 	mode=option.split('=',1)[1]
		if option.startswith('--genspdx='):
			genSpdx=True
			spdxPath=option.split('=',1)[1]
		if option.startswith('--gencyclonedx='):
			genCyclonedx=True
			cyclonedxPath=option.split('=',1)[1]
	if genSpdx is False and genCyclonedx is False:
		genSpdx=True
	packages=querypackageInfo(binFiles)
	
	if len(packages)==0:
		print("ERROR::failed to get package info: unknown fail")
		return 1
	sourcesListManager=SourcesListManager.SourcesListManager()
	entryMap=SpecificPackage.EntryMap()
	repoPackages=sourcesListManager.getAllPackages()
	repoPackages.extend(scanSrc.setInstalledPackagesStatus(sourcesListManager))
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
			spdxPath=spdxmain(package.fullName,package.fileName,dependsList,'spdx',spdxPath)
		if genCyclonedx is True:
			cyclonedxPath=spdxmain(package.fullName,package.fileName,dependsList,'cyclonedx',cyclonedxPath)
		print("generate SBOM for: "+package.fullName)
	return 0