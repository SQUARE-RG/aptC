import os
import RepoFileManager
import SpecificPackage
import osInfo
from loguru import logger as log

class SourceConfigItem:
	def __init__(self,url,dist,channel):
		self.url=url
		self.url_without_prefix=url.split('//')[1].split('/')[0]
		self.dist=dist
		self.channel=channel
		self.repoFileManager=None
	def getFilePath(self):
		return '/var/lib/apt/lists/'+self.url_without_prefix+'_ubuntu_dists_'+self.dist+'_'+self.channel+"_binary-"+osInfo.arch+"_Packages"
	def getRepoFileManager(self):
		if self.repoFileManager is None:
			repoPath=self.getFilePath()
			self.repoFileManager=RepoFileManager.RepoFileManager(self.url,repoPath,osInfo.OSName,osInfo.OSDist)
	def getGitLink(self,name,arch):
		#abandon
		self.getRepoFileManager()
		return self.repoFileManager.getGitLink(name)
	def getSpecificPackage(self,name,version,release)->SpecificPackage.SpecificPackage:
		self.getRepoFileManager()
		return self.repoFileManager.queryPackage(name,version,release)
	def getAllPackages(self):
		self.getRepoFileManager()
		return self.repoFileManager.getAllPackages()
	
def parseDEBTraditionalSources(data,binaryConfigItems,srcConfigItems):
	for info in data:
		info=info.split('#',1)[0].strip()
		if info.startswith('deb '):
			item=info.split(' ')
			url=item[1]
			dist=item[2]
			if dist in binaryConfigItems:
				configItems=binaryConfigItems[dist]
			else:
				configItems=[]
			for channel in item[3:]:
				configItems.append(SourceConfigItem(url,dist,channel))
			binaryConfigItems[dist]=configItems
		elif info.startswith('deb-src '):
			item=info.split(' ')
			url=item[1]
			dist=item[2]
			if dist in srcConfigItems:
				configItems=srcConfigItems[dist]
			else:
				configItems=[]
			for channel in item[3:]:
				configItems.append(SourceConfigItem(url,dist,channel))
			srcConfigItems[dist]=configItems
def parseDEB822Sources(data,binaryConfigItems,srcConfigItems):
	Types=None
	URIs=None
	Suites=[]
	Components=[]
	for info in data:
		info=info.split('#',1)[0].strip()
		if len(info)==0:
			if Types is None:
				continue
			configItems=[]
			for dist in Suites:
				for channel in Components:
					configItems.append(SourceConfigItem(URIs,dist,channel))
				if Types=='deb':
					if dist in binaryConfigItems:
						for item in configItems:
							binaryConfigItems[dist].append(item)
					else:
						binaryConfigItems[dist]=configItems
				elif Types=='deb-src':
					if dist in srcConfigItems:
						for item in configItems:
							srcConfigItems[dist].append(item)
					else:
						srcConfigItems[dist]=configItems
			Types=None
			URIs=None
			Suites=[]
			Components=[]
		if info.startswith('Types:'):
			Types=info.split(':',1)[1].strip()
		if info.startswith('URIs:'):
			URIs=info.split(':',1)[1].strip()
		if info.startswith('Suites:'):
			Suites=info.split(':',1)[1].strip().split(' ')
		if info.startswith('Components:'):
			Components=info.split(':',1)[1].strip().split(' ')
	if Types is not None:
		configItems=[]
		for dist in Suites:
			for channel in Components:
				configItems.append(SourceConfigItem(URIs,dist,channel))
			if Types=='deb':
				if dist in binaryConfigItems:
					for item in configItems:
						binaryConfigItems[dist].append(item)
				else:
					binaryConfigItems[dist]=configItems
			elif Types=='deb-src':
				if dist in srcConfigItems:
					for item in configItems:
						srcConfigItems[dist].append(item)
				else:
					srcConfigItems[dist]=configItems

class SourcesListManager:
	def __init__(self):
		self.binaryConfigItems=dict()
		self.srcConfigItems=dict()
		with open('/etc/apt/sources.list') as f:
			data=f.readlines()
			parseDEBTraditionalSources(data,self.binaryConfigItems,self.srcConfigItems)
		sourcesd='/etc/apt/sources.list.d'
		for file in os.listdir(sourcesd):
			filePath=os.path.join(sourcesd, file)
			if file.endswith('.sources') and os.path.isfile(filePath):
				with open(filePath) as f:
					data=f.readlines()
					parseDEB822Sources(data,self.binaryConfigItems,self.srcConfigItems)
	
	def setGitLink(self,name,arch,dist):
		#abandon
		log.warning("abandon")
		for configItem in self.binaryConfigItems[dist]:
			res=configItem.getGitLink(name,arch)
			if res is not None:
				return res
		return None
	def getSpecificPackage(self,name,dist,version,release)->SpecificPackage.SpecificPackage:
		#version=version.split(":")[-1]
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release)
			if specificPackage is not None:
				return specificPackage
		return None
	def getAllPackages(self):
		res=[]
		for binaryConfigItem in self.binaryConfigItems.values():
			for configItem in binaryConfigItem:
				res.extend(configItem.getAllPackages())
		return res
	#def getSpecificSrcPackage(self,name,dist,version,release)->SpecificPackage.SpecificPackage:
	#	for configItem in self.srcConfigItems[dist]:
	#		specificPackage=configItem.getSpecificPackage(name,version,release)
	#		if specificPackage is not None:
	#			return specificPackage
	#	return None
	
	def getBinaryDebPackage(self,packageInfo):
		pass
