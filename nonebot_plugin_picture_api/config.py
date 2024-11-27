from pydantic import BaseModel, Extra
from nonebot.config import Config as NBConfig
import yaml
import nonebot
from pathlib import Path

config_path = Path('config/picture_api_config.yml')

CONFIG_TEMPLATE = {
    #key值设置为要触发的词
    'bs':[
        {'url': 'https://v2.api-m.com/api/baisi?return=302',# 在url字段后面写接口链接
        'is_proxy': False} # 是否使用代理,默认为False

        # 根据接口指定类型类型包括 image text json 如不写则默认为image
        # image指接口直接返回图片
        # text指接口返回链接
        # json指接口返回json字符串 ,返回json需指定path请参考以下json示例
    ],

    #也可以以"|"分隔设置多个触发词
    'hs|黑丝|heisi':[
        {'url': 'https://v2.api-m.com/api/heisi?return=302'},
        {'url': 'http://shanhe.kim/api/tu/hs.php'}
        # 可以采用这种格式进行一个关键词设置多个链接

    ],
    #返回json示例
    'ecy':[
        {'url': 'https://sex.nyan.xyz/api/v2/'}, #接口返回链接在 "data数组" 里面用 "[0]" 来指定数组的第几个值后再 ".url" 即可，最后必须指向图片链接
        {'url':'https://api.lolicon.app/setu/v2'}
    ],
    #返回text示例
    'meizi':[
    {'url': 'https://xiaobapi.top/api/xb/api/meizi.php'}
    ]
}

global_config = nonebot.get_driver().config
# 检查config文件夹是否存在 不存在则创建
if not Path("config").exists():
    Path("config").mkdir()
if not config_path.exists():
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(CONFIG_TEMPLATE, f, allow_unicode=True)  

with open(config_path,'r') as f:
    api_data = yaml.load(f,Loader=yaml.FullLoader)#读取yaml文件

try:
    class Config(BaseModel, extra=Extra.ignore, from_attributes=True):
        """Plugin Config Here"""
        
        api_data: dict = api_data
        global_config: NBConfig = global_config
except:
    class Config(BaseModel, extra=Extra.ignore):
        """Plugin Config Here"""
        
        api_data: dict = api_data   
        global_config: NBConfig = global_config