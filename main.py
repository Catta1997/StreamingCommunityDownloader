import requests,os,subprocess
import sys
import getopt
import html
import json
from shutil import which
from youtube_dl import YoutubeDL
from tqdm import trange
from tqdm import tqdm
from time import sleep
import sys
import re
from bs4 import BeautifulSoup
#config
config = {'crawl_path': None, 'download_path': None}
one_file = True #create a single crawljob for Series with multiple season

Down_YT = False # BETA
def interactive_mode():
    try:
        keyword = input("Keyword: ")
    except KeyboardInterrupt:
        sys.exit()
    return keyword
def cli_mode():
    keyword = None
    global config
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 'k:hv',['keyword=', 'crawlpath=', 'jdownloadpath='])
    except getopt.GetoptError:
        # stampa l'informazione di aiuto ed esce:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-k', '--keyword']:
            keyword = arg
        if opt in ['--jdownloadpath']:
            config['download_path'] = arg
        if opt in ['--crawlpath']:
            config['crawl_path'] = arg
        if opt in ['-h', '--help']:
            help()
            sys.exit(0)
    if keyword is None:
        logger.warning("No keyword selected")
        sys.exit(1)
    return keyword

def create_crawl_all(slug,id,ep_list):
    name = slug + '.crawljob'
    season = 1
    if config['download_path'] == None:
        download_path = os.path.dirname(os.path.realpath(__file__))
    else:
        download_path = config['download_path']

    if config['crawl_path'] == None:
        crawl_path = os.path.dirname(os.path.realpath(__file__))
    else:
        crawl_path = config['crawl_path']
    for k in ep_list:
        ep_list_2 = k['episodes']
        with open(crawl_path+'/'+name, 'a') as f:
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

def create_crawl(slug,id,ep_list, season):
    name = slug+"_Season_" + str(season) + '.crawljob'
    if config['download_path'] == None:
        download_path = os.path.dirname(os.path.realpath(__file__))
    else:
        download_path = config['download_path']
    if config['crawl_path'] == None:
        crawl_path = os.path.dirname(os.path.realpath(__file__))
    else:
        crawl_path = config['crawl_path']
    with open(crawl_path+'/'+name, 'w') as f:
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
    if len(sys.argv) == 1:
        keyword = interactive_mode()
    else:
        keyword = cli_mode()
    URL = "https://streamingcommunity.to/search?q=%s"%keyword
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
    r = requests.get(url = URL, params = {}) 
    pastebin_url = r.text 
    my_html = pastebin_url
    parsed_html = BeautifulSoup(my_html,"html.parser")
    json_data_2 = parsed_html.find('season-select')['seasons']
    episodes_2 = json_data_2
    ep_json_2 = json.loads(episodes_2)
    text = ep_json_2[0]['episodes']
    if Down_YT:
        youtube_downloader(ep_json_2,slug,id)
    else:
        if not one_file:
            x = 1
            for k in ep_json_2:
                test = k['episodes']
                create_crawl(slug,id,test,x)
                x +=1
        else:
            create_crawl_all(slug,id,ep_json_2)

def help():
    usage = f"\t-k, --keyword (str):\t\tSpecify the keyword to search\n" \
            f"\t--jdownloadpath (Path):\t\tDestination folder for the anime dir\n" \
            f"\t--crawlpath (Path):\t\tDestination folder for the crawljobs\n" \
            f"\t-h, --help:\t\t\tShow this screen\n"
    print(usage)



def youtube_downloader(ep_list,slug,id):
    content_dir = os.path.join("Download", slug)
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
    ffmpeg_local = ""
    if which("ffmpeg") is None:
        _dir = os.path.dirname(os.path.realpath(__file__))
        ffmpeg_dir_files = os.listdir(os.path.join(_dir, "ffmpeg"))
        ffmpeg_dir_files.remove("readme.md")
        # If the directory is ambiguous stop the script
        if len(ffmpeg_dir_files) > 1:
            print("Controlla che la cartella ffmpeg contwnga solo il readme e la cartella con òa build di ffmpeg")
            quit()
        elif len(ffmpeg_dir_files) == 0:
            print("Installa ffmpeg, consulta la pagina su GitHub per maggiori informazioni")
            quit()
        ffmpeg_local = os.path.join( _dir, "ffmpeg", ffmpeg_dir_files[0], "bin")
    pbar = tqdm(ep_list, bar_format=("{l_bar}{bar}| {n_fmt}/{total_fmt}"))
    for episode in pbar:
        ydl_opts = {
            "format": "best",
            "outtmpl": "%s/%s.%%(ext)s" % (content_dir, slug),
            "continuedl": True,
            "quiet" : True,
            "simulate":True, # Debug: simulate a dowload 
        }
        if ffmpeg_local:
            ydl_opts["ffmpeg_location"] = ffmpeg_local
        ep_list_2 = episode['episodes']
        season = 1
        episode_n = 1
        for i in ep_list_2:
            ep_id = i['id']
            with YoutubeDL(ydl_opts) as ydl:
            #meta = ydl.extract_info(episode.link, download=False) 
                pbar.set_description("Processing: %s" % slug + ' Season ' + str(season) + ' ep ' + str(episode_n))
                link = "https://streamingcommunity.to/watch/%s?e=%s\n"%(id,ep_id)
                r = requests.get(url = link, params = {}) 
                pastebin_url = r.text 
                my_html = pastebin_url
                parsed_html = BeautifulSoup(my_html,"html.parser")
                json_data = parsed_html.find('video-player')['response']
                episodes = json_data
                ep_json = json.loads(episodes)
                try:
                    link = ep_json['video_url']
                    ydl.download([link])
                except KeyboardInterrupt:
                    sys.exit()
                episode_n +=1
            #f.write("\ttext=https://streamingcommunity.to/watch/%s?e=%s\n"%(id,ep_id))
        season += 1
        episode_n = 1

if __name__ == "__main__":
    main()
