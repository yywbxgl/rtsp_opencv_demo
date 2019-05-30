# -*- coding: UTF-8 -*-

##plt 同时显示多幅图像
import os
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import requests
import Tkinter as tk


FIGURE_X = 4
FIGURE_Y = 4
FIGURE_TOTAL = FIGURE_X * FIGURE_Y
URL = "http://127.0.0.1:8001/"
# URL = "http://172.16.3.35:8001/"


class palyGUI():

    def __init__(self):
        self.pictures = []

    # 返回服务器最近的16张快照
    def get_snapshoot(self):
        response = requests.get(URL)
        print("get %s  %d"%(URL, response.status_code))
        if response.status_code != 200:
            return
        result = []
        li = response.text.split("</a>\n")
        num = len(li[1:-1])
        for line in li[num -15:-1]:
            temp = line.split(">")
            result.append(temp[-1])
            # print(temp[-1])
        
        for i in range(16):
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

    def show_picture(self):

        self.pictures = self.get_snapshoot()
        print(self.pictures)

        top = tk.Tk()
        top.title('SnapShoot')

        # 获取屏幕的宽度和高度，并且在高度上考虑到底部的任务栏，为了是弹出的窗口在屏幕中间
        screenwidth = top.winfo_screenwidth()
        screenheight = top.winfo_screenheight() - 100
        # top.resizable(False, False) 
        
        frame_root = tk.LabelFrame(top)

        for i in range(FIGURE_TOTAL):
            img = Image.open(self.pictures[i])
            img = img.resize( (520,320), Image.ANTIALIAS)
            bm = ImageTk.PhotoImage(img)
            label = tk.Label(frame_root, image=bm, text=self.pictures[i])
            label.image = bm
            x = i / 4
            y = i % 4
            label.grid(row=x, column=y)

        frame_root.grid(row=0, column=0)
        top.mainloop()

            

if __name__ == "__main__":
    gui = palyGUI()
    gui.show_picture()

   
