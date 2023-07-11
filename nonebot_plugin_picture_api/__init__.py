from nonebot import get_driver
from nonebot import on_fullmatch
from .config import Config
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import Fullmatch
import httpx
from random import choice

plugin_config = Config.parse_obj(get_driver().config)
cmds_config = plugin_config.data

cmds = []
for i in cmds_config:
    if '|' in i:
        cmds = cmds + (i.split('|'))
    else:
        cmds.append(i)

pic = on_fullmatch(cmds, priority=10, block=True)
print(cmds_config)
@pic.handle()
async def handle_function(arg: str = Fullmatch()):
    for i in cmds_config:
        if arg in i:
            urls = cmds_config[i] 
            url_dic = choice(urls)
            url = url_dic.get('url')
            api_type = 'image'
            is_proxy = False
            path = None
            if url_dic.get('type'):
                api_type = url_dic['type']
            if url_dic.get('is_proxy'):
                is_proxy = url_dic['is_proxy']
            if url_dic.get('path'):
                path = url_dic['path']
            await get_pic(url, api_type, is_proxy, path)
            break
    return

async def get_pic(url, api_type, is_proxy=False, path=None):
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
    async with httpx.AsyncClient(proxies=proxies) as client:
        res = await client.get(url,follow_redirects=True,headers=header)
        if api_type == 'image':
            await pic.send(MessageSegment.image(res.content))
        elif api_type == 'text':
            picture_url = res.text
            picture = await client.get(picture_url)
            await pic.send(MessageSegment.image(picture.content))
        elif api_type == 'json':
            picture_url = await from_json_get_url(res.json(), path)
            picture = await client.get(picture_url)
            await pic.send(MessageSegment.image(picture.content))

async def from_json_get_url(json_dict,str_path):
    res = str_path.split('.')
    res_list = []
    url = json_dict
    for i in res:
        i = i.split('[')
        for j in i:
            j = j.strip(']')
            res_list.append(j)

    for i in res_list:
        if i.isdigit():
            i = int(i)
        url = url[i]
    return url
