# video_stream_convert

通过rtsp协议拉取前端摄像头码流，通过opencv进行AI处理（如人脸检测），重新生成视频数据，并进行rtsp服务转发，用于后端设备（如视频录像机）或其他客户端拉流。

详细说明见我的笔记  
http://note.youdao.com/noteshare?id=53d7f3cf891fa7870e23879f4fc17cca


# 环境安装
1. 安装opencv
```
$ pip install --upgrade pip 
$ pip install wheel #如果确定已经安装了wheel就不用执行这条指令
$ pip install opencv-python #安装opencv 
$ pip install opencv-contrib-python #安装opencv的contrib扩展包
```

2. 安装vlc
```
sudo add-apt-repository ppa:videolan/master-daily 
sudo apt-get update 
sudo apt-get install vlc
```

3. 安装ffmpeg
```
sudo add-apt-repository ppa:djcj/hybrid
sudo apt-get update
sudo apt-get install ffmpeg
```

# 测试Camera拉流
可以安装VLC测试下是否正常拉流
```
cvlc "rtsp://admin:s65656645@172.16.1.29/cam/realmonitor?channel=1&subtype=0" //注意拉刘请求带引号 否则可能解析错误
```
拉流请求中admin 为账号 s65656645为密码 172.16.1.29为摄像头IP /cam/realmonitor?channel=1&subtype=0 为大华设备的rtsp拉流格式 channel为通道 subtype为主辅码流
显示如下


# 测试openCV人脸检测功能
使用opencv拉前端摄像头流，做AI处理（如人脸检测），并进行显示，
直接运行python stream_test.py 
运行效果如下，按q退出


# 搭建ffmpeg码流转发服务
后端设备如果接NVR(网络硬盘录像机)，需支持rtsp服务，
1. 启动 ffserver转发服务器
```
sudo vim /etc/ffserver.conf   # 修改ffserver配置如下， 见ffserver.conf
ffserver -f /etc/ffserver.conf
```

2. 将opencv处理后的视频推到ffserver
```
python stream_to_stdout.py | ffmpeg -f rawvideo -pixel_format bgr24 -video_size 1280x720 -framerate 10 -i - http://localhost:8090/feed1.ffm

//pixel_format 为opencv输出的图片格式，为bgr24 video_size 为图片大小 framerate 为帧率
```

3. 使用VLC拉流
可以同时拉camera与ffserver的码流，对比查看,命令分别如下
```
cvlc "rtsp://admin:s65656645@172.16.1.29/cam/realmonitor?channel=1&subtype=0"
cvlc "rtsp://127.0.0.1:8554/test.h264"
```
运行效果如下 延时大约90秒