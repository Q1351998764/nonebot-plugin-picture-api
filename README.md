<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-picture-api

_✨ 一款可以自由增删图片指令和api的插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Q1351998764/nonebot-plugin-picture-api.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-picture-api">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-picture-api.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>


## 📖 介绍

在我调用各种图片api的时候，觉得每个api取一个指令并写一个小插件太麻烦了，因此写了本插件，只需配置yml即可增添图片api以及触发指令，如下图所示：

![image](https://github.com/Q1351998764/nonebot-plugin-picture-api/assets/57926506/6bf57db6-e96f-40a5-a04f-287c525d6db4)


## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-picture-api

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-picture-api
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-picture-api"]

</details>

## ⚙️ 配置

本插件的配置在bot根目录下的config文件夹下，名为picture_api_config.yml，该文件会在插件第一次运行时自动生成。其内容如同介绍中的截图所示。
写法如下所示：


    bs|白丝:
      - url: https://v2.api-m.com/api/baisi?return=302
        is_proxy: false
        type: image


其中，bs|白丝 代表api的触发指令，用"bs"或者是"白丝"均可触发。url后跟api；is_proxy代表是否使用代理，可不写，默认false；type代表该api是否直接返回图片，可不写，默认为image

也可在一个关键词下设置多个url，如下所示：


    hs|黑丝|heisi:
      - url: https://v2.api-m.com/api/heisi?return=302
      - url: http://shanhe.kim/api/tu/hs.php

其中，is_proxy与image均没写，采用默认值false和image

如果api返回是json，如下所示：

    ecy:
      - url: https://api.lolicon.app/setu/v2
        path: data[0].urls.original
        type: json
        is_proxy: true

其中 https://api.lolicon.app/setu/v2 接口返回的json格式如下：

{"error":"","data":[{"pid":75108340,"p":0,"uid":106843,"title":"下着の玉藻","author":"福田シュウシ","r18":false,"width":1430,"height":2000,"tags":["玉藻の前(Fate)","玉藻前（Fate）","キャス狐","C狐","Fate/GrandOrder","命运－冠位指定","下着","内衣","パンツ","内裤","おっぱい","欧派","高品質パンツ","高品质内裤","ブラジャー","胸罩","ぱんつ","胖次"],"ext":"png","aiType":0,"uploadDate":1559919601000,"urls":{"original":"https://i.pixiv.re/img-original/img/2019/06/08/00/00/01/75108340_p0.png"}}]}

path后就需要跟路径data[0].urls.original，指向最终图片的url，注意：返回格式为json的api，必须要写path，并最终指向图片url

如果api返回的是单一个图片链接，配置如下所示：

    meizi:
      - url: https://xiaobapi.top/api/xb/api/meizi.php
        type: text

上面的这个接口貌似收费了，这种直接返回图片url的接口不太好找，大体是这么个意思。

一个关键词下可以设置多个url，并且返回不同类型的url也可以混合设置，如下所示：

    美腿:
      - url: https://api.f4team.cn/API/meizi/
        type: json
        path: text
      - url: http://www.ggapi.cn/api/legs

在上面的配置中，指令"美腿"对应了两个url，第一个url返回json格式，第二个url直接返回图片。注意：第一个api返回的是json格式，其中指向图片url的path恰好是text，并不是说第一个api返回的是text格式。

大概配置就这样。

## 🎉 使用
配置完后直接对机器人发送配置的指令即可，机器人将随机调用该指令下的一个接口。
