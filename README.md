# Backdroppr
*Backdroppr* is a tool written in Python that is used to import movies and shows from Radarr and Sonar, download appropriate trailers, remove borders and adding them to your library.

## Features
* Automatically select the highest resolution available on YouTube (while trying to avoid 360 videos).
* Download to multiple directories.
* Automatically detect and crop black borders.
* Fallback to manual search if no trailer exists in TheMovieDB.
* Video length filtering to avoid short or long videos.
* Automatic subtitle download.
* Automatic intro, outro and intermission skipping in trailers.
* Option to run the script once, if no sleep time was set.

## Known Bugs
* If no trailer was found on TheMovieDB, the script will manually search for one, but will keep searching again even if it already found and downloaded one. It won't redownload it though.
* Issue when a video with 5.1 audio is found.
* Skips the rest of the trailers in TheMovieDB if a link is dead.

## To-do List
* Vimeo fallback.
* Customizeable filenames.
* Codec selection (as well as hardware acceleration).
* Customizeable bitrates.

## Requirements
(note: currently only works in Linux)
* Python3
* ffmpeg
* Radarr
* Sonarr

## How to Install
Backdropper can be used as a standalone program or as a docker container.
This guide assumes you already have Docker (if used), Radarr, and Sonarr installed and set up.
### Standalone
1. Clone the repository: `git clone https://github.com/ShiniGandhi/Backdroppr.git`.
2. Navigate to the repo's directory: `cd Backdroppr`.
3. Install python and ffmpeg: `sudo apt install python3 ffmpeg -y`.
4. Install python requirements: `pip install -r requirements.txt`.
5. [Edit the configuration file](###config.yaml).
6. Run the program `python3 main.py`.
### Docker
1. Clone the repository: `git clone https://github.com/ShiniGandhi/Backdroppr.git`.
2. Navigate to the repo's directory: `cd Backdroppr`.
3. Build the image: `docker build -t shinigandhi/backdroppr:latest .` (you can skip if you want to use my image)
4. [Edit the docker-compose file](###docker-compose.yml).
5. [Edit the configuration file](###config.yaml).
6. Start the container `docker-compose up -d`.

## Configuration
These variables are used to configure the runtime options of Backdroppr. At least some of them are required to be configured for Backdroppr to run.

| Name | Description                                                                                                                                                                                                                                | Example | Required |
| --- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| --- | --- |
| radarr_api | API key received from Radarr<br>**if not set:** disables Radarr.                                                                                                                                                                                                               | `4556edb99d442d83b88c6809c42fc78d` | Yes |
| radarr_host | IP and port in-which Radarr runs<br>**if not set:** disables Radarr.                                                                                                                                                                                                           | `http://172.0.0.1:7878` | Yes |
| sonarr_api | API key received from Sonarr<br>**if not set:** disables Sonarr.                                                                                                                                                                                                               | `01bb1ebca84e8939f112c414b98c70f7` | Yes |
| sonarr_host | IP and port in-which Sonarr runs<br>**if not set:** disables Sonarr.                                                                                                                                                                                                           | `http://172.0.0.1:8989` | Yes |
| tmdb_api | [API key from themoviedb](https://developers.themoviedb.org/3/getting-started/introduction)                                                                                                                                                | `96dd72f9176e688b8967829911a184fb` | Yes |
| output_dirs | The directory inside the tv show/movie's directory that trailers will be downloaded to. </br>Multiple values can be set using a comma (`,`).                                                                                               | `trailers` or `trailers,backdrops` | Yes
| sleep_time | Time in hours that the script will wait until running again. </br>Can be set to minutes using a decimal point.</br>If not set, the script will only run once (but make sure you disable `restart: always` if you do this.                  | `3` or `0.5` | No |
| length_range | Time range in seconds in which the trailer must be. Separated with a comma `,` </br>Optional, but I do recommend setting it, as some entries may have extremely long or short videos. | `30,300` | No |
| filetype | File extension used in target file. </br>Defaults to `mp4` (`h264`) if left empty. </br>I recommend using `webm` since it uses `vp9`, which, while slower to encode is more efficient.                                                     | `webm` - `vp9` codec </br> `mp4` - `h264` codec | No |
| skip_intros | Uses SponsorBlock to detect intros and other junk in the video and skips it. </br>Doesn't always work. If you're experiencing any issues just disable it for a while. </br>Defaults to `False` if not set.                                 | `True` or `False` | No |
| thread_count | Number of threads to use when transcoding. Set to all threads if not set. | `8` | No |
| subs | Whether or not subtitles will be downloaded </br>`vtt` if `webm` and `ass` if `mp4`. </br>Defaults to `False` if not set.                                                                                                                  | `True` or `False` | No |
| moviepath | Override the path set inside Radarr if not the same as the script's </br>Useful if Radarr is running inside a container or on a different machine.                                                                                         | `"/vault/Media/Movies"` | No |
| tvpath | Override the path set inside Sonarr if not the same as the script's </br>Useful if Sonarr is running inside a container or on a different machine.                                                                                         | `"/vault/Media/TV Shows"` | No |

When using configuration file, Backdroppr will read `config.yaml` in the configuration folder to get these runtime parameters:

### config.yaml
```### Mandatory ###
radarr_api: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
radarr_host: "http://172.0.0.1:7878"
sonarr_api: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
sonarr_host: "http://172.0.0.1:8989"
tmdb_api: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
output_dirs: "trailers"
sleep_time: 3
length_range: "30,300"
### Optional ###
filetype: "webm"
skip_intros: True
thread_count: 8
subs: True
### Uncomment if needed ###
moviepath: "/vault/Media/Movies"
tvpath: "/vault/Media/TV Shows"
```

### docker-compose.yml
```
version: "3"
services:
  backdroppr:
    container_name: backdroppr
    image: shinigandhi/backdroppr:latest
    ### Optional: Uncomment case-sensitive environment variables to configure backdroppr ###
    # environment:
    #   - RADARR_API="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    #   - RADARR_HOST=http://localhost:7878
    #   - SONARR_API="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    #   - SONARR_HOST=http://localhost:8989
    #   - TMDB_API=""xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx""
    #   - OUTPUT_DIRS="trailers"
    #   - SLEEP_TIME=3
    #   - LENGTH_RANGE="30,300"
    #   - FILETYPE="webm"
    #   - SKIP_INTROS=True
    #   - THREAD_COUNT="8"
    #   - SUBS=True
      ### Uncomment if needed ###
      # - MOVIEPATH="/vault/Media/Movies"
      # - TVPATH="/vault/Media/TV Shows"
    restart: always
    volumes:
      - ./config:/config #The config file location, Optional if using env variables
      - /vault/Media/TV Shows:/tv #TV show directory re-routing
      - /vault/Media/Movies:/movies #Movie directory re-routing
```
Note: You may append `_FILE` to the end of the following variables: RADARR_API, SONARR_API, TMDB_API and provide a valid file path.