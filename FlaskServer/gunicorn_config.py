# 文件 gunicorn_config.py
loglevel = 'debug' #日志级别 debug info warning error critical
bind = "127.0.0.1:6000" #绑定地址和端口 # utils.get_host_ip2()+':8000'
daemon = False # 是否以守护进程启动
# workers = multiprocessing.cpu_count() * 2 + 1 #启动进程数
workers = 4 #10
worker_class = 'gthread' #工作模式 切记不能使用 gevent ,会拦截内部flask发出的请求
threads = 4 #每个工作者线程数
worker_connections = 2000 # 最大并发量
pidfile = "./log/gunicorn.pid" # pid 文件
accesslog = "./log/access.log" #访问日志目录
errorlog = "./log/debug.log" #出错日志
graceful_timeout = 300
timeout = 300 #reload worker after slicent 3 secs
# preload_app=True #是否预加载app,加快启动速度
# reload=True # 代码更新自动重启

