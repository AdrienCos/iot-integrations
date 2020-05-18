import vlc
import pafy
from time import sleep


class TV():
    "Simple wrapper for a PIR device "

    def __init__(self, media: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        # Get the correct media URL
        video = pafy.new(media)
        best = video.getbest()
        playurl: str = best.url
        self.url = playurl

        self.instance = vlc.Instance("--vout=dummy", "--aout=dummy", "--input-repeat=-1")
        self.player: vlc.MediaPlayer = self.instance.media_player_new()
        self.media: vlc.Media = self.instance.media_new(self.url)
        self.media.get_mrl()
        self.player.set_media(self.media)

        self._state: bool = False

    @property
    def state(self) -> bool:
        return bool(self.player.is_playing())

    def on(self) -> None:
        err = self.player.play()
        sleep(3)
        if err != 0:
            print('Error while starting the player')
        else:
            print("TV started")

    def off(self) -> None:
        self.player.stop()

    def toggle(self) -> None:
        if self.state is True:
            self.off()
        else:
            self.on()


if __name__ == "__main__":

    tv = TV()
    tv.on()
    while tv.state is True:
        print(tv.state)
        sleep(1)
