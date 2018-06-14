#!usr/bin/python
# -*- coding: utf-8 -*-

' an im_send project '

# __author__ 'ZHU JIAMIN'

import sys
import mysql.connector #python3不支持
import requests
import json
from os import path, access, R_OK  # W_OK for write permission.

#python2默认编码ascii 使用此方法改为utf8
reload(sys)  
sys.setdefaultencoding('utf8')   

# 流程
# 1.检查传入的参数是否符合程序需求(必填mobile，其他都有默认值)
# 2.检查同级目录下是否有accessToken文件，有的话读取其中的token，没有的话去环信服务器获取后写入到该文件
# 3.拿到accessToken之后，根据传入的参数（mobile, limit, offset），查询数据库，获取发送方集合、接收方的用户信息
# 4.循环发送消息

#请求头
BASE_URL = 'https://a1.easemob.com/xxxx/xxxxxx'

#用来获取和保存环信ACCESS_TOKEN
CLIENT_ID = 'xxxxxx'
CLIENT_SECRET = 'xxxxxxx'
ACCESS_TOKEN ='' #从文件读取
TOKEN_PATH = './accessToken.txt'

#用来存放传入的参数
INPUT_PARAMS = {'offset':0, 'limit':1, 'isGroup':0, 'text': '测试消息'} 

# TODO 
 # 支持往一个人所加的所有群里面发送消息
 # 支持一个群里面所有人往同时群里发消息

def main():
	args = sys.argv
	if len(args) == 1:
		print('请输入必要参数：\
			 \n-mobile 接收方手机号(必填)\
			 \n-text 发送内容(默认为：测试消息)\
			 \n-offset 起始游标(默认为0)\
			 \n-limit 发送数量(默认为1)')
		# \n-isGroup 是否群聊(默认为0，需要则填1)'
		return

	global INPUT_PARAMS
	argsLen = len(args)
	for i in range(argsLen):
		arg = args[i]
		#过滤掉第一个参数（自己本身）
		if i == 0: continue
		if i%2 == 1:
			#去掉key参数中的'-'
			arg = arg.replace('-', '')
			if i < argsLen - 1:
				INPUT_PARAMS[arg] = args[i+1]
				pass

	#检查必要参数mobile是否正确传入
	if not('mobile' in INPUT_PARAMS) or len(INPUT_PARAMS['mobile']) == 0:
		print('请传入必要参数-mobile')
		return

	checkAccessToken()
	pass

#检查access_token 不存在便获取
def checkAccessToken():
	global ACCESS_TOKEN
	if path.exists(TOKEN_PATH) and path.isfile(TOKEN_PATH) and access(TOKEN_PATH, R_OK):
	    # print("token文件存在且可读")
	    f = open(TOKEN_PATH, 'r')
	    ACCESS_TOKEN = f.read()
	    f.close()
	    if not(ACCESS_TOKEN):
	    	getIMAccessToken()
	else:
	    # print("token文件不存在或不可读")
	    getIMAccessToken()

	prepareSend()
	pass

#准备发送 获取发送消息所需要的数据
def prepareSend():
	userSQL = 'select * from y_user where mobile_phone=%s && isdel=0' %(INPUT_PARAMS['mobile'], )
	result = getDataFromDataBase(userSQL)
	accepterInfo = result[0]
	if accepterInfo == None:
		print "未查询到手机号码为%s的用户" %(INPUT_PARAMS['mobile'])
		return

	sendersSQL = 'select * from y_user where mobile_phone like "1300000%%" && isdel=0 limit %s offset %s' %(INPUT_PARAMS['limit'], INPUT_PARAMS['offset'])
	result = getDataFromDataBase(sendersSQL)

	if len(result) == 0:
		print '没有找到发送者列表'
		return

	#imid字段在第14个 这里因为没有使用ORM，返回的是一个元组（tuple）
	toImId = accepterInfo[14]
	for user in result:
		sendMessage(user, toImId)
		pass

	pass

#发送消息
def sendMessage(fromUser, toImId):
	fromImId = fromUser[14]
	if len(ACCESS_TOKEN) == 0: return
	sendBody = {
		"target_type": "users",
		"target": [
			toImId
		],
		"msg": {
			"type": "txt",
			"msg": INPUT_PARAMS['text']
		},
		#13000000000
		"from": fromImId,#"im_378e54cbc6e5453eaad0da67e8f3f1e0",
		"ext": {
			"attr1": "v1"
		}
	}
	url = BASE_URL + '/messages'
	headers = {
		'Content-Type': 'application/json;charset=utf-8', 
		'Authorization': ACCESS_TOKEN
	}
	r = requests.post(url, headers = headers, data = json.dumps(sendBody))

	# print fromUser
	logInfo = '用户名:%s,手机号:%s,' %(fromUser[7], fromUser[8])
	if r.status_code == 200:
		print logInfo + '发送成功'
	else:
		print logInfo + '发送失败'

#传入查询语句 查询数据库
def getDataFromDataBase(execute):
	conn = mysql.connector.connect(host = 'mysql.xxxx.net',user = 'root',
		password = 'xxxx',database = 'xxxx',port = 3306,
		charset = 'utf8')
	cursor = conn.cursor()
	cursor.execute(execute)
	result = cursor.fetchall()
	cursor.close()
	conn.close()
	return result

#获取环信access_token 用于后续操作
def getIMAccessToken():
	global ACCESS_TOKEN
	url = BASE_URL+'/token'
	headers = {'Content-Type': 'application/json;charset=utf-8'}
	payload = {
		'grant_type': 'client_credentials', 
		'client_id': CLIENT_ID, 
		'client_secret': CLIENT_SECRET
	}
	r = requests.post(url,headers = headers,data = json.dumps(payload))
	if r.status_code == 200:
		data = json.loads(r.text)
		# print(data)
		print('获取access_token成功')
		#这里返回的r.text是unicode类型，所以转换出来的dict需要用unicode编码的key取到
		ukey = 'access_token'.encode('unicode_escape')
		ACCESS_TOKEN = 'Bearer ' + data[ukey]
		# 写入文件 w直接覆盖
		fp = open(TOKEN_PATH, 'w')
		fp.write(ACCESS_TOKEN)
		fp.close()
	else:
		print('获取access_token失败')
	pass

if __name__ == '__main__':
	main()
