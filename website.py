from flask import Flask, request, render_template, make_response, jsonify
import time
import secrets
from os import remove, listdir
from threading import Thread, Lock
import logging
import sys
import os
import shutil
# 临时文件存放目录
tempOutputPath = "./tempAudioOutput/"
# 进程锁
locker = Lock()

queueRecord = {
	"time": 0,
	"place": 0
}


# 启动日志
hzysLogger = logging.getLogger()
hzysFileHandler = logging.FileHandler("record.log", encoding="utf8", mode="a")
hzysFormatter = logging.Formatter("%(asctime)s, %(message)s")
hzysFileHandler.setFormatter(hzysFormatter)
hzysLogger.addHandler(hzysFileHandler)
hzysLogger.addHandler(logging.StreamHandler(sys.stdout))
hzysLogger.setLevel(logging.DEBUG)


# 生成ID
def makeid():
	locker.acquire()
	currentSec = str(int(time.time()))
	# 若进入下一秒，重置次序
	if(queueRecord["time"] != currentSec):
		queueRecord["time"] = currentSec
		queueRecord["place"] = 0
	# ID=时间+次序+随机数
	id = currentSec + "_" + str(queueRecord["place"]) + "_" + secrets.token_hex(8)
	queueRecord["place"] += 1
	locker.release()
	return id


# 清理临时文件
def clearCache():
	while(True):
		currentTime = int(time.time())  # 当前时间
		# 输出目录下的所有文件
		for fileName in listdir(tempOutputPath):
			# 文件名符合格式
			try:
				timeCreated = int(fileName.split("_")[0])  # 创建时间
				if (currentTime - timeCreated) > 600:  # 间隔时间(秒)
					if fileName.endswith(".wav"):
						remove(tempOutputPath + fileName)
			# 若文件名不符合格式，(currentTime - timeCreated)会报错
			except:
				pass

		time.sleep(60)


# ----------------------------------------------------
# 核心代码
# ----------------------------------------------------

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


# 用户发出储存音频的请求
@app.route('/send', methods=['POST'])
def Send():
	# 生成选项
	file = request.files['file']
	# 记录日志
	app.logger.debug("%s", request.form)
	# 特殊情况不予生成音频并返回错误代码
    # if (len(file) > 100):
 	# 	return jsonify({"code": 400, "message": "音频过大！"}), 400
	try:
		id = makeid()
		file.save(tempOutputPath + id+".wav")
		out_path = '/home/sovits4/return/' + id+".wav"
		while True:
			time.sleep(5)  # 暂停1秒
			if os.path.exists(out_path):
				shutil.copy2(out_path, tempOutputPath)
				os.remove(out_path)
				return jsonify({"code": 200, "id": id}), 200
		
	except Exception as e:
		# 返回错误代码
		print(e)
		return jsonify({"code": 400, "message": "生成失败"}), 400
	


# 用户发出下载音频的请求
@app.route('/get/<id>.wav')
def get_audio(id):
	try:
		with open(tempOutputPath+id+".wav", 'rb') as f:
			audio = f.read()
		response = make_response(audio)
		f.close()
		response.content_type = "audio/wav"
		return response
	except:
		return render_template("fileNotFound.html"), 404


if __name__ == '__main__':
	Thread(target=clearCache, args=( )).start()
	app.run(port=5000,host='127.0.0.1')
