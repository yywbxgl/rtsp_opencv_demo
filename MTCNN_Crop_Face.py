#coding:utf-8
import sys
sys.path.append('..')
import numpy as np
from Detection.MtcnnDetector import MtcnnDetector
from Detection.detector import Detector
from Detection.fcn_detector import FcnDetector

from train_models.mtcnn_model import P_Net, R_Net, O_Net
# from prepare_data.loader import TestLoader
import cv2
import os

class MTCNN_Crop_Face(object):
    def __init__(self):
        test_mode = "ONet"
        thresh = [0.9, 0.7, 0.7]
        min_face_size = 32
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
        # return all_boxes
        return cropped_list

def main():
    gt_imdb = []
    path = "./data2/data"

    MCF = MTCNN_Crop_Face()

    for item in os.listdir(path):
        gt_imdb.append(os.path.join(path,item))
    # test_data = TestLoader(gt_imdb)

    count = 0
    for imagepath in gt_imdb:
        print(imagepath)
        image = cv2.imread(imagepath)
        image = cv2.resize(image,(720,480))
        cv2.imshow("image", image)
        cv2.waitKey(100)
        input('Continue? <Y/N>')

        cropped_list = MCF.cropface(image)

        for bbox in cropped_list:
            cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)

        cv2.imwrite("./data/test_result/%d.png" % (count), image)
        cv2.imshow("image", image)
        cv2.waitKey(100)
        count += 1
        key = input('Next? <Y/N>')
        if key == 'N' or key == 'No' or key == 'n' or key == 'no':
            break
        else:
            print('next picture is from: ')

if __name__ == "__main__":
    main()
