#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import locale
import logging
import signal
import sys
import os
import time

from aiy.assistant.grpc import AssistantServiceClientWithLed
from aiy.cloudspeech import CloudSpeechClient
from PIL import Image, ImageDraw, ImageFont
from aiy.board import Board, Led


def volume(string):
    value = int(string)
    if value < 0 or value > 100:
        raise argparse.ArgumentTypeError('Volume must be in [0...100] range.')
    return value


def locale_language():
    language, _ = locale.getdefaultlocale()
    return language


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_text_size(font, text):
    return font.getsize(text)


def text_to_ascii_text(font, text, cols, lines):
    """Convert text to ASCII art text banner"""
    image = Image.new('RGB', (cols - 1, lines - 1), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, fill='black', font=font)
    width, height = image.size
    pixels = image.load()
    out = ''
    for y in range(height):
        for x in range(width):
            pix = pixels[x, y]
            if pix != (255, 255, 255):
                out += '#'
            else:
                out += ' '
        out += '\n'
    return out


def ascii_print(text_to_print, board, font_file='roboto.ttf'):
    column, lines = os.get_terminal_size(0)
    font = ImageFont.truetype(font_file, lines - 8)
    space_width = get_text_size(font, ' ')[0]
    padding = ' ' * int(column / space_width + 1)
    text = padding + text_to_print
    index = 0
    try:
        while True:
            print(text_to_ascii_text(font, text[index:], column, lines))
            index += 1
            if index > len(text):
                index = 0
            if board.button.wait_for_press(0.095):
                return 0
            clear_console()
    except KeyboardInterrupt:
        pass


def main():
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    parser.add_argument('--volume', type=volume, default=100)
    args = parser.parse_args()
    client = CloudSpeechClient()
    with Board() as board:
        assistant = AssistantServiceClientWithLed(board=board,
                                                  volume_percentage=args.volume,
                                                  language_code=args.language)
        while :
            logging.info('Press button to start conversation...')
            board.button.wait_for_release()
            logging.info('Conversation started!')
            # assistant.conversation()
            text = client.recognize(language_code=args.language)
            if text:
                ascii_print(text, board)


if __name__ == '__main__':
    main()

