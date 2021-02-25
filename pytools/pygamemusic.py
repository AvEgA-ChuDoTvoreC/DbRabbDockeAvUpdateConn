# -*- coding: utf-8 -*-
from MY_SCRIPTS.decorators import my_timer

import os

import pygame as pg
import sys
import random

# from playsound import playsound
# pipenv install PyObjC

pg.init()
sc = pg.display.set_mode((200, 150))


path_to_sounds = "../Sounds/"

ls_sounds = os.listdir(path_to_sounds)
sounds = [os.path.join(path_to_sounds, sound) for sound in ls_sounds]
# sounds.reverse()
print(sounds)


@my_timer
def sound_prepare():
    _sound = "sound"
    _nn = [_sound + str(_n) for _n in range(len(sounds))]
    songs = dict.fromkeys(_nn)

    for i in songs:
        for _ in sounds:
            if _ not in songs.values():
                songs[i] = _  # pg.mixer.Sound(_)

    songs_to_diplay = songs.copy()
    for i in songs.keys():
        songs[i] = pg.mixer.Sound(songs[i])

    # ax = list(map(lambda x: pg.mixer.Sound(x), list(songs.keys())))
    # print(ax)

    print(f"Number of tracks in ./{path_to_sounds} : {len(songs)}")
    return songs, songs_to_diplay


@my_timer
def sound_flags():
    flag = True
    return flag


@my_timer
def sound_controller(songs_in_folder, s_flags=None, songs_to_d=None):
    n = 0
    m = random.randrange(len(sounds) - 1)
    circl = 1
    while True:
        for i in pg.event.get():

            if i.type == pg.QUIT:
                sys.exit()

            elif i.type == pg.KEYUP:
                if i.key == pg.K_1:
                    pg.mixer.music.stop()
                    # pygame.mixer.music.stop()
                elif i.key == pg.K_2:
                    pg.mixer.music.unpause()
                    # pygame.mixer.music.play()
                    pg.mixer.music.set_volume(0.5)
                elif i.key == pg.K_3:
                    pg.mixer.music.unpause()
                    # pygame.mixer.music.play()
                    pg.mixer.music.set_volume(1)

                elif i.key == pg.K_RIGHT:

                    if n >= len(sounds):
                        songs_in_folder[f'sound{n - 1}'].stop()
                        n = 0
                        if s_flags:
                            circles = 2
                            if circl >= circles:
                                print(f"Start from first track. {circl}/{circles} circles")
                                circl = 1
                                break
                            print(f"Start from first track. {circl}/{circles} circles")
                            circl += 1

                    if n > 0:
                        songs_in_folder[f'sound{n - 1}'].stop()
                    songs_in_folder[f'sound{n}'].play()
                    pg.mixer.music.queue(songs_to_d[f'sound{n}'])
                    print(f"Playing  #{n + 1}: ", os.path.basename(songs_to_disp[f'sound{n}']))
                    n += 1


                elif i.key == pg.K_UP:
                    sound_lenth = f"{songs_in_folder[f'sound{n}'].get_length():.2f}"

                    if n > 0:
                        songs_in_folder[f'sound{n - 1}'].stop()
                    else:
                        songs_in_folder[f'sound{n}'].stop()

                    m = n
                    n = random.randrange(len(sounds) - 1)

                    print("N: ", n, " Length: ", sound_lenth)
                    songs_in_folder[f'sound{n}'].play()
                    print(f"Playing  #{n + 1}: ", os.path.basename(songs_to_disp[f'sound{n}']))
                    n += 1

                elif i.key == pg.K_DOWN:

                    if n > 0:
                        songs_in_folder[f'sound{n - 1}'].stop()
                    else:
                        songs_in_folder[f'sound{n}'].stop()

                    n = m - 1

                    songs_in_folder[f'sound{n}'].play()
                    print(f"Playing  #{n + 1}: ", os.path.basename(songs_to_disp[f'sound{n}']))
                    n += 1

                elif i.key == pg.K_LEFT:

                    if n <= 0:
                        n = 0
                        songs_in_folder[f'sound{n}'].stop()
                        print(f"Stoped  #{n + 1}: ", os.path.basename(songs_to_disp[f'sound{n}']))
                    else:
                        songs_in_folder[f'sound{n - 1}'].stop()
                        n -= 1
                        print(f"Stoped  #{n + 1}: ", os.path.basename(songs_to_disp[f'sound{n}']))

                elif i.key == pg.K_ESCAPE:
                    sys.exit()

        pg.time.delay(1)


songs, songs_to_disp = sound_prepare()
flags = sound_flags()
sound_controller(songs, flags, songs_to_disp)

# pg.mixer.music.load(songs["sound1"])
# pg.mixer.music.play()
# print(f"Playing: {songs['sound1']}")

# dd = dict()
#
# dd["path"] = re.escape(_)
# print(f"{dd['path']}".replace('\\', '').replace(" ", "%20"))
# playsound(f"{dd['path']}".replace('\\', '').replace(" ", "%20"))
