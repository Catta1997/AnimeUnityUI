import colorama
import os
from shutil import which
from youtube_dl import YoutubeDL
from tqdm import tqdm
from AnimeUnityEngine import logging_aux, common_classes
import sys
import re

"""
Print mode levels:
1) Print only anime info
2) Print 1 and episode list
"""

colorama.init()


@logging_aux.logger_wraps()
def print_anime_list(search_res, config, print_mode):
    # Se search_res è un anime singolo lo trasformo in array per comodità
    if isinstance(search_res, common_classes.Anime):
        search_res = [search_res]
    for res in search_res:
        # Primo livello di print, uso l'str della classe anime + info varie
        if print_mode >= 1 and config['print_level'] >= 1:
            print(str(res))
            print(f"year: {res.year}\t Episodes: {len(res.episodes)}\t Episode length: {res.episodes_length} minutes")
            print("---------------------------------------------------------------")
        if print_mode >= 2 and config['print_level'] >= 2:
            if "vvvvid.it" not in str(res.episodes[0]):
                print("Episodes: ")
            for episode in res.episodes:
                if "vvvvid.it" in str(episode):
                    print("Downloading %s"%len(res.episodes)+" Episoes\n")
                    vvvvid_downloader(config,res)
                    break
                else:
                    print(str(episode))
def vvvvid_downloader(config,anime):
    if(config['download_path'] is not None):
        content_dir = os.path.join(config['download_path'], anime.slug)
    else:
        content_dir = os.path.join("Download", anime.slug)
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
    ffmpeg_local = ""
    if which("ffmpeg") is None:
        _dir = os.path.dirname(os.path.realpath(__file__))
        if os.path.isfile(os.path.join(_dir, "ffmpeg", ".DS_Store")):
            os.remove(os.path.join(_dir, "ffmpeg", ".DS_Store"))
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
    pbar = tqdm(anime.episodes, bar_format=("{l_bar}{bar}| {n_fmt}/{total_fmt}"))
    for episode in pbar:
        title = re.findall("(.*)/(.*)$", episode.link)[0][1]
        pbar.set_description("Processing: %s" % title)
        ydl_opts = {
            "format": "best",
            "outtmpl": "%s/%s.%%(ext)s" % (content_dir, title),
            "continuedl": True,
            "quiet" : True,
            #"simulate":True, # Debug: simulate a dowload
        }
        if ffmpeg_local:
            ydl_opts["ffmpeg_location"] = ffmpeg_local
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([episode.link])
            except KeyboardInterrupt:
                sys.exit()
    print("All Download Completed!")
