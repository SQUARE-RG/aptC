import json
import normalize
class PackageInfo:
	def __init__(self,osType:str,dist:str,name:str,version:str,release:str,arch:str,dscLink=None):
		self.osType=osType
		self.dist=dist
		self.name=name
		#self.gitLink=gitLink
		self.arch=arch
		self.version=version
		self.release=release
		self.dscLink=dscLink
	def dump(self):
		info={'osType':self.osType,'dist':self.dist,'name':self.name,'version':self.version,'release':self.release}
		#if self.dscLink is not None:
		#	info['dscLink']=self.dscLink
		return json.dumps(info)
	def dumpAsDict(self):
		release=""
		if self.release is not None:
			release="-"+self.release
		version=self.version+release
		info={'name':normalize.normalReplace(self.name),'version':normalize.normalReplace(version),'purl':self.dumpAsPurl()}
		if self.dscLink is not None:
			info['dscLink']=self.dscLink
		return info

	def dumpAsPurl(self):
		osKind="deb"
		release=""
		if self.release is not None:
			release="-"+self.release
		if self.dscLink is None:
			return 'pkg:'+osKind+'/'+self.osType+'/'+normalize.normalReplace(self.name)+'@'+normalize.normalReplace(self.version+release)+'.'+normalize.normalReplace(self.dist)
		else:
			return 'pkg:'+osKind+'/'+self.osType+'/'+normalize.normalReplace(self.name)+'@'+normalize.normalReplace(self.version+release)+'.'+normalize.normalReplace(self.dist)+"?"+"dscLink="+normalize.normalReplace(self.dscLink)

def loadPurl(purlStr):
	info=purlStr.split(':',1)[1]
	info_extra=info.split('?')
	info=info_extra[0].split('/')
	osType=info[1]
	name=info[2].split('@')[0]
	version_dist=info[2].split('@')[1].rsplit('.',1)
	version_release=version_dist[0].rsplit('-',1)
	version=version_release[0]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=""
	if len(version_dist)>1:
		dist=version_dist[1]
	dscLink=""
	if len(info_extra)>1:
		extraInfo=info_extra[1]
		for extra in extraInfo.split('&'):
			ei=extra.split('=')
			if ei[0]=='dscLink':
				dscLink=ei[1]
	return PackageInfo(osType,dist,name,version,release,dscLink)