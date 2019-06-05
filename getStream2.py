# -*- coding: UTF-8 -*-

import numpy as np
import cv2
import sys
sys.path.append('..')
import threading, _thread
from queue import Queue
import time
import hashlib


from Detection.MtcnnDetector import MtcnnDetector
from Detection.detector import Detector
from Detection.fcn_detector import FcnDetector

from train_models.mtcnn_model import P_Net, R_Net, O_Net
# from prepare_data.loader import TestLoader

LIVE_URL = "rtsp://admin:admin123@172.16.1.29/cam/realmonitor?channel=1&subtype=0"
RECORD_URL = "rtsp://admin:admin123@172.16.1.16:554/cam/playback?channel=1&subtype=0&starttime=2019_05_27_17_06_00&endtime=2019_05_27_17_08_00"


class MTCNN_Crop_Face(object):
    def __init__(self):
        test_mode = "PNet"
        thresh = [0.6, 0.7, 0.7]
        min_face_size = 20
        stride = 2
        slide_window = False
        shuffle = False

        batch_size = [2048, 64, 16]
        detectors = [None, None, None]
        prefix = ['./data2/MTCNN_model/PNet_landmark/PNet', './data2/MTCNN_model/RNet_landmark/RNet', './data2/MTCNN_model/ONet_landmark/ONet']
        epoch = [18, 14, 16]
        model_path = ['%s-%s' % (x, y) for x, y in zip(prefix, epoch)]
        PNet = FcnDetector(P_Net, model_path[0])
        detectors[0] = PNet
        RNet = Detector(R_Net, 24, 1, model_path[1])
        detectors[1] = RNet
        ONet = Detector(O_Net, 48, 1, model_path[2])
        detectors[2] = ONet

        self.mtcnn_detector = MtcnnDetector(detectors=detectors, min_face_size=min_face_size,
                                       stride=stride, threshold=thresh, slide_window=slide_window)

    def cropface(self, frame):
        cropped_list = []

        i = 0

        image = np.array(frame)
        all_boxes, landmarks = self.mtcnn_detector.detect(image)
        # all_boxes,landmarks = self.mtcnn_detector.detect_face(test_data)
        # image = cv2.imread(imagepath)
        for bbox in all_boxes:
            corpbbox = [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])]
            if abs(corpbbox[3] - corpbbox[1]) > abs(corpbbox[2] - corpbbox[0]):
                n0 = int(0.5 * (corpbbox[2] + corpbbox[0]) - 0.5 * abs(corpbbox[3] - corpbbox[1]))
                n1 = corpbbox[1]
                n2 = int(0.5 * (corpbbox[2] + corpbbox[0]) + 0.5 * abs(corpbbox[3] - corpbbox[1]))
                n3 = corpbbox[3]
            else:
                n0 = corpbbox[0]
                n1 = int(0.5 * (corpbbox[3] + corpbbox[1]) - 0.5 * abs(corpbbox[2] - corpbbox[0]))
                n2 = corpbbox[2]
                n3 = int(0.5 * (corpbbox[3] + corpbbox[1]) + 0.5 * abs(corpbbox[2] - corpbbox[0]))
            # cropped = image[n1:n3, n0:n2]
            cropped = [int(n0), int(n1), int(n2), int(n3)]
            cropped_list.append(cropped)

            # cv2.rectangle(frame, (int(bbox[0]),int(bbox[1])),(int(bbox[2]),int(bbox[3])),(0,0,255))

        # cv2.imwrite("../data/test_result/%d.png" %(count),image)
        # cv2.imshow("image",frame)
        # cv2.waitKey(0)
        return all_boxes
        # return cropped_list


class DealRecord(threading.Thread):

	def __init__(self, start_time, end_time):
		threading.Thread.__init__(self, name = "GetPicture")
		self.start_time = start_time
		self.end_time = end_time

		self.frame_queue = Queue()
		self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		self.MTC = MTCNN_Crop_Face()

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
				# 缩小图片，加快处理速度
				self.frame_queue.put("fileover")
				break
			else:
				frame = cv2.resize(frame,(540,360))
				self.frame_queue.put(frame)
				# print("---- put frame.")

		print("---- get record finish.")
		self.capture.release()


	def dealRecord(self):
		frame_num = 0
		data = []
		
		file_name = "form %s to %s.txt"%(self.start_time, self.end_time)
		txt = open(file_name, "w")

		while 1:
			# get接口默认为阻塞接口，会一直等待数据
			frame = self.frame_queue.get()
			# cv2.imshow('record_raw', frame)
			# ha = hash(str(frame))

			if frame == "fileover":
				break

			frame_num += 1
			if (frame_num % 20 == 0) or (self.frame_queue.qsize() != 0):
				print("get frame %d. left %d"% (frame_num, self.frame_queue.qsize()))
			
			# 人脸检测
			faces = self.MTC.cropface(frame)

			for bbox in faces:
				cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255))

			cv2.imshow('record_deal',frame)
			txt.write(str(faces) + "\n")
			# txt.write(str(faces) + '  ' + str(ha) + "\n")

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



