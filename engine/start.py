#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys
import sockets
import threading
import zmq
import time

from pygame.locals import *
from enum import Enum
from pad import Pad

def receive():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:8080") 

    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        time.sleep(1)

        print("Waiting...")

receive()

# inicjacja modułu pygame
pygame.init()

# szerokość i wysokość okna gry
WIDTH = 800
HEIGHT = 400
# kolor okna gry, składowe RGB zapisane w tupli
LT_BLUE = (230, 255, 255)



class GAME_STATE(Enum):
   WAITING = 1 
   RUNNING = 2

# powierzchnia do rysowania, czyli inicjacja okna gry
main_window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
# tytuł okna gry
pygame.display.set_caption('Prosty Pong')

class Color:
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)


pad1 = Pad(pygame, Color.BLUE, 350, 360)
pad2 = Pad(pygame, Color.RED, 350, 20)

# piłka #################################################################
BALL_WIDTH = 20  # szerokość
BALL_HEIGHT = 20  # wysokość
BALL_X_SPEED = 4  # prędkość pozioma x
BALL_Y_SPEED = 4  # prędkość pionowa y
# utworzenie powierzchni piłki, narysowanie piłki i wypełnienie kolorem
ball = pygame.Surface([BALL_WIDTH, BALL_HEIGHT], pygame.SRCALPHA, 32).convert_alpha()
pygame.draw.ellipse(ball, Color.GREEN, [0, 0, BALL_WIDTH, BALL_HEIGHT])
# ustawienie prostokąta zawierającego piłkę w początkowej pozycji
ball_rect = ball.get_rect()
ball_rect.x = WIDTH / 2
ball_rect.y = HEIGHT / 2


# TODO: send game state, receive pad request

# ustawienia animacji ###################################################
FPS = 30  # liczba klatek na sekundę
fpsClock = pygame.time.Clock()  # zegar śledzący czas

# ustawienie prostokąta zawierającego paletkę w początkowej pozycji
# szybkość paletki AI
AI_SPEED = 5

# komunikaty textowe ###################################################
# zmienne przechowujące punkty i funkcje wyświetlające punkty
PLAYER_SCORE = '0'
AI_SCORE = '0'
fontObj = pygame.font.Font('freesansbold.ttf', 64)  # czcionka komunikatów


def print_points1():
    text1 = fontObj.render(PLAYER_SCORE, True, (0, 0, 0))
    text_player_rect = text1.get_rect()
    text_player_rect.center = (WIDTH / 2, HEIGHT * 0.75)
    main_window.blit(text1, text_player_rect)

def print_pointsAI():
    textAI = fontObj.render(AI_SCORE, True, (0, 0, 0))
    text_ai_rect = textAI.get_rect()
    text_ai_rect.center = (WIDTH / 2, HEIGHT / 4)
    main_window.blit(textAI, text_ai_rect)

# powtarzalność klawiszy (delay, interval)
pygame.key.set_repeat(50, 25)

'''
pad=1, direction=-1
'''

while True:
    # obsługa zdarzeń generowanych przez gracza
    for event in pygame.event.get():
        # przechwyć zamknięcie okna
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # przechwyć naciśnięcia klawiszy kursora
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                pad1.left()
            if event.key == pygame.K_RIGHT:
                pad1.right()

    # ruch piłki ########################################################
    # przesuń piłkę po obsłużeniu zdarzeń
    ball_rect.move_ip(BALL_X_SPEED, BALL_Y_SPEED)

    # jeżeli piłka wykracza poza pole gry
    # z lewej/prawej – odwracamy kierunek ruchu poziomego piłki
    if ball_rect.right >= WIDTH:
        BALL_X_SPEED *= -1
    if ball_rect.left <= 0:
        BALL_X_SPEED *= -1

    if ball_rect.top <= 0:  # piłka uciekła górą
        # BALL_Y_SPEED *= -1  # odwracamy kierunek ruchu pionowego piłki
        ball_rect.x = WIDTH / 2  # więc startuję ze środka
        ball_rect.y = HEIGHT / 2
        PLAYER_SCORE = str(int(PLAYER_SCORE) + 1)

    if ball_rect.bottom >= HEIGHT:  # piłka uciekła dołem
        ball_rect.x = WIDTH / 2  # więc startuję ze środka
        ball_rect.y = HEIGHT / 2
        AI_SCORE = str(int(AI_SCORE) + 1)

    # AI (jak gra komputer)
    # jeżeli piłka ucieka na prawo, przesuń za nią paletkę
    if ball_rect.centerx > pad2.rect.centerx:
        pad2.rect.x += AI_SPEED
    # w przeciwnym wypadku przesuń w lewo
    elif ball_rect.centerx < pad2.rect.centerx:
        pad2.rect.x -= AI_SPEED

    # jeżeli piłka dotknie paletki AI, skieruj ją w przeciwną stronę
    if ball_rect.colliderect(pad2.rect):
        BALL_Y_SPEED *= -1
        # uwzględnij nachodzenie paletki na piłkę (przysłonięcie)
        ball_rect.top = pad2.rect.bottom

    # jeżeli piłka dotknie paletki gracza, skieruj ją w przeciwną stronę
    if ball_rect.colliderect(pad1.rect):
        BALL_Y_SPEED *= -1
        # zapobiegaj przysłanianiu paletki przez piłkę
        ball_rect.bottom = pad1.rect.top

    # rysowanie obiektów ################################################
    main_window.fill(LT_BLUE)  # wypełnienie okna gry kolorem

    print_points1()  # wyświetl punkty gracza
    print_pointsAI()  # wyświetl punkty AI

    # narysuj w oknie gry paletki
    pad1.paint(main_window)
    pad2.paint(main_window)

    # narysuj w oknie piłkę
    main_window.blit(ball, ball_rect)

    # zaktualizuj okno i wyświetl
    pygame.display.update()

    # zaktualizuj zegar po narysowaniu obiektów
    fpsClock.tick(FPS)

