import requests
import os
import subprocess
import sys
import getopt
import html
import json
import signal
from shutil import which
from youtube_dl import YoutubeDL
from tqdm import trange
from tqdm import tqdm
import sys
from bs4 import BeautifulSoup

# config
config = {'crawl_path': None, 'download_path': None}
one_file = False  # create a single crawljob for Series with multiple season
Down_YT = False
All_seasons = False
crawljob = False

def interactive_mode():
    keyword = input("Keyword: ")
    return keyword


def cli_mode():
    global Down_YT
    global one_file
    global All_seasons
    global crawljob
    global config
    keyword = None
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            argv, 'k:yhvosc', ['keyword=', 'crawlpath=', 'downloadpath=', 'onefile'])
    except getopt.GetoptError:
        # stampa l'informazione di aiuto ed esce:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-s']:
            All_seasons = True
        if opt in ['-y']:
            Down_YT = True
            if one_file:
                print("Cannot use -o and -y")
                sys.exit()
            if (config['crawl_path'] != None):
                print("Cannot specify crawlpath with -y param")
                sys.exit()
        if opt in ['-c']:
            crawljob = True
            if opt in ['-o', '--onefile']:
                one_file = True
                if Down_YT:
                    print("Cannot use -o and -y")
                    sys.exit()
            if opt in ['--crawlpath']:
                if Down_YT:
                    print("Cannot use --crawlpath with -y")
                    sys.exit()
            config['crawl_path'] = arg
        if opt in ['-k', '--keyword']:
            keyword = arg
        if opt in ['--downloadpath']:
            config['download_path'] = arg
        if opt in ['-h', '--help']:
            help()
            sys.exit(0)
    if keyword is None:
        logger.warning("No keyword selected")
        sys.exit(1)
    return keyword


def create_crawl_all(slug, id, ep_list):
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
                f.write(
                    "\ttext=https://streamingcommunity.to/watch/%s?e=%s\n" % (id, ep_id))
                f.write("\tdownloadFolder= %s/%s/Season_%d\n" %
                        (download_path, slug, season))
                f.write("\tenabled=true\n")
                f.write("\tautoStart=TRUE\n")
                f.write("\tforcedStart=TRUE\n")
                f.write("\tautoConfirm=TRUE\n")
                f.write("}\n")
        season += 1
    f.close()


def create_crawl(slug, id, ep_list, season):
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
            f.write("\ttext=https://streamingcommunity.to/watch/%s?e=%s\n" %
                    (id, ep_id))
            f.write("\tdownloadFolder= %s/%s/Season_%d\n" %
                    (download_path, slug, season))
            f.write("\tenabled=true\n")
            f.write("\tautoStart=TRUE\n")
            f.write("\tforcedStart=TRUE\n")
            f.write("\tautoConfirm=TRUE\n")
            f.write("}\n")
        f.close()


def crawljob_movie(link, slug):
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    name = slug + '.crawljob'
    if config['download_path'] == None:
        download_path = os.path.dirname(os.path.realpath(__file__))
    else:
        download_path = config['download_path']
    if config['crawl_path'] == None:
        crawl_path = os.path.dirname(os.path.realpath(__file__))
    else:
        crawl_path = config['crawl_path']
    with open(crawl_path+'/'+name, 'w') as f:
        f.write("{\n")
        f.write("\ttext=%s" % link)
        f.write("\tdownloadFolder= %s/%s/\n" % (download_path, slug))
        f.write("\tenabled=true\n")
        f.write("\tautoStart=TRUE\n")
        f.write("\tforcedStart=TRUE\n")
        f.write("\tautoConfirm=TRUE\n")
        f.write("}\n")
        f.close()


