# aptC

## 如何在docker内进行测试：
### 构建docker:
在linux系统中下载项目，构建docker测试环境:
```
docker run --name aptc -v <项目位置>:/code -it ubuntu:jammy /bin/bash
```
### 运行docker:
```
docker start aptc
docker exec -it aptc /bin/bash
```
进入docker后，在docker内执行:
```
/usr/bin/apt update
/usr/bin/apt install -y python3 python3-loguru python3-pycurl python3-certifi python3-wget   python3-lz4 python3-magic python3-packaging python3-rarfile python3-numpy python3-uritools python3-rdflib python3-xmltodict python3-yaml python3-sortedcontainers python3-defusedxml python3-license-expression python3-requests
/usr/bin/apt install -y make
cd /code
make install
```

### 手动测试：
apt install xxx，此时会执行检查

### 自动测试：

测试集为`test/jammyinfo.txt`，是Ubuntu jammy版本对应的软件包，应在jammy(22.04)版本中测试

进入`/code/test`文件夹

```
apt install -y devscripts #下载源码包利用了dget

mkdir binary #保存软件包分析结果
mkdir source #临时保存下载的源码包
mkdir src #保存源码包分析结果

```


使用`autotest_binary.py`自动下载测试集中的每个软件包并进行分析

使用`autotest_src.py`自动下载测试集中的每个项目的源码包并进行分析（一个源码包可能对应多个软件包）

此操作需要向服务端提交请求，请运行服务端，并在客户端编辑etc/aptC/config.json，配置服务端ip

使用`check.py`可以粗略对比通过二进制和通过源码生成的分析结果中，外部依赖是否不同

测试的原理是通过不同的方式分析依赖关系，将apt输出结果和内置分析模块的结果对比，确定内部分析模块的正确性

若要详细确认具体的软件包依赖信息，可以修改项目中src/SpecificPackage.py中debugMode，将其设为True。分别将`testbin.py`和`testsrc.py`中的`testName`修改为要测试的项目名，，分别运行，会输出每个软件包依赖信息。

将`testbin.py`的输出结果重定向到`resbin.txt`，`testsrc.py`的输出结果重定向到`restsrc.txt`，可以运行`checkdiff.py`，自动对比两个文件差异

### 取消安装:
```
cd /code
chmod +x uninstall.sh
./uninstall.sh
```
## 如何打包

### 在本地环境构建软件包
```
sudo apt install -y dh-make
```
文件夹改名为aptc-1.0

在文件夹内,若对代码进行修改：
```
dh_make --createorig -i -y
```

```
dpkg-buildpackage -us -uc
```
### 利用docker构建软件包
若对代码进行修改
```
dh_make --native -i -y
```

```
docker build --output=<二进制文件保存目录> --target=deb_package .
```
