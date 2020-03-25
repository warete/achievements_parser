#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import requests
import os
import pathlib
import json

out_dir = 'achievements'
base_url = 'https://wfts.su'
page_url = base_url + '/achievements'
page = requests.get(page_url)


# In[51]:


def parse_item(item):
    if 'mark' in item['class']:
        type = 'mark'
    elif 'stripe' in item['class']:
        type = 'stripe'
    elif 'badge' in item['class']:
        type = 'badge'
    elif 'console' in item['class']:
        type = 'console'
    else:
        return {}
    
    image_path = item.find('div', class_='picture').img['src']
    return {
        'id': pathlib.Path(image_path).stem,
        'type': type,
        'name': item.find('div', class_='name').a.string.strip(),
        'desc': item.find('div', class_='description').string.strip(),
        'image': image_path
    }

def get_name_from_path(path):
    return pathlib.Path(path).name

def download_image(to_dir, image_path):
    file_name = get_name_from_path(image_path)
    file_path = '/'.join([to_dir, file_name])
    if not os.path.exists(to_dir):
        os.makedirs(to_dir)
    
    image_data = requests.get(base_url + image_path)
    if len(image_data.content) > 0:
        f=open(file_path, 'wb')
        f.write(image_data.content)
        f.close()
    else:
        return False
    
    return file_path


# In[52]:


if page.status_code == 200:
    soup = BeautifulSoup(page.text, "html.parser")
    
    achievements = soup.findAll('div', class_='achievement')
    #исключаем достижения с вкладки "новые"
    achievements = list(filter(lambda item: 1 if str(item['id']).isdigit() == False else 0, achievements))
    
    parsed_achievements = {
        'mark': [],
        'stripe': [],
        'badge': [],
        'console': []
    }
    for item in achievements:
        parsed_item = parse_item(item)
        if len(parsed_item) > 0:
            parsed_achievements[parsed_item['type']].append(parsed_item)


# In[53]:


if not os.path.exists(out_dir):
    os.makedirs(out_dir)
for category in parsed_achievements:
    for i in range(len(parsed_achievements[category])):
        image_path = download_image('/'.join([out_dir, category]), parsed_achievements[category][i]['image'])
        if image_path == False:
            print('ERROR', parsed_achievements[category][i]['name'])
            del parsed_achievements[category][i]
        else:
            parsed_achievements[category][i]['image'] = image_path
            
with open('achievements.json', 'w') as write_file:
    json.dump(parsed_achievements, write_file)

