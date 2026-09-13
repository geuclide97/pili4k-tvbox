# -*- coding: utf-8 -*-
"""
构建给 FongMi / CatVod 系壳使用的 drpy2 运行时。

背景：
  drpy2.min.js 在模块顶层就裸引用了 pdfh / pdfa / pd：
      const defaultParser={pdfh:pdfh,pdfa:pdfa,pd:pd};
  这三个函数原本由 TVBox 的 native 层注入。FongMi（com.fongmi.android.tv）
  不注入它们，导致加载该模块时直接抛
      QuickJSException: UnhandledPromiseRejectionException: 'pdfh' is not defined
  整个 spider 初始化失败 -> 站点零分类。

做法：
  1. 用 cheerio（drpy2 自己已经从 assets://js/lib/cheerio.min.js 引入）
     实现 pdfh / pdfa / pd，挂到 globalThis 上；
  2. 把 模板.js / gbk.js 的相对 import 换成绝对 URL（远程模块的相对解析不可靠）；
  3. 保持 assets:// 引用不变（FongMi 内置了逐字节相同的 cheerio / crypto-js）。

不定义 pdfl：drpy2 用 `typeof pdfl==="function"` 判定版本，定义它会切到
另一条 detail 分支，本规则不需要。
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'drpy2_final.js')
DST = os.path.join(HERE, 'repo_pili4k', 'lib', 'drpy2.min.js')

REPO = 'https://cdn.jsdelivr.net/gh/geuclide97/pili4k-tvbox@main'

SHIM = r'''/* ===== host shim: pdfh / pdfa / pd =====
 * drpy2 references pdfh/pdfa/pd as bare globals at module top level
 * (const defaultParser={pdfh:pdfh,pdfa:pdfa,pd:pd}).
 * TVBox injects them from native code; FongMi (com.fongmi.android.tv) does not,
 * so the module throws "ReferenceError: pdfh is not defined" on load and the
 * whole spider fails -> the site shows zero categories.
 * Implemented here with cheerio (already imported above).
 * Selector syntax: "sel1&&sel2&&...&&key", key = Text | Html | outerHtml | <attr>
 * Do NOT define pdfl: drpy2 uses typeof pdfl==="function" to switch versions.
 */
function __drpyHostHtml(html){
  if(html&&typeof html!=="string"){
    try{if(typeof html.rr==="function"){return html.rr(html.ele).toString()}}catch(e){}
    try{return String(html)}catch(e){return""}
  }
  return html==null?"":String(html)
}
function __drpyHostKey(node,key){
  key=(key||"Text").trim();
  var k=key.toLowerCase();
  if(k===""||k==="text"){return node.text()}
  if(k==="html"||k==="innerhtml"){return node.html()||""}
  if(k==="outerhtml"){return node.prop("outerHTML")||""}
  return node.attr(key)||""
}
function __drpyHostParts(parse){
  return String(parse||"").split("&&").map(function(s){return s.trim()}).filter(function(s){return s})
}
function __drpyHostPdfh(html,parse){
  try{
    var parts=__drpyHostParts(parse);
    if(!parts.length){return""}
    var $=cheerio.load(__drpyHostHtml(html));
    var key=parts[parts.length-1];
    var sels=parts.slice(0,-1);
    var cur;
    if(!sels.length){cur=$.root().children().first()}
    else{
      cur=$.root().find(sels[0]);
      for(var i=1;i<sels.length;i++){cur=cur.find(sels[i])}
      cur=cur.first()
    }
    return cur&&cur.length?__drpyHostKey(cur,key):""
  }catch(e){return""}
}
function __drpyHostPdfa(html,parse){
  try{
    var parts=__drpyHostParts(parse);
    if(parts.length<2){return[]}
    var $=cheerio.load(__drpyHostHtml(html));
    var key=parts[parts.length-1];
    var sels=parts.slice(0,-1);
    var out=[];
    if(sels.length===1){
      $.root().find(sels[0]).each(function(i,el){out.push(__drpyHostKey($(el),key))});
      return out
    }
    var parents=$.root().find(sels[0]);
    for(var i=1;i<sels.length-1;i++){parents=parents.find(sels[i])}
    parents.each(function(i,p){
      var n=$(p).find(sels[sels.length-1]).first();
      if(n.length){out.push(__drpyHostKey(n,key))}
    });
    return out
  }catch(e){return[]}
}
globalThis.pdfh=__drpyHostPdfh;
globalThis.pdfa=__drpyHostPdfa;
globalThis.pd=__drpyHostPdfh;
/* ===== end host shim ===== */
'''


def main():
    with io.open(SRC, encoding='utf-8') as f:
        js = f.read()

    # 1) 相对 import -> 绝对 URL（远程模块的相对解析不可靠）
    js = js.replace('from"../js/模板.js"', 'from"%s/js/模板.js"' % REPO)
    js = js.replace('from"./gbk.js"', 'from"%s/lib/gbk.js"' % REPO)

    # 2) 定位 import 块结束位置：最后一个 import ... ; 之后插入 shim
    m = None
    for m in re.finditer(r'import[^;]*;', js):
        pass
    if m is None:
        sys.exit('no import statement found')
    cut = m.end()
    patched = js[:cut] + '\n' + SHIM + js[cut:]

    # 3) 自检
    if patched.count('globalThis.pdfh=') != 1:
        sys.exit('shim insertion failed')
    if 'from"../js/' in patched or 'from"./' in patched:
        sys.exit('relative import still present')

    with io.open(DST, 'w', encoding='utf-8', newline='') as f:
        f.write(patched)

    print('import block ends at %d' % cut)
    print('wrote %s  (%d bytes)' % (DST, len(patched.encode('utf-8'))))


if __name__ == '__main__':
    main()
