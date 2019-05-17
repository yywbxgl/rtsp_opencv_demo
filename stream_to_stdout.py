# -*- coding: UTF-8 -*-

import numpy as np
import cv2
import sys


def deal_stream():
	# cap = cv2.VideoCapture(0)
	cap = cv2.VideoCapture("rtsp://admin:s65656645@172.16.1.29/cam/realmonitor?channel=1&subtype=0")

	# 打印视频相关参数，帧率，宽高
	if cap.isOpened():
		print cap.get(cv2.CAP_PROP_FPS)
		print cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		print cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

	face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

	while cap.isOpened():
		# Capture frame-by-frame
		ret, frame = cap.read()
		# cv2.imshow('get stream', frame)

		# Our operations on the frame come here
		# opencv读取的图片格式为bgr24 转为灰度图
		frame_temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# 直方图均匀化(改善图像的对比度和亮度)
		frame_temp = cv2.equalizeHist(frame_temp)	

		# 获取该图片中的各个人脸的坐标
		faces = face_cascade.detectMultiScale(frame_temp, 1.3, 5)
		# 人脸画框
		for (x, y, w, h) in faces:
			frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
			roi_gray = frame[y:y + h, x:x + w]
			roi_color = frame[y:y + h, x:x + w]
			eyes = eye_cascade.detectMultiScale(roi_gray)
			for (ex, ey, ew, eh) in eyes:
				cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

		# Display the resulting frame
		# cv2.imshow('process stream', frame)
		sys.stdout.write(frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()



if __name__ == "__main__":
	deal_stream()
