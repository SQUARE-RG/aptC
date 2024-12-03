# aptC.py为程序入口，若想阅读源码，应从此处开始
# 此文件解析用户输入，从而分析命令类型，并根据命令调用对应模块进行处理

# 若命令为install/reinstall/genspdx/gencyclonedx，则调用scanDeb模块处理，模块返回值表示是否要执行安装，有关该模块详细细节详阅scanBin.py
# 若命令为scanbin，则调用scanBin模块处理
# 若命令为scansrc，则调用scanSrc模块处理
# 若命令为querycve，则调用queryCVE模块处理

# 除此之外，项目存在一些重要的底层模块，在此列出简单介绍：
# RepoFileManager: 实现对元数据进行解析的功能
# SourceListManager: 对本地软件源仓库进行管理，自动读取全部元数据，依赖于RepoFileManager
# PackageInfo.py: 一个PackageInfo表示一个项目的信息，一个项目可以对应一个源码包（如果有源码包的话），一个项目可能对应多个软件包。
# SpecificPackage.py 一个SpecificPackage表示一个软件包的信息，它内部包含一个PackageInfo，即包含了对应项目信息。可能存在多个软件包对应完全相同的项目信息。
# SpecificPackage.py内实现了依赖图分析的代码，请有关该模块详细细节详阅SpecificPackage.py


import sys
import os
import scanDeb
import scanBin
import scanSrc
import queryCVE
def runApt(exec,args,setyes=False):
	cmd=exec
	for arg in args:
		if arg.startswith('--genspdx'):
			continue
		if arg.startswith('--gencyclonedx'):
			continue
		if arg=='-n':
			continue
		cmd+=" "+arg
		if arg=='-y':
			setyes=False
		
	if setyes is True:
		cmd+=" -y"
	return os.system(cmd)

def parseCommand(args):
	command=None
	options=[]
	packages=[]
	needMerge=False
	for arg in args:
		if arg.startswith('-'):
			if needMerge is True:
				options[-1]+=" "+arg
				needMerge=False
			else:
				options.append(arg)
			if arg=='-o' or arg=='-c' or arg=='-t' or arg=='-a' or arg.endswith('='):
				needMerge=True
		else:
			if arg.startswith('=') or needMerge is True:
				options[-1]+=" "+arg
				needMerge=False
			else:
				if command is None:
					command=arg
				else:
					packages.append(arg)
			if arg.endswith('='):
				needMerge=True
	return command,options,packages

def user_main(exec,args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='-s' or arg=="--simulate" or arg=="--just-print" or arg=="--dry-run" or arg=="--recon" or arg=="--no-act" or arg=="-y":
			errcode=runApt(exec,args)
			break
	if errcode is None:
		command,options,packages=parseCommand(args)
		if command=='install' or command=='reinstall':
			if scanDeb.scanDeb(command,options,packages) is True:
				errcode=runApt(exec,args,setyes=True)
			else:
				errcode=0
		elif command=='genspdx':
			if len(packages)<2:
				print("unknown usage for apt genspdx")
				return 1
			scanDeb.scanDeb(command,options,packages[:-1],genSpdx=True,saveSpdxPath=packages[-1],genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=True)
			return 0
		elif command=='gencyclonedx':
			if len(packages)<2:
				print("unknown usage for apt gencyclonedx")
				return 1
			scanDeb.scanDeb(command,options,packages[:-1],genSpdx=False,saveSpdxPath=None,genCyclonedx=True,saveCyclonedxPath=packages[1],dumpFileOnly=True)
			return 0
		elif command=='scanbin':
			errcode=scanBin.scanBin(packages,options)
		elif command=='scansrc':
			errcode=scanSrc.scanSrc(packages,options)
		elif command=='querycve':
			errcode=queryCVE.queryCVECli(packages,options)
	if errcode is None:
		errcode=runApt(exec,args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[0],sys.argv[1:],True)