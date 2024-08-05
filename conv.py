import requests

def uigf24p(old_file, output):
    output["hk4e"] = [
        {
            "uid": old_file["info"]["uid"],
            "timezone": old_file["info"]["region_time_zone"],
            "lang": old_file["info"]["lang"],
            "list": old_file["list"],
        }
    ]
    return output


def srgf(old_file, output):
    output["hkrpg"] = [
        {
            "uid": old_file["info"]["uid"],
            "timezone": old_file["info"]["region_time_zone"],
            "lang": old_file["info"]["lang"],
            "list": old_file["list"],
        }
    ]
    return output


def uigf23(old_file, output):
    prefix = int(old_file["info"]["uid"][-9])
    if 1 <= prefix and prefix <= 5 or prefix == 8 or prefix == 9:
        timezone = 8
    elif prefix == 6:
        timezone = -5
    elif prefix == 7:
        timezone = 1

    output["hk4e"] = [
        {
            "uid": old_file["info"]["uid"],
            "timezone": timezone,
            "lang": old_file["info"]["lang"],
            "list": old_file["list"],
        }
    ]
    return output

def uigf22(old_file, output):
    
    lang_map = {
        'zh-cn':'chs',
        'zh-tw':'cht',
        'de-de':'de',
        'en-us':'en',
        'ja-jp':'jp',
        'ru-ru':'ru'
    }
    
    prefix = int(old_file["info"]["uid"][-9])
    if 1 <= prefix and prefix <= 5 or prefix == 8 or prefix == 9:
        timezone = 8
    elif prefix == 6:
        timezone = -5
    elif prefix == 7:
        timezone = 1

    output["hk4e"] = [
        {
            "uid": old_file["info"]["uid"],
            "timezone": timezone,
            "lang": old_file["info"]["lang"],
            "list": [],
        }
    ]
    
    data_itemid = requests.get('https://api.uigf.org/dict/genshin/{}.json'.format(lang_map.get(old_file['info']['lang'], 'chs'))).json()
    
    for i in old_file["list"]:
        i['item_id'] = str(data_itemid.get(i['name']))
        output['hk4e'][0]['list'].append(i)
        
    return output
    
