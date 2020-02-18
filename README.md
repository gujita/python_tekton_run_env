## 目标
在Tekton Pipeline中，使用python基本环境容器（下称A）运行python项目（下称B），B读取集群NFS共享数据（下称C），处理数据后写入C。
（B的项目文件需要上传到Git，A中任务依赖Git中该资源）

## 一、NFS搭建
目的：使用NFS模拟数据共享
### 1.1 NFS Server端
**1. 配置**
```bash
yum install nfs-utils
mkdir /var/nfs
chmod -R 777 /var/nfs
chown nfsnobody:nfsnobody /var/nfs

systemctl enable rpcbind
systemctl start rpcbind
```
`vi /etc/exports`：
/var/nfs 192.168.0.39(rw,sync,no_root_squash,no_subtree_check) 192.168.0.41(rw,sync,no_root_squash,no_subtree_check)

**2. 参数解释：**
```
(1) Ro 该主机对该共享目录有只读权限

(2) Rw 该主机对该共享目录有读写权限

(3) Root_squash 客户机用root用户访问该共享文件夹时，将root用户映射成匿名用户

(4) No_root_squash 客户机用root访问该共享文件夹时，不映射root用户

(5) All_squash 客户机上的任何用户访问该共享目录时都映射成匿名用户

(6) Sync 资料同步写入到内存与硬盘中

(7) Async 资料会先暂存于内存中，而非直接写入硬盘

(8) Insecure 允许从这台机器过来的非授权访问
　
(9) subtree_check 如果共享/usr/bin之类的子目录时，强制NFS检查父目录的权限（默认）

(10) no_subtree_check 和上面相对，不检查父目录权限
```
**3. 查看共享信息**

![查看](https://img-blog.csdnimg.cn/20200214185602230.png#pic_center)

### 1.2 NFS Client端
**1. 准备**
yum install nfs-utils
mkdir /var/nfs

**2. 检查NFS服务器上可用的NFS共享**

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200214185956363.png#pic_center)
**3. 挂载**
mount -t nfs -v 192.168.0.40:/var/nfs /var/nfs
**4. 验证**
- mount | grep nfs
- df -h

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200214192449146.png#pic_center)
**5. 设置开机自动挂载**
`vi /etc/fstab`
192.168.0.40:/var/nfs    /var/nfs   nfs defaults 0 0

## 二、测试代码
### 2.1 main.py
```python
import numpy as np


def read_file(file_path):
    with open(file_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    # convert str to int
    return list(map(int, content))


def write_file(file_path, content):
    f = open(file_path, 'a')
    f.write(content)
    f.close()


if __name__ == '__main__':
    print('np.version.full_version : ' + np.version.full_version)
    nums = read_file('/var/nfs/read/number_to_add.txt')
    write_file('/var/nfs/write/number_added.txt', str(nums[0] + nums[1]))
    write_file('/var/nfs/write/number_added.txt', str(np.arange(6)))

```
### 2.2 requirements.txt
numpy
pandas

## 三、tekton yaml
### 3.1 PiplineResource

```bash
apiVersion: tekton.dev/v1alpha1
kind: PipelineResource
metadata:
  name: resource-git-for-python-run
spec:
  type: git
  params:
   - name: url
     value: https://github.com/gujita1/python_tekton_run_env.git
   - name: revison
     value: master
```

### 3.2 Task
1. 拉取git
2. 挂载数据
3. 运行
```bash
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: task-python-run-on-verification-env
spec:
  inputs:
    resources:
      - name: source-fed-to-task
        type: git
  steps:
    - name: list-source
      image: ubuntu
      command: ["/bin/bash"]
      args: ['-c', 'ls -R $(inputs.resources.source-fed-to-task.path)/']
    - name: run-on-verification-env
      image: python:3.6-buster
      volumeMounts:
        - name: data-volume
          mountPath: /var/nfs/
      workingDir: "$(inputs.resources.source-fed-to-task.path)/"
      command:
        - /bin/bash
      args:
        - -c
        - |
          ls -R /var/nfs/
          pip install -r requirements.txt --index https://pypi.tuna.tsinghua.edu.cn/simple
          python main.py
  volumes:
    - name: data-volume
      hostPath:
        path: /var/nfs/
```

### 3.3 TaskRun

```python
apiVersion: tekton.dev/v1alpha1
kind: TaskRun
metadata:
  name: taskrun-python-run-on-verification-env
spec:
  taskRef:
    name: task-python-run-on-verification-env
  inputs:
    resources:
      - name: source-fed-to-task
        resourceRef:
          name: resource-git-for-python-run

```

```
kubectl get pods -A
tkn tr desc taskrun-python-run-based-docker
kubectl get taskruns taskrun-python-run-based-docker -o yaml

tkn tr logs -f taskrun-python-run-on-verification-env
tkn t logs -f task-python-run-on-verification-env

tkn tr cancel taskrun-python-run-on-verification-env

tkn tr delete -f taskrun-python-run-on-verification-env
tkn t delete -f task-python-run-on-verification-env

kc apply -f pipeline.yaml
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200218212852689.png?type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhaXhXYW5n,size_16,color_FFFFFF,t_70)

## 参考
1. [NFS Server and Client Installation on CentOS 7](https://www.howtoforge.com/nfs-server-and-client-on-centos-7)
2. [NFS /etc/exports参数解释](https://blog.csdn.net/qq_36357820/article/details/78488077)
3. [One NFS server to multiple clients](https://askubuntu.com/questions/609891/one-nfs-server-to-multiple-clients)
4. [How To Setup NFS Server on CentOS 7 / RHEL 7](https://www.itzgeek.com/how-tos/linux/centos-how-tos/how-to-setup-nfs-server-on-centos-7-rhel-7-fedora-22.html)

