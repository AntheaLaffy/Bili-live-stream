# Bili-live-stream
一个简陋的哔哩哔哩直播视频流获取脚本，大佬勿入

## 使用者文档
### 功能特点

- 🚀 获取Bilibili直播间的基本信息（标题、主播名、直播状态等）
- 📺 抓取多种协议的直播流地址（HTTP-FLV、HLS等）
- 🔍 支持多种视频格式（FLV、TS、FMP4）和编码（H.264、H.265）
- ⏱️ 显示直播流地址的有效期和剩余时间
- 🛡️ 自动处理请求头和用户代理，避免被检测
- 📋 提供详细的播放器使用指南


#### 安装依赖
```bash
pip install requests
```
#### 运行程序
```bash
python bili-live-stream.py
```

## 开发者文档
原理：使用哔哩哔哩的api调取必要参数，拼接形成url
- api接口
  房间基本信息接口：https://api.live.bilibili.com/room/v1/Room/get_info                     👉房间标题，ID
  主播信息接口：https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room      👉主播名称，ID
  支持参数：房间号（必填）
  
  视频流接口：https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo        👉返回嵌套字典结构：协议 -> 格式 -> 编码 -> URL列表
  支持参数:
  > protocol：流协议（HTTP流/HLS）
  > 
  > format：格式（FLV/TS/FMP4）
  > 
  > codec：编码（H.264/H.265）
  > 
  > qn=10000：原画清晰度
  
