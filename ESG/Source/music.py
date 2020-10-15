import mp3play
import time
def play(name):
    clip = mp3play.load("..\\data\\musics\\" + str(name) + ".mp3")
    clip.play()
    time.sleep(min(60, clip.seconds()))
    clip.stop()