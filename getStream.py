# -*- coding: UTF-8 -*-

import numpy as np
import cv2
import sys
import threading, _thread
from queue import Queue
import time
import hashlib
import MTCNN_Crop_Face

LIVE_URL = "rtsp://admin:admin123@172.16.1.29/cam/realmonitor?channel=1&subtype=0"
RECORD_URL = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=2019_05_27_17_06_00&endtime=2019_05_27_17_08_00"

class DealRecord(threading.Thread):

	def __init__(self, start_time, end_time):
		threading.Thread.__init__(self, name = "GetPicture")
		self.start_time = start_time
		self.end_time = end_time

		self.frame_queue = Queue()
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		self.MTC = MTCNN_Crop_Face.MTCNN_Crop_Face()

		if '-' in start_time:
			url = LIVE_URL
		else:
			url = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=" + self.start_time + "&endtime=" + self.end_time
		self.capture = cv2.VideoCapture(url)
		print("get %s"%(url))


	def run(self):
		# 打印视频相关参数，帧率，宽高
		if self.capture.isOpened():
			print (self.capture.get(cv2.CAP_PROP_FPS))
			print (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
			print (self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
		
		_thread.start_new_thread(self.getRecord, ())

		self.dealRecord()


	def getRecord(self):
		while self.capture.isOpened():
			# Capture frame-by-frame
			ret, frame = self.capture.read()
			if frame is None:
				self.frame_queue.put("fileover")
				break
			else:
				# frame = cv2.resize(frame,(864,576))
				self.frame_queue.put(frame)
				# print("---- put frame.")

		print("---- get record finish.")
		self.capture.release()


	def dealRecord(self):
		frame_num = 0
		data = []
		
		file_name = "form %s to %s.txt"%(self.start_time, self.end_time)
		txt = open(file_name, "w")

		last_face = 0
		while 1:
			# get接口默认为阻塞接口，会一直等待数据
			frame = self.frame_queue.get()
			# cv2.imshow('record_raw', frame)
			ha = hash(str(frame))

			if frame == "fileover":
				break

			frame_num += 1
			if (frame_num % 20 == 0) or (self.frame_queue.qsize() != 0):
				print("get frame %d. left %d"% (frame_num, self.frame_queue.qsize()))
			
			# 人脸检测
			# faces = self.MTC.cropface(frame)
			if frame_num % 2 == 1:
				faces = self.MTC.cropface(frame)
				last_face = faces
			else:
				faces = last_face

			for bbox in faces:
				cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)

			cv2.imshow('record_deal',frame)
			# txt.write(str(faces) + "\n")
			txt.write(str(faces) + '  ' + str(ha) + "\n")

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

		txt.flush()
		txt.close()
		print("save to file %s"%(file_name))
		cv2.destroyAllWindows()
		print("---- deal record finish. total frame %d"%(frame_num))



if __name__ == "__main__":

	start_time = "2019_05_27_17_08_20"
	end_time =  "2019_05_27_17_09_30"

	if (len(sys.argv) == 3):
		start_time = sys.argv[1]
		end_time = sys.argv[2]

	test = DealRecord(start_time, end_time)

	test.start()
	test.join()

	print("exit.")