def sig_handler(_signo, _stack_frame):
    print("\n")
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    if len(sys.argv) == 1:
        keyword = interactive_mode()
    else:
        keyword = cli_mode()
    URL = "https://streamingcommunity.to/search?q=%s" % keyword
    try:
        r = requests.get(url=URL, params={}, timeout=3)
    except Exception as e:
        print("An error occured")
        sys.exit()
    pastebin_url = r.text
    my_html = pastebin_url
    parsed_html = BeautifulSoup(my_html, "html.parser")
    json_data = parsed_html.find('the-search-page')['records']
    episodes = json_data
    ep_json = json.loads(episodes)
    playerstuff = ep_json[0]
    num = 1
    ser_id = list()
    ser_slug = list()
    type_element = list()
    serie_season = list()
    for i in playerstuff:
        id = i['id']
        ser_id.append(id)
        slug = i['slug']
        season = int(i['seasons_count'])
        serie_season.append(season)
        ser_slug.append(slug)
        type_element.append(i['type'])
        print("Result:\t" + str(num))
        print("\x1b[32m" + i['name'] + " \x1b[36m" + i['type'] + ' ' + i['release_date'] +
              "\x1b[33m" + " Seasons: " + str(i['seasons_count']) + "\x1b[0m")
        print("Plot:\n" + i['plot'])
        print("-------------------")
        num += 1
    print("-------------------")
    print("-------------------")
    id = int(input("Result:"))
    # get info
    slug = str(ser_slug[id-1])
    identifier = str(ser_id[id-1])
    URL = ("https://streamingcommunity.to/titles/%s-%s" % (identifier, slug))
    r = requests.get(url=URL, params={})
    pastebin_url = r.text
    my_html = pastebin_url
    parsed_html = BeautifulSoup(my_html, "html.parser")
    # seasons
    if ("movie" in type_element[id-1]):
        link = parsed_html.find('a', 'play-hitzone')['href']
        r = requests.get(url=link, params={})
        pastebin_url = r.text
        my_html = pastebin_url
        parsed_html = BeautifulSoup(my_html, "html.parser")
        json_data = parsed_html.find('video-player')['response']
        episodes = json_data
        ep_json = json.loads(episodes)
        link = ep_json['video_url']
        if Down_YT:
            youtube_downloader_movie(link, slug)
        elif crawljob:
            crawljob_movie(link, slug)
        else:
            print(link)
    else:
        json_data_2 = parsed_html.find('season-select')['seasons']
        episodes_2 = json_data_2
        ep_json_2 = json.loads(episodes_2)
        text = ep_json_2[0]['episodes']
        if Down_YT:
            youtube_downloader(ep_json_2, slug, identifier)
        elif crawljob:
            if not one_file:
                if All_seasons:
                    seas_sel = int(input('Season: '))
                    if(seas_sel > serie_season[id-1]):
                        print("Only %d season" % serie_season[id-1])
                        sys.exit("\n")
                    k = ep_json_2[seas_sel-1]
                    test = k['episodes']
                    create_crawl(slug, id, test, seas_sel)
                else:
                    x = 1
                    for k in ep_json_2:
                        test = k['episodes']
                        create_crawl(slug, id, test, x)
                        x += 1
            else:
                create_crawl_all(slug, id, ep_json_2)
        else:
            x = 1
            for k in ep_json_2:
                test = k['episodes']
                for i in test:
                    ep_id = i['id']
                    print("https://streamingcommunity.to/watch/%s?e=%s" %(id, ep_id))
                x += 1


def help():
    usage = f"\t-k, --keyword (str):\t\tSpecify the keyword to search\n" \
            f"\t--downloadpath (Path):\t\tJDownloadr and yt_downloader download folder\n" \
            f"\t-o,--onefile:\t\t\tCreate only one crawljob instead one for each season, CANNOT use with -y param\n" \
            f"\t-y:\t\t\t\tDownload using YT_Downloader, CANNOT use with -o param\\n" \
            f"\t--crawlpath (Path):\t\tDestination folder for the crawljobs\n" \
            f"\t-s:\t\t\t\t Download or add to crawljob all seasons\n"\
            f"\t-h, --help:\t\t\tShow this screen\n"
    print(usage)


