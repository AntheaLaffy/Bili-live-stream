from bili_live_stream import get_stream_info

# 获取直播间12345的直播流信息
result = get_stream_info(room_id=12345)

if "error" in result:
    print(f"错误: {result['error']}")
else:
    print(f"主播: {result['room_info']['uname']}")
    print(f"标题: {result['room_info']['title']}")
    
    # 获取第一个流地址
    first_stream = result["streams"][0]
    print(f"推荐播放地址: {first_stream['url']}")
    print(f"有效期至: {first_stream['expires_time']}")
    
    # 获取所有URL
    for i, url in enumerate(result["urls"], 1):
        print(f"{i}. {url}")