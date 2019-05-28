# -*- coding: UTF-8 -*-

import numpy as np
import cv2
import sys
import threading
from Queue import Queue
import time

LIVE_URL = "rtsp://admin:admin123@172.16.1.29/cam/realmonitor?channel=1&subtype=0"
RECORD_URL = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=2019_05_27_17_06_00&endtime=2019_05_27_17_08_00"

SEGMENT_TIME = 60  #切片间隔，单位秒

class GetRecord(threading.Thread):

	def __init__(self, queue, start_time, end_time):
		threading.Thread.__init__(self, name = "GetPicture")
		self.frame_queue = queue
		self.start_time = start_time
		record_url = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=" + start_time + "&endtime=" + end_time
		self.capture = cv2.VideoCapture(record_url)

		# 打印视频相关参数，帧率，宽高
		if self.capture.isOpened():
			print (self.capture.get(cv2.CAP_PROP_FPS))
			print (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
			print (self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


	def run(self):	
		while self.capture.isOpened():
			# Capture frame-by-frame
			ret, frame = self.capture.read()
			# cv2.imshow('image_ori', frame)
			if frame is None:
				self.frame_queue.put("fileover")
				break
			else:
				self.frame_queue.put(frame)
				print("---- put frame.")

		print("---- get record finish.")
		self.capture.release()


class ShowPicture(threading.Thread):

	def __init__(self, queue, file_name):
		threading.Thread.__init__(self, name = "ShowPicture")
		self.frame_queue = queue
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		self.stop_flag = False
		self.file_name = file_name


	def run(self):
		frame_num = 0
		txt = open(self.file_name, "w")

		while 1:
			# get接口默认为阻塞接口，会一直等待数据
			frame = self.frame_queue.get()
			if frame == "fileover":
				break

			frame_num = frame_num + 1
			print("get frame %d. left %d"% (frame_num, self.frame_queue.qsize()))
			
			# opencv读取的图片格式为bgr24 转为灰度图
			frame_temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			# 直方图均匀化(改善图像的对比度和亮度)
			frame_temp = cv2.equalizeHist(frame_temp)	

			# 获取该图片中的各个人脸的坐标,画框
			faces = self.face_cascade.detectMultiScale(frame_temp, 1.3, 5)
			# print(faces)
			for (x, y, w, h) in faces:
				frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
				roi_gray = frame[y:y + h, x:x + w]
				roi_color = frame[y:y + h, x:x + w]

			
			content = str(frame_num) + ' ' + str(faces) + "\n"
			txt.write(content)

			cv2.imshow('image',frame)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		txt.flush()
		txt.close()
		cv2.destroyAllWindows()
		print("---- deal record finish.")
			

	def stop(self):
		self.stop_flag = True
		cv2.destroyAllWindows()


if __name__ == "__main__":

	queue = Queue()

	start_time = "2019_05_27_17_09_00"
	end_time = "2019_05_27_17_10_00"
	file_name = "data/" + start_time + "_to_" + end_time + ".txt"

	producer = GetRecord(queue, start_time, end_time)
	consumer = ShowPicture(queue, file_name)

	producer.start()
	consumer.start()

	producer.join()
	consumer.join()

	print("exit.")
