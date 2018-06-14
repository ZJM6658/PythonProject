# PythonProject
<h3 align="center">python入坑小项目</h3>
---

###1、环信多对一消息发送脚本【projects/imsend/imsend.py】

- 功能描述
		
	- 客户端App里面集成了环信即时通信，为了压力测试，需要客户端同一时间接收大量消息的测试，人力测试达不到要求，所以使用脚本来发送大量消息。
	- 群聊需要多人同时发送消息进行压力测试
	- 脚本目前支持四个参数：mobile: 接收者手机号，text：发送的文本内容，limit：指定多少人给接收者发送消息，offset：从多少下标开始（因为有可能发送到某一个号的时候停止了，下次可以接着上次中止的地方发送）
	- 目前单聊是使用指定的1300000（0000-2000）号码生成的用户进行消息发送，群聊消息待支持（TODO）

- 实现逻辑

	-  检查传入的参数是否符合程序需求(必填mobile，(text, limit, offset)有相应默认值，见运行效果图)

	- 检查同级目录下是否有accessToken文件，有的话读取其中的token，没有的话去环信服务器获取后写入到该文件

	- 拿到accessToken之后，根据传入的参数（mobile, limit, offset），查询数据库，获取发送者集合、接收者的用户信息

	- 循环发送消息（fromImid to acceptImids）

- 语言特性

	- python编码问题，默认是ASCII编码，需要主动指定为utf8
	- python3不支持 `mysql.connector` 模块
	- 使用`mysql.connector`模块连接数据库，查询到的数据库信息返回默认是unicode编码，需要转换为json
	- python2对全局变量进行赋值的时候，需要先进行局部global varname定义
	- python与或非： and or not

- 运行效果

	![运行效果](https://github.com/ZJM6658/PythonProject/blob/master/projects/imsend/im_send.png?raw=true)

---
####2、未完待续