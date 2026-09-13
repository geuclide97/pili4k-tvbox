# pili4k-tvbox

TVBox 点播配置：`霹雳⚡4K` 线路。

## 这是什么

从 Android 应用「霹雳4k启航」（`com.pilia1.qiji` v5.8.8）中提取的内置点播线路规则。
该线路本质是一个 **drpy2 规则脚本**，调用腾讯视频的公开目录接口，不自行托管任何影视文件。

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
  "api": "https://cdn.jsdelivr.net/gh/geuclide97/pili4k-tvbox@main/lib/drpy2.min.js",
  "ext": "https://cdn.jsdelivr.net/gh/geuclide97/pili4k-tvbox@main/pili4k.js",
  "searchable": 1,
  "quickSearch": 1,
  "filterable": 1,
  "changeable": 1,
  "timeout": 30
}
```

## 文件

| 文件 | 说明 |
|---|---|
| `config.json` | TVBox 总配置 |
| `pili4k.js` | 霹雳4K 规则本体（drpy2 格式） |
| `lib/drpy2.min.js` | drpy2 运行时，规则的解释器 |
| `lib/jsencrypt.js` | drpy2 依赖 |
| `lib/gbk.js` | drpy2 依赖 |
| `js/模板.js` | drpy2 依赖 |

## 关键：`api` 与 `ext` 不能搞反

这是最容易踩的坑。`type: 3` 的站点里：

- `api` → **运行时**（`lib/drpy2.min.js`）
- `ext` → **规则**（`pili4k.js`）

如果写成 `"api": "./pili4k.js"`（把规则当运行时），TVBox 会把规则文件当成 ESM spider 模块去 `import`，
而规则里没有 `__jsEvalReturn` 也没有 `export default`，结果就是**配置加载成功、站点名能显示、但一个分类都没有**。

同理，`lib/` 与 `js/` 的目录层级也不能改。`drpy2.min.js` 里有相对导入：

```js
import cheerio from "assets://js/lib/cheerio.min.js";   // 由 App 自带
import "assets://js/lib/crypto-js.js";                  // 由 App 自带
import 模板 from "../js/模板.js";                        // 本仓库 js/模板.js
import { gbkTool } from "./gbk.js";                     // 本仓库 lib/gbk.js
```

少任何一个文件，drpy2 模块加载失败 → 同样没有分类。

## 关于 `lib/drpy2.min.js` 的来源（安全说明）

本仓库的 `lib/drpy2.min.js` **不是**上游原版，而是**清理过**的版本。

规则里用到 `$js.toString(() => {...})`，它要求运行时提供 `$js`，把箭头函数转成 drpy2 认识的
`js:` 前缀字符串：

```js
const $js = { toString(func) {
    return func.toString().replace(/^\(\)(\s+)?=>(\s+)?\{/, "js:").replace(/\}$/, "");
}};
```

上游 `hjdhnx/dr_py@main/libs/drpy2.min.js`（2024-04 构建）**没有 `$js`**，直接用它会导致
`$js is not defined`，`一级` 函数永远不执行，退化成 HTML 选择器解析 → 依然没有内容。

而网上流传的某些镜像版（例如 `yzsczx/tvboxjs` 的 `lib/drpy2.min.js`，66881 字节）虽然带 `$js`，
但**被注入了 5 个第三方远程 import**：

```js
import "https://down.nigx.cn/qu.ax/cLFE.js";
import "https://down.nigx.cn/qu.ax/kOUW.js";
import "https://down.nigx.cn/qu.ax/ucoN.js";
import 模板 from "https://down.nigx.cn/qu.ax/XUKQ.js";
import { gbkTool } from "https://down.nigx.cn/qu.ax/wYCz.js";
```

这是典型的供应链注入——运行时会静默加载第三方脚本。本仓库的做法是：保留 `$js`，
把上面 5 行替换回本地依赖：

```js
import 模板 from "../js/模板.js";
import { gbkTool } from "./gbk.js";
```

清理后文件 66707 字节，`down.nigx.cn` 引用数为 0，sha1 前 12 位 `cde9358bc0b9`。

**建议自行复核**：

```bash
grep -c "down.nigx.cn" lib/drpy2.min.js   # 应为 0
grep -o 'import[^;]*' lib/drpy2.min.js    # 只应出现 assets:// 与本地相对路径
```

## 对原规则的改动

除上述运行时清理外，`pili4k.js` 相对 App 内原始规则有 **3 处搜索逻辑修复**。
原规则在通用 TVBox 里搜索恒为 0 条，原因有两个：

1. 搜索接口返回的标题带 `<em>` 高亮标签（如 `<em>剑来</em>第三季定档`），
   原 `isMainContent()` 见到 `<em>` 直接丢弃 → 所有结果被过滤。
2. 原 `isQQPlatform()` 要求 `site.enName === '霹雳⚡4k'`，而接口返回的 `playSites` 是空数组
   → `[].some(...)` 恒为 `false` → 所有结果被过滤。

改动内容：

- `isMainContent()`：先 `title.replace(/<\/?em>/g, '')` 再判断关键词。
- `isQQPlatform()`：`playSites` 为空数组时视为通过；同时接受 `enName` 为 `qq`。
- 入列表时对 `title` 剥离 `<em>` 标签，避免标题里带标签。

目录、详情、播放逻辑未改动。

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

## 已验证

用 Node 加载本仓库的 `lib/drpy2.min.js` + `pili4k.js`，stub 掉 TVBox 宿主能力后实测：

| 调用 | 结果 |
|---|---|
| `home()` | 返回 7 个分类 + filters |
| `category('100173','1')` | 21 条（出入平安 / 特立独行 / 蜂鸟行动 …） |
| `search('剑来','1')` | 14 条（剑来第三季定档 / 《剑来》陈平安这身红色皮衣…） |

## 已知限制

- **播放链路**：规则输出的条目初始是腾讯视频网页 URL，由规则的 `lazy` 段或 TVBox 解析链
  生成可播放地址。规则本身不固化 m3u8 直链。
- **需要 JS 引擎**：`type: 3` 的 drpy 规则要求播放器支持 ESM import 的 JS Spider。
  已确认 `com.fongmi.android.tv` v5.6.3 与 `com.yuanbaotv.tvbox` v1.0.2 可用。
- **上游可用性**：腾讯接口与规则服务器都可能变动。分类空白时先确认接口是否仍可访问。
- **来源**：规则原件托管在第三方服务器 `http://8.148.229.212:802/霹雳4ka1/lib/霹雳xintx.js`，
  本仓库为其解压副本。版权归原作者，此处仅作备份与自用。

## 免责声明

仅供学习与技术研究使用，请勿用于商业用途。所有影视内容版权归原权利人所有，
本仓库不存储、不分发任何影视文件。请在 24 小时内删除。
