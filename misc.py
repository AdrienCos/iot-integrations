# How to stream a youtube video on a headless device

import vlc
import pafy
import time

url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

video = pafy.new(url)
best = video.getbest()
playurl: str = best.url

instance = vlc.Instance("--vout=dummy", "--aout=dummy")
player: vlc.MediaPlayer = instance.media_player_new()
media: vlc.Media = instance.media_new(playurl)
media.get_mrl()
player.set_media(media)
err = player.play()

if err != 0:
    print("Error while starting the player")

time.sleep(5)
while player.is_playing():
    time.sleep(1)
