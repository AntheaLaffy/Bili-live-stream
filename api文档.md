#  API 文档
- 如果你的项目需要这个功能
- 且不想自己写代码的的话可以直接使用我的脚本

## API核心函数

```python
def get_stream_info(room_id, qn=10000, include_urls=True, include_metadata=True):

```

## 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| room_id | int/str | 必填 | Bilibili 直播间 ID |
| qn | int | 10000 | 视频清晰度选项: 10000=原画, 20000=4K, 400=流畅, 250=极速, 150=高清 |
| include_urls | bool | True | 是否在返回结果中包含扁平化的 URL 列表 |
| include_metadata | bool | True | 是否包含完整的直播流元数据 |


## 字段说明

### room_info 对象
- `room_id`: 直播间ID
- `title`: 直播间标题
- `uname`: 主播名称
- `uid`: 主播用户ID
- `live_status`: 直播状态 (1=直播中, 其他=未直播)

### urls 数组
当`include_urls=True`时存在，包含所有可用直播流URL的扁平化列表

### streams_metadata 对象
当`include_metadata=True`时存在，原始直播流数据结构，按协议→格式→编码层级组织

### streams 数组
包含每个流详细信息的字典列表：
- `index`: 序号
- `protocol`: 协议类型 (http_stream, http_hls)
- `format`: 流格式 (flv, ts, fmp4)
- `codec`: 视频编码 (h264, h265)
- `url`: 完整流地址
- `expires`: 过期时间戳
- `expires_time`: 格式化的过期时间

## 错误类型

| 错误信息 | 说明 |
|---------|------|
| "无法获取房间信息" | 房间ID无效或API请求失败 |
| "房间 {room_id} 当前未在直播" | 指定房间未开播 |
| "无法获取直播流数据" | 直播流API请求失败 |

## 使用示例

```python
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
```


## 清晰度参考(qn参数)

| 值 | 清晰度 | 说明 |
|----|--------|------|
| 10000 | 原画 | 最高质量 |
| 20000 | 4K | 超高清 |
| 400 | 流畅 | 低带宽适用 |
| 250 | 极速 | 最低码率 |
| 150 | 高清 | 平衡画质 |
| 30000 | 杜比视界 | 需设备支持 |

注：不同直播间支持的清晰度可能不同
