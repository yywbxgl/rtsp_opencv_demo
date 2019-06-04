# -*- coding: UTF-8 -*-

import numpy as np
import cv2
import sys
import threading, thread
from Queue import Queue
import time
import requests
import json

LIVE_URL = "rtsp://admin:admin123@172.16.1.29/cam/realmonitor?channel=1&subtype=0"
RECORD_URL = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=2019_05_27_17_06_00&endtime=2019_05_27_17_08_00"

SEGMENT_TIME = 60  #切片间隔，单位秒
FPS = 15  #帧率，可以从码流中获取
PER_FILE_FRAME = SEGMENT_TIME * FPS

FILE_PATH = "data/"

# DATA_SERVER = "http://127.0.0.1:8000/"
DATA_SERVER = "http://172.16.1.91:8000/"

class playRecord():

	def __init__(self, start_time, end_time):
		# threading.Thread.__init__(self, name = "GetPicture")
		self.start_time = start_time
		self.end_time = end_time
		self.start_timeArray = time.strptime(self.start_time, "%Y_%m_%d_%H_%M_%S")
		self.sart_timeStamp = time.mktime(self.start_timeArray)

		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		self.frame_queue = Queue()
		self.ai_data_queue = Queue(1200)
		record_url = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=" + self.start_time + "&endtime=" + self.end_time
		self.capture = cv2.VideoCapture(record_url)
		print("get %s"%(record_url))

		self.stop_flag = False

	def run(self):
		# 打印视频相关参数，帧率，宽高
		if self.capture.isOpened():
			print (self.capture.get(cv2.CAP_PROP_FPS))
			print (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
			print (self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
		
		self.t1 = thread.start_new_thread(self.getRecord, ())
		self.t2 = thread.start_new_thread(self.getAIData, ())

		self.play()


	def getRecord(self):
		while self.capture.isOpened() and not self.stop_flag:
			# Capture frame-by-frame
			ret, frame = self.capture.read()
			if frame is None:
				self.frame_queue.put("fileover")
				break
			else:
				self.frame_queue.put(frame)

		print("---- get record finish.")
		self.capture.release()


	def getAIData(self):

		timetemp = self.sart_timeStamp
		while not self.stop_flag:
			txt_name = time.strftime("%Y%m%d_%H%M", time.localtime(timetemp))
			txt_name = txt_name + '00.txt'
			url = DATA_SERVER + txt_name
			print("get url=%s"%(url))
			response = requests.get(url)
			print("response=%d"%(response.status_code))
			if response.status_code != 200:
				break
			
			lines = response.text.split('\n')

			# 第一个文件起始位置精确到秒数
			drop_num = 0
			if timetemp == self.sart_timeStamp:
				drop_num = self.start_timeArray.tm_sec * FPS
				if drop_num >= len(lines) -2:
					drop_num = len(lines) -2
				print("droped=%d"%(drop_num))

			for line in lines[drop_num:-1]:
				d = json.loads(line)
				self.ai_data_queue.put(d)
			
			timetemp += 60

		print("---- get ai data finish.")


	def play(self):
		frame_num = 0
		data = []
		while 1:
			# get接口默认为阻塞接口，会一直等待数据
			frame = self.frame_queue.get()
			ai_data = self.ai_data_queue.get()

			if frame == "fileover":
				break

			frame_num += 1
			if (frame_num % (FPS*10) == 0):
				print("get frame %d. left %d"% (frame_num, self.frame_queue.qsize()))
			
			# 只显示了一个人脸
			if len(ai_data) != 0:
				x = ai_data[0][0]
				y = ai_data[0][1]
				w = ai_data[0][2]
				h = ai_data[0][3]
				frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

			cv2.imshow('image',frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		cv2.destroyAllWindows()
		self.stop_flag = True
		print("---- deal record finish. total frame %d"%(frame_num))
		time.sleep(1)


if __name__ == "__main__":

	start_time = "2019_05_27_17_06_00"
	end_time =  "2019_05_27_17_16_00"

	if (len(sys.argv) == 3):
		start_time = sys.argv[1]
		end_time = sys.argv[2]

	test = playRecord(start_time, end_time)
	# test.setDaemon(True)
	# test.start()
	# test.join()
	test.run()
	print("exit.")



