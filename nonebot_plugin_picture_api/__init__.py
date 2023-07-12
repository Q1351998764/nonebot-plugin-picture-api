from nonebot import get_driver
from nonebot import on_fullmatch
from .config import Config
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import Fullmatch
import httpx
from random import choice
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-picture-api",
    description="一款可以自由增删图片指令和api的插件",
    usage="配置好后发送相应的指令即可，配置文件在cofig/picture_api_config",
    type="application",
    homepage="https://github.com/Q1351998764/nonebot-plugin-picture-api",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
plugin_config = Config.parse_obj(get_driver().config)
cmds_config = plugin_config.data

cmds = []
for cmd in cmds_config:
    if '|' in cmd:
        cmds = cmds + (cmd.split('|'))
    else:
        cmds.append(cmd)

pic = on_fullmatch(cmds, priority=10, block=True)

@pic.handle()
async def handle_function(arg: str = Fullmatch()):
    for cmd in cmds_config:
        if arg in cmd:
            urls = cmds_config[cmd] 
            url_dic = choice(urls)
            url = url_dic.get('url')
            is_proxy = False
            if url_dic.get('is_proxy'):
                is_proxy = url_dic['is_proxy']
            await get_pic(url, is_proxy)
            break
    return

async def get_pic(url, is_proxy=False):
    '''
    获取图片
    
    params
    ----

    url: 图片api的url

    is_proxy: 是否使用代理

    path: json的路径，例如：data[0].url
    '''
    proxies = None
    if is_proxy:
        try:
            proxy = plugin_config.proxies_http
        except:
            await pic.finish("请先在.env中配置代理")
        proxies = {
            "all://": proxy,
        }
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36",
    }
    async with httpx.AsyncClient(proxies=proxies) as client:
        res = await client.get(url, follow_redirects=True, headers=header)
        
        content_type = res.headers.get('Content-Type', '').lower()
        is_image = content_type.startswith('image/')
        is_text = content_type.startswith('text/')
        is_json = content_type.startswith('application/json')
        
        if is_image:
            await pic.send(MessageSegment.image(res.content))
        elif is_image or is_text:
            if not res.text.startswith('http://') and not res.text.startswith('https://'):
                picture_url = 'https://' + res.text
            picture = await client.get(picture_url)
            await pic.send(MessageSegment.image(picture.content))
        elif is_json:
            picture_url = choice(get_url_from_json(res.json()))
            picture = await client.get(picture_url)
            await pic.send(MessageSegment.image(picture.content))

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