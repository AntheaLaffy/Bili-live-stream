import requests
import json
import sys
import time
from datetime import datetime

def get_room_info(room_id):
    """获取直播间基本信息"""
    # 第一步：获取房间基本信息（包含主播UID）
    room_url = "https://api.live.bilibili.com/room/v1/Room/get_info"
    # 第二步：获取主播详细信息（需要主播UID）
    user_url = "https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room"
    
    params = {"room_id": room_id}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://live.bilibili.com/{room_id}"
    }
    
    try:
        # 获取房间基本信息
        response = requests.get(room_url, params=params, headers=headers)
        response.raise_for_status()
        room_data = response.json()
        
        if room_data.get("code") != 0:
            print(f"获取房间信息失败: {room_data.get('message')}")
            return None
            
        room_info = room_data.get("data", {})
        uid = room_info.get("uid", "")
        
        # 获取主播详细信息
        user_params = {"roomid": room_id}  # 注意这里参数名是roomid不是room_id
        user_response = requests.get(user_url, params=user_params, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        uname = "未知主播"
        if user_data.get("code") == 0:
            user_info = user_data.get("data", {}).get("info", {})
            uname = user_info.get("uname", "未知主播")
        
        # 构造返回数据
        result = {
            "title": room_info.get("title", "未知标题"),
            "uname": uname,
            "uid": uid,
            "live_status": room_info.get("live_status", 0),
            "room_id": room_info.get("room_id", room_id)
        }
        
        return result
        
    except Exception as e:
        print(f"获取房间信息时出错: {e}")
        return None

def get_all_streams(room_id, qn=10000):
    """
    获取所有可用的直播流地址
    :param room_id: 直播间ID
    :param qn: 清晰度 (10000=原画)
    :return: 按协议分类的直播流字典
    """
    url = "https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo"
    params = {
        "room_id": room_id,
        "protocol": "0,1",  # 0=http_stream, 1=http_hls
        "format": "0,1,2",   # 0=flv, 1=ts, 2=fmp4
        "codec": "0,1",     # 0=h264, 1=h265
        "qn": qn,
        "platform": "web",
        "ptype": 16
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://live.bilibili.com/{room_id}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            print(f"获取直播流失败: {data.get('message')}")
            return None
            
        streams = data.get("data", {}).get("playurl_info", {}).get("playurl", {}).get("stream", [])
        
        result = {}
        for stream in streams:
            protocol = stream.get("protocol_name")
            if protocol not in result:
                result[protocol] = {}
            
            for fmt in stream.get("format", []):
                format_name = fmt.get("format_name")
                if format_name not in result[protocol]:
                    result[protocol][format_name] = {}
                
                for codec in fmt.get("codec", []):
                    codec_name = codec.get("codec_name")
                    urls = []
                    base_url = codec.get("base_url", "")
                    
                    for url_info in codec.get("url_info", []):
                        host = url_info.get("host", "")
                        extra = url_info.get("extra", "")
                        full_url = f"{host}{base_url}{extra}"
                        
                        # 提取URL中的expires参数
                        expires = None
                        if "expires=" in full_url:
                            try:
                                expires_str = full_url.split("expires=")[1].split("&")[0]
                                expires = int(expires_str)
                            except:
                                pass
                        
                        urls.append({
                            "url": full_url,
                            "expires": expires
                        })
                    
                    if urls:
                        result[protocol][format_name][codec_name] = urls
        
        return result if result else None
        
    except Exception as e:
        print(f"获取直播流时出错: {e}")
        return None

def display_streams(streams_data):
    """格式化显示所有直播流"""
    if not streams_data:
        print("没有获取到可用的直播流")
        return
    
    print("\n" + "="*80)
    print("重要提示：这些是直播流地址，浏览器可能无法直接播放，请使用媒体播放器软件")
    print("="*80)
    
    for protocol, formats in streams_data.items():
        print(f"\n{'='*60}")
        print(f"协议类型: {protocol.upper()}")
        print(f"{'='*60}")
        
        for format_name, codecs in formats.items():
            print(f"\n格式: {format_name.upper()}")
            print("-"*50)
            
            for codec, urls in codecs.items():
                print(f"\n编码: {codec.upper()}")
                for i, url_info in enumerate(urls, 1):
                    url = url_info["url"]
                    expires = url_info["expires"]
                    
                    # 显示有效期信息
                    expires_info = ""
                    if expires:
                        expires_time = datetime.fromtimestamp(expires).strftime("%Y-%m-%d %H:%M:%S")
                        current_time = time.time()
                        remaining = expires - current_time
                        expires_info = f" [有效期至: {expires_time} | 剩余: {int(remaining//60)}分{int(remaining%60)}秒]"
                    
                    print(f"{i}. {url}{expires_info}")

    #   外来api调用 -   7/23
def get_stream_info(room_id, qn=10000, include_urls=True, include_metadata=True):
    """
    获取直播流详细信息
    :param room_id: 直播间ID
    :param qn: 清晰度 (默认10000=原画)
    :param include_urls: 是否包含URL列表
    :param include_metadata: 是否包含元数据
    :return: 包含直播流详细信息的字典
    """
    # 检查房间状态
    room_info = get_room_info(room_id)
    if not room_info:
        return {"error": "无法获取房间信息"}
    
    # 检查直播状态
    if room_info.get("live_status") != 1:
        return {"error": f"房间 {room_id} 当前未在直播"}
    
    # 获取直播流数据
    streams_data = get_all_streams(room_id, qn)
    if not streams_data:
        return {"error": "无法获取直播流数据"}
    
    # 构建结果字典
    result = {
        "room_info": {
            "room_id": room_info.get("room_id"),
            "title": room_info.get("title"),
            "uname": room_info.get("uname"),
            "uid": room_info.get("uid"),
            "live_status": room_info.get("live_status")
        }
    }
    
    # 包含URL列表
    if include_urls:
        url_list = []
        for protocol, formats in streams_data.items():
            for format_name, codecs in formats.items():
                for codec, urls in codecs.items():
                    for url_info in urls:
                        if url_info["url"]:
                            url_list.append(url_info["url"])
        result["urls"] = url_list
    
    # 包含完整元数据
    if include_metadata:
        result["streams_metadata"] = streams_data
    
    # 提取关键参数
    key_params = []
    for protocol, formats in streams_data.items():
        for format_name, codecs in formats.items():
            for codec, urls in codecs.items():
                for i, url_info in enumerate(urls):
                    params = {
                        "index": i + 1,
                        "protocol": protocol,
                        "format": format_name,
                        "codec": codec,
                        "url": url_info["url"],
                        "expires": url_info.get("expires"),
                        "expires_time": datetime.fromtimestamp(url_info["expires"]).strftime("%Y-%m-%d %H:%M:%S") if url_info.get("expires") else None
                    }
                    key_params.append(params)
    
    result["streams"] = key_params
    
    return result

def main():
    try:
        print("Bilibili直播流抓取工具")
        print("="*60)
        
        while True:
            room_id = input("\n请输入Bilibili直播间ID (输入0退出): ").strip()
            
            if room_id == "0":
                print("程序退出，感谢使用！")
                break
                
            if not room_id.isdigit():
                print("请输入有效的数字房间ID")
                continue
            
            # 获取房间信息
            print("\n正在获取房间信息...")
            room_info = get_room_info(room_id)
            if not room_info:
                print("无法获取房间信息，请检查房间ID是否正确")
                continue
                
            print(f"\n房间标题: {room_info.get('title')}")
            print(f"主播名字: {room_info.get('uname')}")
            print(f"主播UID: {room_info.get('uid')}")
            print(f"直播状态: {'直播中' if room_info.get('live_status') == 1 else '未直播'}")
            
            if room_info.get("live_status") != 1:
                print("当前直播间未在直播")
                continue
                
            # 获取所有直播流
            print("\n正在获取直播流地址...")
            streams_data = get_all_streams(room_id)
            
            # 显示结果
            if streams_data:
                display_streams(streams_data)
                
                # 详细的播放器使用说明
                print("\n" + "="*80)
                print("如何播放这些直播流:")
                print("="*80)
                print("1. ffplay (FFmpeg):")
                print("   - 安装FFmpeg: https://ffmpeg.org/download.html")
                print("   - 在命令行中使用: ffplay \"流地址\"")
                print("   - 示例: ffplay \"https://example.com/stream.flv\"")
                print("\n2. VLC媒体播放器:")
                print("   - 下载VLC: https://www.videolan.org/vlc/")
                print("   - 打开VLC -> 媒体 -> 打开网络串流 -> 粘贴地址 -> 播放")
                print("\n3. PotPlayer:")
                print("   - 下载PotPlayer: https://potplayer.daum.net/")
                print("   - 打开PotPlayer -> 按F3 -> 粘贴地址 -> 确定")
                print("\n4. 其他播放器:")
                print("   - 大多数媒体播放器都支持打开网络流")
                print("\n注意:")
                print("- 直播流地址有有效期(显示在每条地址后面)，过期后需要重新获取")
                print("- 浏览器通常无法直接播放这些原始流媒体格式")
                print("- 如果地址失效，请重新运行此工具获取新地址")
                print("="*80)
            else:
                print("无法获取直播流地址")
            
            print("\n" + "="*80)
    
    except KeyboardInterrupt:
        print("\n用户中断操作，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {e}")
        input("按Enter键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()
