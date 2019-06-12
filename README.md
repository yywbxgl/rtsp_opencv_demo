# video_stream_convert

## 服务端

功能
```
1. AI Server 通过rtsp协议拉取前录像，进行AI处理（如MTCNN人脸检测），并保存AI处理结果。 
2. 保存特征数据的同时可保存快照，短视频等用于快速浏览与检索。
```

运行命令 (python3)
```
# 参数为需要处理的录像时间段，分别为开始时间和结束时间,处理后的数据保存在data和snapshot目录下
python AIServerDemo.py  2019_05_27_17_30_00  2019_05_27_17_40_00

# 不断查询最新的录像进行处理
python AIServerDemo.py live

# 打开HTTP服务器，用于客户端访问
cd data
python -m http.server  8000

cd snapshot
python -m http.server 8001
```

## 客户端

功能
```
1. 请求保存在AI Server的AI处理数据，用于快速检索。
2. 请求录像回放，将AI Sever的数据合入录像码流进行播放。
```

运行命令 (python3)
```
# 客户端Demo，查询快照展示
python playGUI.py

# 参数为需要处理的录像时间段，分别为开始时间和结束时间
python playDemo.py  2019_05_27_17_30_00  2019_05_27_17_35_00
```

## 其他

运行命令
```
# 播放录像
python getStream.py  2019_05_27_17_30_00  2019_05_27_17_35_00

# 播放实时流
python getStream.py  -1  -1
```