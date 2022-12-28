import os
import shutil
import subprocess
from glob import glob
from time import sleep
import logging
import requests
import yaml
import yt_dlp
from pyarr import SonarrAPI, RadarrAPI


def load_config():
    with open('config/config.yaml', 'r') as f:
        global config
        config = yaml.load(f, Loader=yaml.Loader)


def dl_progress(d):
    if d['status'] == 'finished':
        logging.info("Trailer downloaded.")


def check_duration(info, *, incomplete):
    duration = info.get('duration')
    if duration not in range(int(config['length_range'].split(",")[0]), int(config['length_range'].split(",")[1])):
        return 'Video too long/short'


def trailer_pull(tmdb_id, item_type):
    logging.info("Getting information about the item...")
    try:
        item_trailers = requests.get(
            f"http://api.themoviedb.org/3/{item_type}/{tmdb_id}/videos?api_key={config['tmdb_api']}").json()['results']
        item_trailers = list(filter(lambda x: x['type'] == 'Trailer' and x['site'] == 'YouTube', item_trailers))
        return sorted(item_trailers, key=lambda x: x['size'])[-1]['key']
    except IndexError:
        return 1


def movie_finder():
    logging.info("Movie trailer finder started.")
    movie_num = 0
    movie_json = radarr.get_movie()
    for movie_item in movie_json:
        if movie_item['hasFile']:
            movie_num = movie_num + 1
            try:
                if 'moviepath' in config:
                    if movie_item['path'][-1] == "/":
                        movie_item['path'] = f"{config['moviepath']}/{movie_item['path'][0:-1].split('/')[-1]}"
                    else:
                        movie_item['path'] = f"{config['moviepath']}/{movie_item['path'].split('/')[-1]}"
                logging.info(
                    f"[{movie_num}] -- Title: {movie_item['title']}: Path: {movie_item['path']} -- TMDB-ID: "
                    f"{movie_item['tmdbId']}")
                if os.path.isfile(f"{movie_item['path']}/{config['output_dirs'].split(',')[0]}/video1.{config['filetype']}"):
                    logging.info("Trailer exists!")
                else:
                    tmdb_id = movie_item['tmdbId']
                    try:
                        link = trailer_pull(tmdb_id, "movie")
                        trailer_download(link, movie_item)
                    except:
                        logging.warning("No trailer found on TMDB! Searching manually...")
                        trailer_download(f"ytsearch5:{movie_item['title']} ({movie_item['year']}) Trailer", movie_item)
                    fileout = glob(f'cache/{movie_item["sortTitle"]}.*')
                    result = crop_check(fileout[0])
                    if result[1] is None:
                        logging.error("ERROR!")
                        exit()
                    post_process(fileout[0], result[0], movie_item['path'], result[1])
                logging.info("Copying trailer to additional directories from the config, if not copied yet...")
                for dir in config['output_dirs'].split(',')[1:]:
                    try:
                        os.mkdir(f"{movie_item['path']}/{dir}")
                    except:
                        continue
                    if not os.path.isfile(f"{movie_item['path']}/{dir}/video1.webm"):
                        shutil.copy(
                            f"{movie_item['path']}/{config['output_dirs'].split(',')[0]}/video1.{config['filetype']}",
                            f"{movie_item['path']}/{dir}/video1.{config['filetype']}")
                        logging.info("Copied trailer.")
            except Exception as e:
                logging.error(e)


def show_finder():
    logging.info("Show trailer finder started.")
    tv_num = 0
    shows_json = sonarr.get_series()
    for show_item in shows_json:
        try:
            if 'tvpath' in config:
                if show_item['path'][-1] == "/":
                    show_item['path'] = f"{config['tvpath']}/{show_item['path'][0:-1].split('/')[-1]}"
                else:
                    show_item['path'] = f"{config['tvpath']}/{show_item['path'].split('/')[-1]}"
            if show_item['episodeFileCount'] > 0:
                tv_num = tv_num + 1
                logging.info(
                    f"[{tv_num}] -- Title: {show_item['title']}: Path: {show_item['path']} -- IMDB-ID: "
                    f"{show_item['imdbId']}")
                if os.path.isfile(f"{show_item['path']}/{config['output_dirs'].split(',')[0]}/video1.{config['filetype']}"):
                    logging.info("Trailer exists!")
                else:
                    try:
                        show_id = requests.get(
                            f"https://api.themoviedb.org/3/find/{show_item['imdbId']}?api_key={config['tmdb_api']}"
                            f"&external_source=imdb_id").json()['tv_results']
                        if 'id' in show_id[0]:
                            link = trailer_pull(show_id[0]['id'], "tv")
                            if link == 1:
                                logging.warning("No trailer found!\nSearching manually...")
                                trailer_download(f"ytsearch5:{show_item['title']} ({show_item['year']}) Trailer",
                                                 show_item)
                            trailer_download(link, show_item)
                        else:
                            logging.warning("Not found on TMDB!\nSearching manually...")
                            trailer_download(f"ytsearch5:{show_item['title']} ({show_item['year']}) Trailer", show_item)
                    except Exception as e:
                        logging.error(f"ERROR: {e}\nSearching manually...")
                        trailer_download(f"ytsearch5:{show_item['title']} ({show_item['year']}) Trailer", show_item)
                    fileout = glob(f'cache/{show_item["sortTitle"]}.*')
                    result = crop_check(fileout[0])
                    if result[1] is None:
                        logging.error("ERROR!")
                        exit()
                    post_process(fileout[0], result[0], show_item['path'], result[1])
                logging.info("Copying trailer to additional directories from the config, if not copied yet...")
                for dir in config['output_dirs'].split(',')[1:]:
                    try:
                        os.mkdir(f"{show_item['path']}/{dir}")
                    except:
                        continue
                    if not os.path.isfile(f"{show_item['path']}/{dir}/video1.webm"):
                        shutil.copy(
                            f"{show_item['path']}/{config['output_dirs'].split(',')[0]}/video1.{config['filetype']}",
                            f"{show_item['path']}/{dir}/video1.{config['filetype']}")
                        logging.info("Copied trailer.")
        except Exception as e:
            logging.error(e)


