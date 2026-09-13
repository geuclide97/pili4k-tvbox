# pili4k-tvbox

TVBox 点播配置：`霹雳⚡4K` 线路。

## 这是什么

从 Android 应用「霹雳4k启航」（`com.pilia1.qiji` v5.8.8）中提取的内置点播线路规则。
该线路本质是一个 QuickJS 规则脚本，调用腾讯视频的公开目录接口，不自行托管任何影视文件。

## 快速使用

TVBox 配置地址填入：

```
https://cdn.jsdelivr.net/gh/geuclide97/pili4k-tvbox@main/config.json
```

或在 TVBox 内手动添加站点：

```json
{
  "key": "pili4k",
  "name": "霹雳⚡4K",
  "type": 3,
  "api": "https://cdn.jsdelivr.net/gh/geuclide97/pili4k-tvbox@main/pili4k.js",
  "searchable": 1,
  "quickSearch": 1,
  "filterable": 1,
  "timeout": 30,
  "playerType": 0
}
```

## 文件

| 文件 | 说明 |
|---|---|
| `config.json` | TVBox 总配置，`api` 使用 `./pili4k.js` 相对路径，换仓库不用改 |
| `pili4k.js` | 霹雳4K QuickJS 规则本体 |

`config.json` 里的 `"api": "./pili4k.js"` 依赖 TVBox 的 `fixContentPath()`：加载配置时会把
`"./` 展开为配置 URL 所在目录。所以两个文件必须放在同一目录下，且不能改名。

## 线路用到的上游接口

| 用途 | 接口 |
|---|---|
| 分类/推荐目录 | `POST https://pbaccess.video.qq.com/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData` |
| 详情 | `https://node.video.qq.com/x/api/float_vinfo2?cid={cid}` |
| 搜索 | `POST https://pbaccess.video.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch` |
| 剧集列表 | `https://s.video.qq.com/get_playsource?id={id}&plat=2&type=4&data_type=3&range={range}&video_type=10&plname=qq&otype=json` |
| 单集元数据 | `https://union.video.qq.com/fcgi-bin/data?otype=json&tid=1804&appid=20001238&appkey=6c03bbe9658448a4&union_platform=1&idlist={vid}` |

分类 ID：

| type_id | 名称 |
|---|---|
| 100113 | 霹雳⚡4K电视剧 |
| 100173 | 霹雳⚡4K电影 |
| 100109 | 霹雳⚡4K综艺 |
| 100105 | 霹雳⚡4K纪录片 |
| 100119 | 霹雳⚡4K动漫 |
| 100150 | 霹雳⚡4K少儿 |
| 110755 | 霹雳⚡4K短剧 |

## 已知限制

- **播放链路**：规则输出的条目初始是腾讯视频网页 URL，由规则的 `lazy` 阶段或 TVBox 解析链
  生成可播放地址。规则本身不固化 m3u8 直链。
- **规则格式**：`pili4k.js` 是 drpy 风格规则（`var rule = {...}`），需要播放器内置 drpy 或
  QuickJS JS-Spider 支持。已验证 `com.yuanbaotv.tvbox` v1.0.2 含 `libquickjs.so` 与
  `__JS_SPIDER__`。
- **上游可用性**：腾讯接口与第三方规则服务器都可能变动。分类空白时先确认接口是否仍可访问。
- **来源**：规则原件托管在第三方服务器 `http://8.148.229.212:802/霹雳4ka1/lib/霹雳xintx.js`，
  本仓库为其解压副本。版权归原作者，此处仅作备份与自用。

## 免责声明

仅供学习与技术研究使用，请勿用于商业用途。所有影视内容版权归原权利人所有，
本仓库不存储、不分发任何影视文件。请在 24 小时内删除。