def youtube_downloader_movie(link, slug):
    if(config['download_path'] is not None):
        content_dir = os.path.join(config['download_path'], slug)
    else:
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
            print(
                "Controlla che la cartella ffmpeg contwnga solo il readme e la cartella con òa build di ffmpeg")
            quit()
        elif len(ffmpeg_dir_files) == 0:
            print(
                "Installa ffmpeg, consulta la pagina su GitHub per maggiori informazioni")
            quit()
        ffmpeg_local = os.path.join(_dir, "ffmpeg", ffmpeg_dir_files[0], "bin")
    movie_pbar = tqdm(total=1, bar_format=(
        "{l_bar}{bar}| {n_fmt}/{total_fmt}"))
    ydl_opts = {
        "format": "best",
        "outtmpl": "%s/%s.%%(ext)s" % (content_dir, slug),
        "continuedl": True,
        "quiet": True,
        "simulate": True,  # Debug: simulate a dowload
    }
    if ffmpeg_local:
        ydl_opts["ffmpeg_location"] = ffmpeg_local
    with YoutubeDL(ydl_opts) as ydl:
        try:
            movie_pbar.set_description("Processing %s: " % slug)
            skip = False
            try:
                r = requests.get(url=link, params={})
            except Exception as e:
                print("Error downloading %s\n" % slug)
                skip = True
            if(r.status_code == 200 and not skip):
                ydl.download([link])
            movie_pbar.update(1)
        except KeyboardInterrupt:
            sys.exit()


def youtube_downloader(ep_list, slug, id):
    if(config['download_path'] != None):
        content_dir = os.path.join(config['download_path'], slug)
    else:
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
            print(
                "Controlla che la cartella ffmpeg contwnga solo il readme e la cartella con òa build di ffmpeg")
            quit()
        elif len(ffmpeg_dir_files) == 0:
            print(
                "Installa ffmpeg, consulta la pagina su GitHub per maggiori informazioni")
            quit()
        ffmpeg_local = os.path.join(_dir, "ffmpeg", ffmpeg_dir_files[0], "bin")
    n_episoeds = 0
    error_download = list()
    # calc numbero of episodes
    for episode in ep_list:
        ep_list_2 = episode['episodes']
        for i in ep_list_2:
            n_episoeds += 1
    print("Downloadin %d episodes" % n_episoeds)
    episode_pbar = tqdm(total=n_episoeds, bar_format=(
        "{l_bar}{bar}| {n_fmt}/{total_fmt}"))
    season = 1
    for episode in ep_list:
        ydl_opts = {
            "format": "best",
            "outtmpl": "%s/%s.%%(ext)s" % (content_dir, slug),
            "continuedl": True,
            "quiet": True,
            "simulate": True,  # Debug: simulate a dowload
        }
        if ffmpeg_local:
            ydl_opts["ffmpeg_location"] = ffmpeg_local
        ep_list_2 = episode['episodes']
        episode_n = 1
        for i in ep_list_2:
            ep_id = i['id']
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    if len(error_download) > 0:
                        episode_pbar.set_description("Processing %s(\x1b[31m%d error\x1b[0m): " % (
                            slug, len(error_download)) + 'Season ' + str(season) + ', episode: ' + str(episode_n))
                    else:
                        episode_pbar.set_description(
                            "Processing %s: " % slug + 'Season ' + str(season) + ', episode: ' + str(episode_n))
                    link = "https://streamingcommunity.to/watch/%s?e=%s\n" % (
                        id, ep_id)
                    r = requests.get(url=link, params={})
                    pastebin_url = r.text
                    my_html = pastebin_url
                    parsed_html = BeautifulSoup(my_html, "html.parser")
                    json_data = parsed_html.find('video-player')['response']
                    episodes = json_data
                    ep_json = json.loads(episodes)
                    link = ep_json['video_url']
                    skip = False
                    try:
                        r = requests.get(url=link, params={})
                    except Exception as e:
                        error_download.append(
                            "Error downloading season %d, episode %d" % (season, episode_n))
                        skip = True
                    if(r.status_code == 200 and not skip):
                        ydl.download([link])
                    episode_pbar.update(1)
                    episode_n += 1
                except KeyboardInterrupt:
                    if (len(error_download) > 0):
                        print("\n\x1b[31mError downloading %d episodes:\x1b[0m" % len(
                            error_download))
                        for error in error_download:
                            print(error)
                    sys.exit()
        season += 1
        episode_n = 1
    if (len(error_download) > 0):
        print("\n\x1b[31mError downloading %d episodes:\x1b[0m" %
              len(error_download))
        for error in error_download:
            print(error)


if __name__ == "__main__":
    main()
