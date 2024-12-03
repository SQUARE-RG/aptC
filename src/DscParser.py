# getDscFileLink函数：输入为软件包信息，根据一定规则生成对应dsc文件链接。


import nwkTools
from loguru import logger as log
import os
def getDscFile(repoURL,dscFileName):
	#abandon
	baseURL=repoURL
	try:
		dscFilePath=nwkTools.downloadFile(baseURL+dscFileName,os.path.join("/tmp","aptC","repoMetadata","dscFiles",dscFileName.rsplit('/',1)[0]),dscFileName.rsplit('/',1)[1])
		#os.chmod(dscFilePath, 0o744)
		return dscFilePath
	except Exception as e:
		#log.info("download failed : dsc file :"+dscFileName+" from "+baseURL+dscFileName)
		return None
def parseDscFile(dscFilePath):
	#abandon
	with open(dscFilePath,"r") as f:
		data=f.readlines()
	for info in data:
		info=info.strip()
		if info.startswith("Vcs-Git:") or info.startswith("Debian-Vcs-Git:"):
			return info.split(' ',1)[1]
def getGitLink(specPackageInfo):
	#abandon
	#下载dsc文件，从dsc文件中获取git链接信息。
	repoURL=specPackageInfo.repoURL
	if repoURL is None or specPackageInfo.fileName == "":
		return None
	version=specPackageInfo.fileName.rsplit('_',2)[1]
	source=specPackageInfo.source.split(' ')
	if len(source)>1:
		version=source[1].strip()[1:-1]
	dscFileName=specPackageInfo.fileName.rsplit('/',1)[0]+'/'+specPackageInfo.packageInfo.name+'_'+version+".dsc"
	dscFilePath=getDscFile(repoURL,dscFileName)
	if dscFilePath is None:
		return None
	gitLink=parseDscFile(dscFilePath)
	return gitLink


def getDscFileLink(specPackageInfo):
	repoURL=specPackageInfo.repoURL
	if repoURL is None or specPackageInfo.fileName == "":
		return None
	version=specPackageInfo.fileName.rsplit('_',2)[1]
	source=specPackageInfo.source.split(' ')
	if len(source)>1:
		version=source[1].strip()[1:-1]
	dscFileName=specPackageInfo.fileName.rsplit('/',1)[0]+'/'+specPackageInfo.packageInfo.name+'_'+version+".dsc"
	return repoURL+dscFileName
