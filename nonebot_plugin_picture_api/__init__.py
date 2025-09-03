from nonebot import get_driver
from nonebot import on_fullmatch, on_message
from nonebot.rule import Rule
from nonebot.adapters import Event
from .config import Config, config_path
from nonebot.adapters.onebot.v11 import MessageSegment
import httpx, yaml, asyncio, json
from random import choice
from nonebot.plugin import PluginMetadata
from nonebot.params import ArgPlainText, EventPlainText
from nonebot.permission import SUPERUSER

from nonebot import require
require("nonebot_plugin_htmlrender")


__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-picture-api",
    description="一款可以自由增删图片指令和api的插件",
    usage="配置好后发送相应的指令即可，配置文件在cofig/picture_api_config",
    type="application",
    homepage="https://github.com/Q1351998764/nonebot-plugin-picture-api",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

try:
    plugin_config = Config.parse_obj(get_driver().config)
except:
    plugin_config = Config.model_validate(get_driver().config)
cmds_config = plugin_config.api_data


# 构建指令列表和正则表达式
cmds = []
for cmd in cmds_config:
    if '|' in cmd:
        cmds += cmd.split('|')
    else:
        cmds.append(cmd)

# 动态完全匹配规则：始终基于当前 cmds 列表判断是否命中
async def _dynamic_fullmatch_rule(event: Event):
    text = str(event.get_message()).strip()
    return text in cmds

pic = on_message(rule=Rule(_dynamic_fullmatch_rule), priority=10, block=True)
jktj = on_fullmatch(["图片接口统计","图片接口","图片api统计","图片api"], priority=10, block=True)
add_api = on_fullmatch(["添加图片接口","添加图片api"], priority=10, block=True, permission=SUPERUSER)

lock = asyncio.Lock()


@pic.handle()
async def handle_function(msg = EventPlainText()):
    # 只处理命中指令的消息
    for cmd in cmds_config:
        if msg in cmd:
            urls = cmds_config[cmd]
            url_dic = choice(urls)
            url = url_dic.get('url')
            is_proxy = url_dic.get('is_proxy', False)
            res = await get_pic(url, is_proxy)
            if res:
                await pic.finish(MessageSegment.image(res.content))
            else:
                # 轮询所有接口
                for url_dic in urls:
                    url = url_dic.get('url')
                    is_proxy = url_dic.get('is_proxy', False)
                    res = await get_pic(url, is_proxy)
                    if res:
                        await pic.finish(MessageSegment.image(res.content))
                        return
                await pic.finish(f"{msg}接口已全部失效，请稍后再试或更换新的接口")
            return

async def get_pic(url, is_proxy=False):
    '''
    获取图片
    
    params
    ----

    url: 图片api的url

    is_proxy: 是否使用代理
    '''
    proxies = None
    if is_proxy:
        try:
            proxy = plugin_config.global_config.proxies_http
        except:
            await pic.finish("请先在.env中配置代理")
        proxies = {
            "all://": proxy,
        }
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36",
    }
    async with httpx.AsyncClient(proxy=proxies) as client:
        try:
            res = await client.get(url, follow_redirects=True, headers=header)
        except:
            return 0
        else:
            if res.status_code != 200:
                return 0
            content_type = res.headers.get('Content-Type', '').lower()
            is_image = content_type.startswith('image/')
            is_text = content_type.startswith('text/')
            is_json = content_type.startswith('application/json')
            
            if is_image:
                if res.status_code == 200:
                    return res
                else:
                    return 0

            elif is_text:

                # 判断是否是json
                try:
                    resjson = json.loads(res.text)
                    picture_urls = get_url_from_json(resjson)
                    if picture_urls:
                        picture_url = choice(picture_urls)
                    else:
                        return 0
                    picture = await client.get(picture_url, follow_redirects=True, headers=header)
                    if picture.status_code == 200:
                        return picture
                    else:
                        return 0
                except:
                    picture_url = res.text
                    if not res.text.startswith('http://') and not res.text.startswith('https://'):
                        picture_url = 'https://' + res.text
                        
                    # 判断是否是image
                    try:
                        picture = await client.get(picture_url, follow_redirects=True, headers=header)
                        if picture.status_code == 200:
                            return picture
                        else:
                            return 0
                    except:
                        return res
                
            elif is_json:
                picture_urls = get_url_from_json(res.json())
                if picture_urls:
                    picture_url = choice(picture_urls)
                else:
                    return 0
                picture = await client.get(picture_url, follow_redirects=True, headers=header)
                if picture.status_code == 200:
                    return picture
                else:
                    return 0



def get_url_from_json(json_data):
    '''
    从json中获取所有的url
    
    :params json_data: json数据
    :return url_list: url列表
    '''
    url_list = []

    def traverse_json(data):
        if isinstance(data, str):
            # 判断是否为链接
            if data.startswith("http://") or data.startswith("https://"):
                url_list.append(data)
        elif isinstance(data, dict):
            for value in data.values():
                traverse_json(value)
        elif isinstance(data, list):
            for item in data:
                traverse_json(item)

    traverse_json(json_data)
    return url_list

@jktj.handle()
async def pic_jktj():
    msg = ''
    for i in cmds_config:
        msg = msg + i + "\n"
    # 去除最后一个换行符
    msg = msg[:-1]
    await jktj.finish(msg)


@add_api.got("pic_name", prompt="请输入调用词")
@add_api.got("pic_api", prompt="请输入图片接口")
async def add_pic_api(pic_api:str = ArgPlainText(), pic_name:str = ArgPlainText()):
    global cmds
    # 检查api
    res = await get_pic(pic_api)
    if not res:
        await add_api.finish("接口测试失败，请稍后再试或更换接口")

    async with lock:
        # 检测调用词是否已存在
        found = False
        for cmd in cmds_config:
            if pic_name in cmd:
                api_info = cmds_config.get(cmd)
                api_info.append({"url":pic_api})
                found = True
                break
        if not found:
            cmds.append(pic_name)
            cmds_config[pic_name] = [{"url":pic_api}]
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(cmds_config, f, allow_unicode=True)

    await add_api.send("添加成功")

