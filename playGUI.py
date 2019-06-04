# -*- coding: UTF-8 -*-

##plt 同时显示多幅图像
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import requests
import Tkinter as tk
import playDemo
import time


FIGURE_X = 4
FIGURE_Y = 4
FIGURE_TOTAL = FIGURE_X * FIGURE_Y

IMG_SIZE_W = int(1280*0.35)
IMG_SIZE_H = int(720*0.35)
# URL = "http://127.0.0.1:8001/"
URL = "http://172.16.1.91:8001/"


class palyGUI():

    def __init__(self):
        self.pictures = []

    # 返回服务器最近的16张快照
    def get_snapshoot(self):
        print("get %s"%(URL))
        response = requests.get(URL)
        print("response %d"%(response.status_code))
        if response.status_code != 200:
            return
        
        result = []
        li = response.text.split("</a>\n")
        num = len(li[1:-1])
        for line in li[num - FIGURE_TOTAL + 1:-1]:
            temp = line.split(">")
            result.append(temp[-1])
            # print(temp[-1])
        
        for i in range(FIGURE_TOTAL):
            res = requests.get(URL + result[i])
            open(result[i], 'wb').write(res.content)

        return result

    def on_press(self, event):
        print("button click event")
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

    def show_picture_2(self):
        fig = plt.figure(figsize=(20,20)) #设置窗口大小
        fig.canvas.mpl_connect("button_press_event", self.on_press)
        plt.suptitle('SnapShoot') # 图片名称

        self.pictures = self.get_snapshoot()
        print(self.pictures)
        for i in range(FIGURE_TOTAL):
            img = Image.open(self.pictures[i])
            plt.subplot(FIGURE_X,FIGURE_Y,i+1)
            plt.title(self.pictures[i])
            plt.imshow(img)
            plt.axis('off')

        plt.show()

    def button_click(self, txt):
        print txt
        context = txt.split(".jpg")
        start_timeArray = time.strptime(context[0], "%Y%m%d_%H%M%S")
        start_timeStamp = time.mktime(start_timeArray)
        start_time = int((start_timeStamp -1) / 10) * 10
        end_time = start_timeStamp + 100
        start_time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(start_time))
        end_time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(end_time))

        # start_time = start_timeStamp -10
        # end_time = start_timeStamp + 100
        # start_time_str = time.strftime("%Y_%m_%d_%H_%M_00", time.localtime(start_time))
        # end_time_str = time.strftime("%Y_%m_%d_%H_%M_00", time.localtime(end_time))

        # print(start_time_str)
        # print(end_time_str)
        player = playDemo.playRecord(start_time_str, end_time_str)
        player.run()
        pass


    def show_picture(self):
        self.pictures = self.get_snapshoot()
        print(self.pictures)

        top = tk.Tk()
        top.title('SnapShoot')

        # 获取屏幕的宽度和高度，并且在高度上考虑到底部的任务栏，为了是弹出的窗口在屏幕中间
        screenwidth = top.winfo_screenwidth()
        screenheight = top.winfo_screenheight()
        # top.resizable(False, False) 
        
        frame_root = tk.LabelFrame(top)
        btn_list =[]
        for i in range(FIGURE_TOTAL):
            img = Image.open(self.pictures[i])
            img = img.resize( (IMG_SIZE_W,IMG_SIZE_H), Image.ANTIALIAS)
            bm = ImageTk.PhotoImage(img)
            button = tk.Button(frame_root, image=bm, text=self.pictures[i])
            button.image = bm
            button.config(command = lambda t=self.pictures[i]:  self.button_click(t))
            btn_list.append(button)
            x = i / FIGURE_X
            y = i % FIGURE_Y
            button.grid(row=x, column=y)
        
        frame_root.grid(row=0, column=0)
        top.mainloop()

            

if __name__ == "__main__":
    gui = palyGUI()
    gui.show_picture()

   