def trailer_download(link, item):
    ytdl_opts = {
        'progress_hooks': [dl_progress],
        'match_filter': check_duration,
        'format': 'bestvideo+bestaudio',
        'outtmpl': f'cache/{item["sortTitle"]}'
    }
    if config['skip_intros']:
        ytdl_opts.update({'postprocessors': [
            {'key': 'SponsorBlock'},
            {'key': 'ModifyChapters',
             'remove_sponsor_segments': ['sponsor', 'intro', 'outro', 'selfpromo', 'preview', 'filler', 'interaction']}
        ]})
    fileout = glob(f'cache/{item["sortTitle"]}.*')
    os.remove(fileout[0]) if len(fileout) > 1 else None
    try:
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        ydl.download([link])
    except Exception as e:
        logging.warning("Something went wrong, Searching for something else...")
        fileout = glob(f'cache/{item["sortTitle"]}.*')
        os.remove(fileout[0]) if len(fileout) > 1 else None
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        ydl.download([f"ytsearch5:{item['title']} ({item['year']}) Trailer"])


def crop_check(filename):
    logging.info("Looking for black borders...")
    cropvalue = subprocess.check_output(f"ffmpeg -i '{filename}' -t 30 -vf cropdetect -f null - 2>&1 | awk "
                                    "'/crop/ {{ print $NF }}' | tail -1",
                                        shell=True).decode('utf-8').strip()
    logging.debug(cropvalue)
    l = [j for i, j in {720: 20, 1280: 24, 1920: 28, 3840: 35}.items()
         if i >= int(cropvalue.split('crop=')[1].split(':')[0])]
    return cropvalue, l[0] if len(l) > 0 else None


def post_process(filename, cropvalue, item_path, bitrate):
    try:
        try:
            os.mkdir(f'{item_path}/{config["output_dirs"].split(",")[0]}')
        except:
            logging.debug("Output directory found.")
        sub_file = ""
        if config['filetype'] == "webm":
            if config['subs']:
                if f"{filename}.en.vtt" in os.listdir("cache/"):
                    logging.info("Subs found")
                    sub_file = f"-i \"cache/{filename}.en.vtt\" -map 0:v -map 0:a -map 1 -metadata:s:s:0 language=eng"
            subprocess.check_call(
                f'ffmpeg -i "{filename}" {sub_file} -threads 16 -vf {cropvalue} -c:v libvpx-vp9 -crf {bitrate} -b:v '
                f'4500k -af "volume=-5dB" -y "{item_path}/{config["output_dirs"].split(",")[0]}/video1.webm"',
                                        shell=True)
        else:
            if config['subs']:
                if f"{filename}.en.vtt" in os.listdir("cache/"):
                    logging.info("Subs found")
                    sub_file = f"-i \"cache/{filename}.en.vtt\" -map 0:v -map 0:a -map 1 -metadata:s:s:0 language=eng " \
                               f"-disposition:s:0 forced -c:s ssa "
            subprocess.check_call(f'ffmpeg -i "{filename}" {sub_file} -threads 16 -vf {cropvalue} -c:v libx264 -b:v {bitrate*140}'
                                  f'-maxrate {bitrate*140} -bufsize 2M -preset slow -c:a aac -af "volume=-7dB" '
                                  f'-y "{item_path}/{config["output_dirs"].split(",")[0]}/video1.mp4"',
                                        shell=True)
        os.remove(f"{filename}")
    except Exception as e:
        logging.error(f"ERROR: {e}")

logging.basicConfig(format='%(asctime)s %(message)s', encoding='utf-8', level=logging.INFO)
try:
    os.mkdir("cache")
    logging.debug("Created cache directory.")
except:
    logging.debug("Cache directory found.")
while True:
    load_config()
    sonarr = SonarrAPI(config['sonarr_host'], config['sonarr_api'])
    radarr = RadarrAPI(config['radarr_host'], config['radarr_api'])
    movie_finder()
    show_finder()
    if isinstance(config['sleep_time'], int):
        logging.info(f"Operation complete. Clearing temporary files and sleeping for {config['sleep_time']} hour(s).")
    else:
        logging.info(f"Operation complete. Clearing temporary files and sleeping for {config['sleep_time'] * 60} minute(s).")
    for f in os.listdir("cache/"): os.remove(f"cache/{f}")
    sleep(float(config['sleep_time']) * 3600)
