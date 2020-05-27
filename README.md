# 爬虫远程部署 scrapyd + spiderkeeper + supervisord

![爬虫部署教程](http://book.17kaifa.com/statics/upload/img/spk000.png '爬虫部署教程')


## 远程服务器

### 创建项目目录 

*是在pyuser用户（非root）下操作*

- 创建目录：	`mkdir crawlpro1`

- 进入目录：	`cd crawlpro1/`

- 创建激活python环境（我这里用的pyenv管理）：

`pyenv virtualenv 3.7.0 crawlpro1`

`pyenv activate crawlpro1`

- 通过`pip install -r requirement.txt` 导入依赖


### 安装scrapyd spiderkeeper

*是在pyuser用户（非root）下操作*

`pip install scrapyd`

`pip install spiderkeeper`


###  配置scrapyd(若不需要修改，可跳过)

*是在pyuser用户（非root）下操作*

`find / -name default_scrapyd.conf`

修改scrapyd服务的端口和ip

`vi /home/pyuser/.pyenv/versions/3.7.0/envs/crawlpro1/lib/python3.7/site-packages/scrapyd/default_scrapyd.conf` 


### 设置supervisor监控项

*是在root用户下操作*

centos安装supervisor请参考：[**supervisord在centos7下安装及使用**](#)

安装好supervisor后：

1. 进入supervisord配置目录：	`cd /etc/supervisord.d/`

2. 创建配置文件： `touch serve.ini` 

3. 编写配置文件： `vi serve.ini`

```
	[program:spiderkeeper]
	; 我这里spiderkeeper没有开启auth认证，而是通过nginx的auth_basic做的。
	; command=/home/pyuser/.pyenv/versions/3.7.0/envs/crawlpro1/bin/spiderkeeper --server=http://localhost:6800 --username=user --password=pwd
	command=/home/pyuser/.pyenv/versions/3.7.0/envs/crawlpro1/bin/spiderkeeper --server=http://localhost:6800 --no-auth
	directory=/home/pyuser/siteprojects/crawlpro1
	autostart=true
	autorestart=true
	startretries=3
	user=pyuser


	[program:scrapyd]
	command=/home/pyuser/.pyenv/versions/3.7.0/envs/crawlpro1/bin/scrapyd
	directory=/home/pyuser/siteprojects/crawlpro1
	autostart=true
	autorestart=true
	redirect_stderr=true
	user=pyuser
```

4. 重新加载supervisor文件：	`supervisorctl reload`

### nginx配置



创建配置文件： `cat /etc/nginx/conf.d/spiderkeeper.conf`

编写配置文件：

```
server {
    charset utf-8;
    listen 80;
    server_name spiderkeeper.xxx.com;

    client_max_body_size 4G;
    keepalive_timeout 5;

	location / {
			proxy_pass http://127.0.0.1:5000/;

			proxy_set_header Host $host:80;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

			auth_basic      "Input('Your key:>>>')";
			auth_basic_user_file    /etc/nginx/conf.d/.htpasswd;
	}
}
```

*因为我的修改了nginx运行用户，上传文件时会报500错误*：

` [crit] 29876#0: *65310 open() "/var/lib/nginx/tmp/client_body/0000000025" failed (13: Permission denied)`

需要修改目录权限：

`chmod -R 775 nginx运行用户`

`chmod 775 /var/lib/nginx/tmp/client_body/`


## 本地机器

1. 安装依赖

`pip install scrapyd-client`

2. 验证安装

`scrapyd-deploy -h`

如果提示： `报错: 'scrapyd-deploy' 不是内部或外部命令，也不是可运行的程序或批处理文件`

**解决步骤**：

**一定要找到自己对应的目录**

- 找到项目依赖的python环境文件

- 对应的目录 `D:\pyprojects\crawlpro1\venv\Scripts` 

- 创建文件 `scrapyd-deploy.bat`

```
@echo off

"D:\pyprojects\crawlpro1\venv\Scripts\python.exe" "D:\pyprojects\crawlpro1\venv\Scripts\scrapyd-deploy" %1 %2 %3 %4 %5 %6 %7 %8 %9
```

3. 打包egg文件

**进入项目的全局目录（有settings.py）下运行**

`scrapyd-deploy -p 项目名crawlpro1 -v 版本号1.0 --build-egg=文件名.egg`

打包完就可以在项目目录下看到对应的egg文件

4. 在本地通过`pip freeze > requirement.txt` 导出依赖

## spiderkeeper操作

访问spiderkeeper站点(上面nginx配置的域名)

1. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk001.png "spiderkeeper教程")

2. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk002.png "spiderkeeper教程")

3. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk003.png "spiderkeeper教程") 

4. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk004.png "spiderkeeper教程")

5. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk005.png "spiderkeeper教程")

6. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk006.png "spiderkeeper教程")

7. ![spiderkeeper](http://book.17kaifa.com/statics/upload/img/spk007.png "spiderkeeper教程")

## 