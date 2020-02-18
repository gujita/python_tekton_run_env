# python_tekton_run_env
python基本环境容器（下称A）运行python项目（下称B），B读取集群NFS共享数据（下称C），处理数据后写入C。
（B的项目文件需要上传到Git，A中任务依赖Git中该资源）
