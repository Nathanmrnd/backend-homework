#!/usr/bin/env python

from argparse import ArgumentParser

import pygame as pg
from pygame.locals import QUIT

from redis import Redis

from screen import Screen
from player import Player
from others import Others

# 2 differents speeds
#
# if we do too few frames per second,
# after another player moves, we may see it very late
# (worst case: if FRAME_RATE is 4, then the delay may reach 250ms)
#
# so, we set our frame rate higher; BUT on the other hand
# this also results in the player moving too fast
# so FRAMES_PER_MOVE is defined so we move our player only once every n frames

# how often we redisplay the screen
FRAME_RATE = 10
# we move our player that many times slower
FRAMES_PER_MOVE = 3


def main():

    parser = ArgumentParser()
    parser.add_argument("-s", "--server", default=None,
                        help="IP adddress for the redis server")
    parser.add_argument("-a", "--auto-move", action="store_true",
                        help="auto move")
    parser.add_argument("name")
    args = parser.parse_args()

    # player's name as provided on the command line
    local_player_name = args.name
    pg.display.set_caption(f"game: {local_player_name}")


    screen = Screen()
    W, H = screen.size()

    clock = pg.time.Clock()

    redis_server = Redis(args.server, decode_responses=True)

    player = Player(local_player_name, H, W, redis_server)
    player.join()

    others = Others(redis_server)

    # ask the redis server where the other players are
    players = others.fetch_all_players()
    screen.display(players)

    # type 'a' to toggle auto move
    auto_move = args.auto_move

    counter = 0
    while True:
        # sync with the frame rate
        clock.tick(FRAME_RATE)
        # get the position of other players
        players = others.fetch_all_players()

        # move the local player
        # actually do all this only once every FRAMES_PER_MOVE frames
        counter += 1
        if counter % FRAMES_PER_MOVE == 0:
            counter = 0
            if auto_move:
                player.random_move()

            for event in pg.event.get():
                if (event.type == QUIT or
                    (event.type == pg.KEYDOWN and event.key == pg.K_q)):
                    player.leave()
                    return
                elif event.type == pg.KEYDOWN and event.key == pg.K_a:
                    auto_move = not auto_move
                else:
                    player.handle_event(event)

        # redisplay accordingly every frame
        screen.display(players)


if __name__ == '__main__':
    main()
