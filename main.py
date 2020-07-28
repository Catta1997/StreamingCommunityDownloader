import requests,os,subprocess
import sys
import html
import json
from bs4 import BeautifulSoup
#config
one_file = True #create a single crawljob for Series with multiple season
download_path = os.path.dirname(os.path.realpath(__file__)) #path  where jdownloader will download the files
crawl_file_l = os.path.dirname(os.path.realpath(__file__)) #folder watch location

def create_crawl_all(download_path,slug,id,ep_list):
    crawl_file_l = os.path.dirname(os.path.realpath(__file__))
    name = slug + '.crawljob'
    season = 1
    for k in ep_list:
        ep_list_2 = k['episodes']
        with open(name, 'a') as f:
            for i in ep_list_2:
                ep_id = i['id']
                f.write("{\n")
                f.write("\ttext=https://streamingcommunity.to/watch/%s?e=%s\n"%(id,ep_id))
                f.write("\tdownloadFolder= %s/%s/Season_%d\n"%(download_path,slug,season))
                f.write("\tenabled=true\n")
                f.write("\tautoStart=TRUE\n")
                f.write("\tforcedStart=TRUE\n")
                f.write("\tautoConfirm=TRUE\n")
                f.write("}\n")
        season += 1
    f.close()

def create_crawl(download_path,slug,id,ep_list, season):
    name = slug+"_Season_" + str(season) + '.crawljob'
    with open(name, 'w') as f:
        for i in ep_list:
            ep_id = i['id']
            f.write("{\n")
            f.write("\ttext=https://streamingcommunity.to/watch/%s?e=%s\n"%(id,ep_id))
            f.write("\tdownloadFolder= %s/%s/Season_%d\n"%(download_path,slug,season))
            f.write("\tenabled=true\n")
            f.write("\tautoStart=TRUE\n")
            f.write("\tforcedStart=TRUE\n")
            f.write("\tautoConfirm=TRUE\n")
            f.write("}\n")
        f.close()

def main():
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
    if not one_file:
        x = 1
        for k in ep_json_2:
            test = k['episodes']
            create_crawl(download_path,slug,id,test,x)
            x +=1
    else:
        create_crawl_all(download_path,slug,id,ep_json_2)
def format_title(old_title):
    # Formatting the string
    new_title = str.capitalize(str.lower(old_title))

    replace_chars = [{'old': ' ', 'new': '_'}, {'old': '!', 'new': ''}, {'old': '?', 'new': ''},
                     {'old': ':', 'new': ''}, {'old': ',', 'new': ''}, {'old': '\'', 'new': ''}]
    for char in replace_chars:
        new_title = str.replace(new_title, char['old'], char['new'])

    return new_title
if __name__ == "__main__":
    main()
