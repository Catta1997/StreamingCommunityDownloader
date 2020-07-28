import requests,os,subprocess
import sys
import html
import json
from bs4 import BeautifulSoup
URL = "https://streamingcommunity.to/search?q=chicago"
r = requests.get(url = URL, params = {}) 
pastebin_url = r.text 
my_html = pastebin_url
parsed_html = BeautifulSoup(my_html,"html.parser")
json_data = parsed_html.find('the-search-page')['records']
episodes = json_data
ep_json = json.loads(episodes)
playerstuff = ep_json[0]
for i in playerstuff:
    print (i['name'])
    name = i['name']
    print (i['id'])
    id = i['id']
    print (i['slug'])
    slug = i['slug']
    print("--------")
#id = input("ID:")

#debug part
slug = "chicago-fire"
id = "180"
# end debug part
URL = ("https://streamingcommunity.to/titles/%s-%s"%(id,slug))
print(URL)
r = requests.get(url = URL, params = {}) 
pastebin_url = r.text 
my_html = pastebin_url
parsed_html = BeautifulSoup(my_html,"html.parser")
json_data_2 = parsed_html.find('season-select')['seasons']
episodes_2 = json_data_2
ep_json_2 = json.loads(episodes_2)
text = ep_json_2[0]['episodes']
x = 1
for k in ep_json_2:
    print("------")
    print("Season %d\n"%x)
    x +=1
    text = k['episodes']
    for i in text:
        ep_id = i['id']
        print("https://streamingcommunity.to/watch/%s?e=%s"%(id,ep_id))