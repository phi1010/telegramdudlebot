#!/usr/bin/env python2
#
# Simple Bot to reply Telegram messages
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
# Copyright (C) 2015 Phillip Kuhrt <reg-telegramdudlebot@phi1010.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import logging
import telegram
import time
import re
import pickle

class Conversation:
    def __init__(self, chat_id, dudle, setby):
        self.chat_id = chat_id
        self.dudle = dudle
        self.setby = setby

LAST_UPDATE_ID = None
ME = None
COMMAND_RE = None
HELP_RE = None
DUDLE_RE = re.compile("(https?://)?dudle.inf.tu-dresden.de/.*")
LOGGER = logging.getLogger(__name__)
#logging.getLogger().setLevel(logging.INFO)
LOGGER.setLevel(logging.INFO)

def main():
    global LAST_UPDATE_ID, COMMAND_RE, ME, HELP_RE
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Telegram Bot Authorization Token
    bot = telegram.Bot('<enteryourkeyhere>')

    # This will be our global variable to keep the latest update_id when requesting
    # for updates. It starts with the latest update_id if available.
    try:
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None
    
    ME = bot.getMe()
    LOGGER.warn(ME)
    restr = "^/%s(?P<botname>@"+re.escape(ME.username)+")?(\ (?P<dudleurl>.*))?$"
    LOGGER.warn(restr % "dudle")
    COMMAND_RE = re.compile(restr % "dudle", re.DOTALL)
    HELP_RE = re.compile(restr % "(help|start)", re.DOTALL)
    
    while True:
        echo(bot)
        time.sleep(3)


def echo(bot):
    global LAST_UPDATE_ID

    # Request updates from last updated_id
    for update in bot.getUpdates(offset=LAST_UPDATE_ID):
        if LAST_UPDATE_ID < update.update_id:
            onupdate(bot, update)
            # Updates global offset to get the new updates
            LAST_UPDATE_ID = update.update_id

def onupdate(bot, update):
    # chat_id is required to reply any message
    chat_id = update.message.chat_id
    message = update.message.text
    
    LOGGER.info("received: "+message)
    rematch = HELP_RE.match(message)
    if rematch:
        LOGGER.info("help")
        bot.sendMessage(chat_id=chat_id, text="/dudle - Get current dudle.\n/dudle <url> - Set new dudle.")
        return
    rematch = COMMAND_RE.match(message)
    if not rematch:
        return
    LOGGER.info(rematch)
    try:
        with open('data.pickle', 'rb') as f:
            data = pickle.load(f)
            print data
    except:
        LOGGER.error("No data found in data.pickle, using default data!", exc_info=True)
        data = []
    url=rematch.group('dudleurl')
    if url:
        LOGGER.info("set on %s: %s" % (chat_id,url))    
        if not DUDLE_RE.match(url):
            LOGGER.info("url invalid")     
            bot.sendMessage(chat_id=chat_id, text="invalid dudle. try using https://dudle.inf.tu-dresden.de/")
            return
        data = [x for x in data if x.chat_id != chat_id]
        setby = update.message.from_user
        data.append(Conversation(chat_id=chat_id, dudle=url, setby=setby))    
        bot.sendMessage(chat_id=chat_id, text="dudle set.")
        with open('data.pickle', 'wb') as f:
            print pickle.dump(data, f)
    else:
        LOGGER.info("get on %s" % (chat_id))    
        for c in data:
            if c.chat_id == chat_id:
                url = c.dudle
                setby = "%s %s %s" % (c.setby.name, c.setby.first_name, c.setby.last_name)
                bot.sendMessage(chat_id=chat_id, text="%s (set by %s)" % (url, setby))
        
    
 
    


if __name__ == '__main__':
    main()
