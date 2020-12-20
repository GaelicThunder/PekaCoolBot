# -*- coding: utf-8 -*-
import telebot
from telebot import types
import os
from peewee import *
from decouple import config
import markovify
import logging
from time import time, asctime, sleep
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, User, CallbackQuery
from typing import List
import random
import time
import sys
import atexit
import signal
from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw, ImageOps
import textwrap
import math
from datetime import datetime
import requests
import urllib.request
from urllib.request import urlopen, Request
import boto3
import psutil
import re
from telegram import TelegramObject
import telegram
from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode, Update
from telegram.ext import InlineQueryHandler, CallbackContext
import pickle
import pygame



class MaskPosition(TelegramObject):
    FOREHEAD = 'forehead'
    EYES = 'eyes'
    MOUTH = 'mouth'
    CHIN = 'chin'

    def __init__(self, point, x_shift, y_shift, scale):
        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.scale = scale

    @staticmethod
    def de_json(data, bot):
        if data is None:
            return None

        return MaskPosition(**data)

    
class Quiz:
    type: str = "quiz"

    def __init__(self, quiz_id, question, options, correct_option_id, owner_id):
        
        self.quiz_id: str = quiz_id                      
        self.question: str = question                    
        self.options: List[str] = [*options]             
        self.correct_option_id: int = correct_option_id 
        self.owner_id: int = owner_id                       
        self.winners: List[int] = []                     
        self.chat_id: int = 0                            
        self.message_id: int = 0                          
 

    
logging.basicConfig(filename='/home/pi/PekaCoolBot-master/PekaLog.log',level=logging.DEBUG)
led_states = [False for _ in range(6)]

width, height = lcd.dimensions()
spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
image = Image.new('1', (width, height),"black")
image.paste(spritemap,(width-32,33))
draw = ImageDraw.Draw(image)

font = ImageFont.truetype(fonts.AmaticSCBold, 38)

text = "Peka"

w, h = font.getsize(text)

x = (width - w) // 2
y = (height - h) // 2

draw.text((x, y), text, 1, font)
rainbow=False
r=0
g=0
b=0
Volume=0
Vocal=False
Stop=False
Count=5
Backlight=False
UwUMode=False
ImagePng=Image.new('1', (width, height),"black")
os.system("aplay -t raw -r 48000 -c 2 -f S16_LE /dev/zero &")
pygame.mixer.init()

def Rainbow():
    global r
    global g
    global b

    center=128
    width=127
    Len=50
    frequency1=0.2
    frequency2=0.2
    frequency3=0.2
    phase1=0
    phase2=2
    phase3=4
    red=r
    green=g
    blue=b
    

    for i in range( Len ):
        r =math.sin(frequency1*i + phase1) * width + center
        g =math.sin(frequency2*i + phase2) * width + center
        b =math.sin(frequency3*i + phase3) * width + center
        backlight.set_all(int(r),int(g),int(b))
        backlight.show()
        time.sleep(0.1)
        
    r=red
    g=green
    b=blue
    


def Size(text):
    fontsize = 1  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.50

    font = ImageFont.truetype(fonts.AmaticSCBold, fontsize)
    while font.getsize(text)[0] < img_fraction*image.size[0]:
    # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(fonts.AmaticSCBold, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1
    font = ImageFont.truetype(fonts.AmaticSCBold, fontsize)
    return(font)

def handler(ch, event):
     global Backlight
     global Volume
     global Count
     if event == 'press':
        if (ch == 0) and Volume<6:
            Volume=Volume+1
            pygame.mixer.music.set_volume(Volume/10)
        if (ch == 1) and Volume>0:
            Volume=Volume-1
            pygame.mixer.music.set_volume(Volume/10)
        if (ch == 2):
            Time()
        if ((ch == 4) and (Backlight==False)):
            Backlight=True
            backlight.set_all(0,0,0)
            
        else:
            if ((ch == 4) and (Backlight==True)): 
                Backlight=False
                backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
                
        for x in range(2,7):
           for y in range(56,8,-1):
               lcd.set_pixel(x, y, 0)
        for x in range(2,6):
           for y in range(56,int(56-(8*Volume)),-1):
               lcd.set_pixel(x+(y  % 2), y, x % 2)
        backlight.show()
        lcd.show()
        
def LedOnOff():
    # Turn on and off led 
    for x in range(6):
        touch.set_led(x, 1)
        time.sleep(0.1)
        touch.set_led(x, 0)

def MsgPrepare(msg):
    # We replace anything the font wont handle or things that shouldnt be remembered by Peka
    msg=msg.replace("/audio ", '')
    msg=msg.replace("/msg ", '')
    msg=msg.replace("/audio", '')
    msg=msg.replace("/msg", '')
    msg=msg.replace("é", "e'")
    msg=msg.replace("á", "a'")
    msg=msg.replace("í", "i'")
    msg=msg.replace("ú", "u'")
    msg=msg.replace("ó", "o'")
    msg=msg.replace("è", "e'")
    msg=msg.replace("à", "a'")
    msg=msg.replace("ì", "i'")
    msg=msg.replace("ù", "u'")
    msg=msg.replace("ò", "o'")
    return msg

def Meme(Text):
    i=1
    NewText=""
    for x in Text:
        if i%2==0:
            NewText=NewText+x.upper()
        else:
            NewText=NewText+x.lower()
        i+=1
    return NewText
    
# VERSION 2.0: added shit-ton of stuff,lazy to write
# VERSION 1.1: added volume control for screen
# VERSION 1.0: added audio mode + percent of random vocal to be sent instead of text
# VERSION 0.9: added UwU mode
# VERSION 0.8: added png mode + night mode for screen + On/Off screen button
# VERSION 0.7: added clock and face for Peka's screen
# VERSION 0.6: added 8ball mode 
# VERSION 0.5: added msg mode
# VERSION 0.4: implementation of the screen (GFX HAT) & Temperature mode
# VERSION 0.3: removed 100 messages limit, removed chain size and text size(defaults 3 and 1024), added algorithm and group settings.
# VERSION 0.2: removed ignored users array and added chance field on user model, and a settings panel.




__version__ = 1.1
temp = ""
debug_mode = config('DEBUG', cast=bool)
if(debug_mode):
    logging.basicConfig(level=logging.DEBUG)

# comment to use default timeout. (3.5)
telebot.apihelper.CONNECT_TIMEOUT = 9999


markov_algorithms = ["all_messages", "last_message"]
# Define database connector, comment/uncomment what you want to use.
# db = PostgresqlDatabase(config('PG_DTBS'), user=config('PG_USER'), password=config('PG_PASS'), host=config('PG_HOST'))
db = SqliteDatabase('{}.db'.format(__file__))
# db = MySQLDatabase(config('PG_DTBS'), user=config('PG_USER'), password=config('PG_PASS'), host=config('PG_HOST'), charset='utf8mb4')
quizzes_database = []
quizzes_owners = []
quizzes_winners = []

# Base class, every model inherits the database connector
class BaseModel(Model):
    class Meta:
        database = db
        

# Telegram user model
class TGUserModel(BaseModel):
    # Telegram data
    chat_id = CharField()
    first_name = CharField()
    username = CharField(null=True)
    language_code = CharField(default="en")
    # Markov settings
    # Chances of getting a response automatically. 10/50/90 % /mute for 0
    autoreply_chance = IntegerField(default=20)
    # Fixed chance of replying after 50/200/1000/5000 messages /mute for 0
    autoreply_fixed = IntegerField(default=200)
    # True for random chance | False for fixed
    random_autoreply = BooleanField(default=True)
    markov_algorithm = CharField(default="all_messages", choices=markov_algorithms)
    

# Model to store all messages
class UserMessageModel(BaseModel):
    user = ForeignKeyField(TGUserModel, backref='messages')
    message_id = CharField()
    chat_id = CharField()
    message_text = CharField(max_length=4000)


class GeneratedMessageModel(BaseModel):
    user = ForeignKeyField(TGUserModel, backref='generated_messages')
    chat_id = CharField(default="")
    message_text = CharField(max_length=1000)


# Store group admins and settings.
class GroupSettings(BaseModel):
    user = ForeignKeyField(TGUserModel)
    chat_id = CharField()
    override_settings = BooleanField(default=True)
    admins = ManyToManyField(TGUserModel, backref="groups")


# Create database file if it doesn't exists.
db.create_tables([TGUserModel, UserMessageModel, GeneratedMessageModel, GroupSettings,
                  GroupSettings.admins.get_through_model()], safe=True)

# Bot instance initialization.
bot = telebot.TeleBot(config('BOT_TOKEN'))
# Bot starts here.
logging.info('Bot started.')
try:
    bot_info = bot.get_me()
    logging.debug('{bot_info.first_name} @{bot_info.username}[{bot_info.id}]'.format(bot_info=bot_info))
except ApiException:
    logging.critical('The given token [{0}] is invalid, please fix it'.format(config('BOT_TOKEN')))
    exit(1)


# Return a TGUser instance based on telegram message instance.
def get_user_from_message(message: telebot.types.Message) -> TGUserModel:
    if(message.forward_from):
        logging.debug("Received a forwarded message.")
        user = message.forward_from  # If it was forwarder from a user, return forwarded message's user.
    elif(message.reply_to_message):
        logging.debug("Received a replied message.")
        user = message.reply_to_message.from_user  # If reply, user is resolved from the replied message.
    else:
        logging.debug("Received a normal message.")
        user: User = message.from_user   # Resolve user as message sender
    # Search user on database or create if it doesn't exists
    logging.debug("Using user {user.id} from message {message.message_id}".format(user=user, message=message))
    try:
        db_user: TGUserModel = TGUserModel.get(chat_id=user.id)
    # Update/Fill nickname and username
    except DoesNotExist:
        logging.debug("Creating user {user.id} {user.first_name} {user.username} {user.language_code}".format(user=user))
        db_user = TGUserModel.create(
            chat_id=user.id,
            first_name=user.first_name,
            username=user.username if user.username else None,
            language_code=user.language_code if user.language_code else 'en')
    return db_user




def get_group_from_message(message: Message) -> GroupSettings:
    # Create TGUser with group info. (YES i store chat groups as users)
    group_obj, created = TGUserModel.get_or_create(chat_id=message.chat.id, first_name=message.chat.title, username=message.chat.username)
    try:
        group_settings: GroupSettings = GroupSettings.get(GroupSettings.user == group_obj)
    except DoesNotExist:
        group_settings = GroupSettings.create(user=group_obj, chat_id=message.chat.id)
        admins_id = [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)]
        group_settings.admins = TGUserModel.select().where(TGUserModel.chat_id.in_(admins_id))
    return group_settings


# Add every text message to the database
def text_model_processor(messages: List[Message]):
    # logging.info("Processing %s new messages", len(messages))
    data_source = []
    for message in messages:
        # Only process text messages that are not commands and contains at least 3 words.
        if message.content_type == "text" and not message.text.startswith('/gnegne') and not message.text.startswith('/cardquiz') and not message.text.startswith('/point') and not message.text.startswith('/sellcard') and not message.text.startswith('/newcard') and not message.text.startswith('/png') and not message.text.startswith('/8') and not message.text.startswith('/uwu') and not message.text.startswith('/warzone') and not message.text.startswith('/multi') and not message.text.startswith('/tmp') and not message.text.startswith('/stats') and not message.text.startswith('/weekly')and not message.text.startswith('/tarot') and message.text.count(' ') >= 2:
            msg=message.text.replace("/audio ", '')
            user = get_user_from_message(message)
            data_source.append({
                'user': user, 'message_text': msg.lower(),
                'message_id': message.message_id, 'chat_id': message.chat.id
            })
            # UserMessageModel.create(user=user, message_text=message.text).save()
    logging.info("Saving {} text messages to the database".format(len(data_source)))
    if(data_source):
        with db.atomic():
            UserMessageModel.insert_many(data_source).execute()


bot.set_update_listener(text_model_processor)

# GLOBAL MESSAGES SECTION.
about_message = '''
Peka *%s*
[Source Code on Github](https://github.com/GaelicThunder/PekaCoolBot)
Author: @GaelicThunder
''' % __version__

bot_help_text = '''
Hi, i'm Peka, i can learn from people's messages and chat like them.
If you want me to generate a message, you can mention me, say my nickname or reply to any of my messages
If you want to play with the HentaiCardGame, then let me explain how it works:
- You start with 7 PekaPoints, this are the points you need to buy the cards
- You get points with CardQuiz or whenever Peka answer at your message randomly
- This cards are yours only, they can't be copied by other people
- Those cards comes in form of sticker that you can see only calling the bot, and they have their stats (Number of Tags, Tags, Page numbers and sauce number)
- Send a card to see the sauce 'wink wink'
- To see your cards just tag @PekaCoolBot and press [space]
- Before using Peka for this game, you have to start talking with her privatly and do /start
- In Groups, Peka needs to be an Admin to have full access to her functionality and being able to delete messages (this is only needed for a command)
List of commands:
- settings - Change Peka Settings
- msg - Send a message on Peka's monitor
- 8 - 8 Ball
- temp - Cpu temp 
- png - Get a png of Peka's screen 
- uwu - Go uwu mode for everyone
- stats - Show  various stats
- gnegne - Reprint the text you sent "wItH tHiS fOrMaT"
- audio - Make an audio, disabled since Amazon AWS isn't free
- tarot - under costruction

##### Call Of Duty Api [All of the CoD commands can be use with '[Battlenet Nickname] vs [Battlenet Nickname]' to do a comparison with someone else]
- warzone [Battlenet Nickname]- Show your Warzone stat
- multi [Battlenet Nickname]- Show your MW Multiplayer stat
- weekly [Battlenet Nickname]- Show your Weekly Warzone stat



##### Hentai Game Commands:
- newcard - Get a new card, cost 1 PekaPoint
- newcard '[sauce-number]' - Get the card of the sauce number provided, cost 10 PekaPoint
- sellcard - Sell a card and get back 1 PekaPoint
- cardquiz - Random Quiz, you can win PekaPoints
- point - See your PekaPoints
'''

settings_text = '''
{user.first_name}[{user.chat_id}]:
Messages sent: {messages} | generated: {generated}
Markov Algorithm: {algorithm} | Autoreply: {method}|{value}
'''

# When bot is added to group, get all admins and add them to internal admin list for this group
@bot.message_handler(content_types=['new_chat_members'])
def bot_added_to_chat(message: Message):
    if(any([user.id == bot_info.id for user in message.new_chat_members])):
        logging.info("Bot added to group {message.chat.id} {message.chat.title} by {message.from_user.id} {message.from_user.first_name}".format(message=message))
        get_group_from_message(message)


def is_private_chat(message: Message):
    return message.chat.type == 'private'


@bot.message_handler(commands=['start', 'help'], func=is_private_chat)
def greet_user(message: Message):
    bot.reply_to(message, bot_help_text, parse_mode="Markdown")


    
#####################COMMANDS###########################
@bot.inline_handler(lambda query: query.query == '')
def query_text(inline_query):
    path="/home/pi/PekaCoolBot-master/"+str(inline_query.from_user.id)
    lastoffset=inline_query.offset
    if lastoffset=="":
        lastoffset=0
    else:
        lastoffset=int(lastoffset)
    StickerAdded=0
    try:
        
        r=[]
        STICKER=bot.get_sticker_set('Peka'+str(inline_query.from_user.id)+"_by_PekaCoolBot").stickers[0].file_id
        StickerPack=bot.get_sticker_set('Peka'+str(inline_query.from_user.id)+"_by_PekaCoolBot").stickers
        
        i=0
        for x in StickerPack:
            
            if i>lastoffset and i<lastoffset+50:
                r.append(types.InlineQueryResultCachedSticker(random.randint(1,329922),x.file_id))
                StickerAdded+=1
            
                
            i+=1
        if lastoffset+StickerAdded==len(StickerPack):
                bot.answer_inline_query(inline_query.id,[r[x] for x in range(len(r))],cache_time=30,is_personal=True,next_offset="")

        else:
                bot.answer_inline_query(inline_query.id,[r[x] for x in range(len(r))],cache_time=30,is_personal=True,next_offset=lastoffset+StickerAdded)

  
    except Exception as e:
        print(e)
        
        
        
@bot.message_handler(commands=['sellcard'])
def sellcard(message: Message):
    bot.reply_to(message,"Answer this message with the card you wanna sell, you will get 1 PekaPoint!" , parse_mode="Markdown")

@bot.poll_answer_handler()
def handle_poll_answer(quiz_answer: types.PollAnswer):
    Voted=0
    with open("/home/pi/PekaCoolBot-master/Polls.txt",'rb') as f:
            SavedPoll=pickle.load(f)
    f.close()
    i=0
    for x in SavedPoll:
        if str(x[1].poll.id)==str(quiz_answer.poll_id):
            Members=bot.get_chat_members_count(x[0])
            Voted=x[2]
            if str(x[1].poll.correct_option_id)==str(quiz_answer.options_ids[0]):
                
                with open("/home/pi/PekaCoolBot-master/"+str(quiz_answer.user.id)+'/'+"PekaPoints.PP") as f:
                    PekaPoints =int(f.readline())
                f.close()
                PekaPoints+=1
                with open("/home/pi/PekaCoolBot-master/"+str(quiz_answer.user.id)+'/'+"PekaPoints.PP", 'w+') as f:
                    f.write(str(PekaPoints))
                f.close()
            
                
            Voted+=1
            if Voted>=Members-1:
                bot.stop_poll(x[1].chat.id,x[1].message_id)
                SavedPoll[i][2]=Voted
                with open("/home/pi/PekaCoolBot-master/Polls.txt", 'w+b') as f:
                    pickle.dump(SavedPoll,f)
                f.close()
            else:
                SavedPoll[i][2]=Voted
                with open("/home/pi/PekaCoolBot-master/Polls.txt", 'w+b') as f:
                    pickle.dump(SavedPoll,f)
                f.close()
            
        i+=1
        
@bot.message_handler(commands=['cardquiz'])
def cardquiz(message: Message):    
    SavedPoll=[]
    if os.path.exists("/home/pi/PekaCoolBot-master/Polls.txt"):    
        with open("/home/pi/PekaCoolBot-master/Polls.txt",'rb') as f:
            SavedPoll=pickle.load(f)
        f.close()
        for x in SavedPoll:
            if str(x[0])==str(message.chat.id):
                if x[1].poll.close_date>=int(datetime.now().timestamp()):
                    if x[2]<(bot.get_chat_members_count(x[0])-1):
                        bot.reply_to(message,"You can't request more than one Quiz at time, please wait until the last one is ended." , parse_mode="Markdown")
                        return False
    size=512,512
    bot.send_chat_action(message.chat.id,'upload_photo')
    path="/home/pi/PekaCoolBot-master/"
    Hentai=random.randint(1,329922)
    page="https://nhentai.net/g/"+str(Hentai)
    print (page)
    req = Request(url=page, headers={'User-Agent': 'Mozilla/5.0'}) 
    try:
        website = urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(e)
        bot.reply_to(message,"Wow, this one isn't there anymore, you must be unlucky as fuck." , parse_mode="Markdown")
        return False
    website = website.split("Uploaded:", 1)[0]
    pat = re.compile(r'data-src\s*=\s*(.+?(cover.jpg))')
    imglist=pat.findall(website)
    if len(imglist)>0 :
        img= ', '.join(map("".join, imglist[0]))
    else:
        
        pat = re.compile(r'data-src\s*=\s*(.+?(cover.png))')
    
        imglist=pat.findall(website)
        #print('IMGLIST\n'+str(imglist))
        if len(imglist)>0 :
            img= ', '.join(map("".join, imglist[0]))
        else:
            print("PARSING FAILED")
            bot.reply_to(message,"Sorry, something went wrong! Try again 👀" , parse_mode="Markdown")
            return False
    
    bot.send_chat_action(message.chat.id,'upload_photo')
    
    img=img.replace('data-src="', '')
    img=img.replace('"', '')
    img=img.replace(', cover.jpg', '')
    img=img.replace(', cover.png', '')
    response = requests.get(img)
    with open(path+"Quiz.jpg", 'w+b') as f:
       f.write(response.content)
    f.close()
    im= Image.open(path+"Quiz.jpg").convert("RGB")
    im.thumbnail(size, Image.BICUBIC)
    back = Image.new('RGBA', (512, 512), (255, 0, 0, 0))
    back.paste(im,(int((512-im.width)/2),int((512-im.height)/2)))
    back.save(path+"Quiz.webp","webp")

    pat = re.compile(r'\s*Pages:\s*(.+?((\d*)*<\/))')
    pagelist=pat.findall(website)
    page=str(pagelist[0][1]) 
    page=page[:-2]

    pat = re.compile(r'<a href="\/tag\/\s*\s*(.+?(\/"))')
    taglist=pat.findall(website)
    tag=[]
    i=0
    for x in taglist:
        string=str(x[0])
        string=string[:-2]
        tag.append(string)
        i+=1
    TotalTag=i
        
    keyboard = InlineKeyboardMarkup(3)
    
    bot.send_sticker(message.chat.id,open(path+"Quiz.webp","rb"))
    bot.send_chat_action(message.chat.id,'typing')
    
    
    if TotalTag>1:
        choice=random.choice(['N','Tag','NTag','Page'])
    else:
        choice=random.choice(['N','Tag','Page'])
    
    
    
    if choice=='N':
        CorrectPos=random.randint(0,2)
        if CorrectPos==0:
            Questions=(str(Hentai),str(Hentai+random.randint(-(Hentai-int(Hentai/2)),1000)),str(Hentai+random.randint(-(Hentai-int(Hentai/2)),1000)))
        if CorrectPos==1:
            Questions=(str(Hentai+random.randint(-(Hentai-int(Hentai/2)),1000)),str(Hentai),str(Hentai+random.randint(-(Hentai-int(Hentai/2)),1000)))
        if CorrectPos==2:
            Questions=(str(Hentai+random.randint(-(Hentai-int(Hentai/2)),1000)),str(Hentai+random.randint(-(Hentai-int(Hentai/2)),1000)),str(Hentai))
        Poll=bot.send_poll(message.chat.id,"Guess the sauce number!",Questions,is_anonymous=False,type='quiz',correct_option_id=CorrectPos,open_period=30)
    
    if choice=='Tag':
        populartags='https://nhentai.net/tags/popular'
        req = Request(url=populartags, headers={'User-Agent': 'Mozilla/5.0'}) 
        try:
            website = urlopen(req).read().decode('utf-8')
        except Exception as e:
            print(e)
        pat = re.compile(r'<a href="\/tag\/\s*\s*(.+?(\/"))')
        popularlist=pat.findall(website)
        randomtag=[]
        for x in popularlist:
            string=str(x[0])
            string=string[:-2]
            randomtag.append(string)
        randomtag = [ele for ele in randomtag if ele not in tag] 

        CorrectPos=random.randint(0,3)
        if CorrectPos==0:
            Questions=(random.choice(tag),random.choice(randomtag),random.choice(randomtag),random.choice(randomtag))
        if CorrectPos==1:
            Questions=(random.choice(randomtag),random.choice(tag),random.choice(randomtag),random.choice(randomtag))
        if CorrectPos==2:
            Questions=(random.choice(randomtag),random.choice(randomtag),random.choice(tag),random.choice(randomtag))
        if CorrectPos==3:
            Questions=(random.choice(randomtag),random.choice(randomtag),random.choice(randomtag),random.choice(tag))
        Poll=bot.send_poll(message.chat.id,"Guess the right Tag!",Questions,is_anonymous=False,type='quiz',correct_option_id=CorrectPos,open_period=30)
        
        
    if choice=='NTag':
        CorrectPos=random.randint(0,2)
        if CorrectPos==0:
            Questions=(str(TotalTag),str(TotalTag+random.randint(-(TotalTag-5),30)),str(TotalTag+random.randint(-(TotalTag-5),30)))
        if CorrectPos==1:
            Questions=(str(TotalTag+random.randint(-(TotalTag-5),30)),str(TotalTag),str(TotalTag+random.randint(-(TotalTag-5),30)))
        if CorrectPos==2:
            Questions=(str(TotalTag+random.randint(-(TotalTag-5),30)),str(TotalTag+random.randint(-(TotalTag-5),30)),str(TotalTag))
        Poll=bot.send_poll(message.chat.id,"Guess number of tags!",Questions,is_anonymous=False,type='quiz',correct_option_id=CorrectPos,open_period=30)
        
        
    if choice=='Page':
        CorrectPos=random.randint(0,2)
        if CorrectPos==0:
            Questions=(str(int(page)),str(int(page)+random.randint(-(int(page)-5),30)),str(int(page)+random.randint(-(int(page)-5),30)))
        if CorrectPos==1:
            Questions=(str(int(page)+random.randint(-(int(page)-5),30)),str(int(page)),str(int(page)+random.randint(-(int(page)-5),30)))
        if CorrectPos==2:
            Questions=(str(int(page)+random.randint(-(int(page)-5),30)),str(int(page)+random.randint(-(int(page)-5),30)),str(int(page)))
        Poll=bot.send_poll(message.chat.id,"Guess the number of pages!",Questions,is_anonymous=False,type='quiz',correct_option_id=CorrectPos,open_period=30)
    
    List=[]
    List.append([message.chat.id,Poll,0])
    for x in SavedPoll:
        if x[0]!=message.chat.id:
            List.append(x)
    with open("/home/pi/PekaCoolBot-master/Polls.txt", 'w+b') as f:
        pickle.dump(List,f)
    f.close()
    

    
@bot.message_handler(content_types=['sticker'], func=lambda m: m.reply_to_message)
def reply_on_sticker(message: Message):
    print(str(message.chat.id)+'\n')
    print(str(message.sticker)+'\n')
    if 'Peka' in str(message.sticker.set_name):
        bot.delete_sticker_from_set(message.sticker.file_id)
        bot.reply_to(message, 'Aaaaaaand is gone!')
        with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP") as f:
            PekaPoints =int(f.readline())
        f.close()
        PekaPoints+=1
        with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP", 'w+') as f:
            f.write(str(PekaPoints))
        f.close()
    else:
        if message.reply_to_message.text=="Answer this message with the card you wanna sell, you will get 1 PekaPoint!":
            bot.reply_to(message,"This is not a Peka Card!" , parse_mode="Markdown")
    
@bot.message_handler(commands=['point'])
def point(message: Message):
    with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP") as f:
            PekaPoints =f.readline()
    f.close()
    bot.reply_to(message,"You got "+PekaPoints +" PekaPoints!", parse_mode="Markdown")


    
    
@bot.message_handler(commands=['tarot'])
def tarot(message: Message):
    Question=message.text
    Question.replace("/tarot ", '')
    Question.replace("/tarot", '')
    random.seed(''.join(random.sample(Question, len(Question))))
    Deck=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
    random.shuffle(Deck)
    Orientation=random.choice(["Up","Reversed"])
    Card=str(random.choice(Deck))
    Desc=""
    
    if Card=="0" and Orientation=="Up":
        Desc="🔮Irrazionalitá\n🔮Spontaneitá\n🔮Inconscio\n🔮Libertá\n🔮Incertezza\n🔮Innocenza"
    if Card=="1" and Orientation=="Up":
        Desc="🔮Abilitá\n🔮Buona riuscita\n🔮Creativitá\n🔮Poter manifestare\n🔮Cambiamento da cogliere\n🔮Prendere decisioni importanti"
    if Card=="2" and Orientation=="Up":
        Desc="🔮Conoscenza\n🔮Saggezza\n🔮Riflessione\n🔮Persona che tende a nascondersi\n🔮Mistero\n🔮Figura femminile autoritaria"
    if Card=="3" and Orientation=="Up":
        Desc="🔮Creatività\n🔮Fecondità\n🔮Maternità\n🔮Empatia\n🔮Amore\n🔮Passione\n🔮Abbondanza\n🔮Successo"
    if Card=="4" and Orientation=="Up":
        Desc:"🔮Padre\n🔮Regole\n🔮Autorità\n🔮Responsabilità\n🔮Amante Irresistibile\n🔮Rapporto destinato a durare"
    if Card=="5" and Orientation=="Up":
        Desc="🔮Leggi spirituali\n🔮Tradizione\n🔮Educazione ricevuta\n🔮Coppia consolidata\n🔮Matrimonio\n🔮Giusta direzione"
    if Card=="6" and Orientation=="Up":
        Desc="🔮Relazione\n🔮Amore\n🔮Piacere\n🔮Scelta\n🔮Collaborazione"
    if Card=="7" and Orientation=="Up":
        Desc="🔮Realizzazione\n🔮Raggiungimento obiettivi\n🔮Volontà\n🔮Successo\n🔮Conquista\n🔮Situazione che va avanti"
    if Card=="8" and Orientation=="Up":
        Desc="🔮Vincita causa legale\n🔮Giudizio maturo\n🔮Lealtà verso sé stessi\n🔮Giusta decisione"
    if Card=="9" and Orientation=="Up":
        Desc="🔮Isolamento psicologico\n🔮Bisogno di distacco\n🔮Bisogno di stare soli\n🔮Non hai bisogno degli altri\n🔮Forza interiore"
    if Card=="10" and Orientation=="Up":
        Desc="🔮Destino\n🔮Karma\n🔮Cambiamento\n🔮Cambiamento in un momento difficile\n🔮Questioni nascoste vengono rivelate\n🔮Buoni investimenti\n🔮Entrate inaspettate\n🔮Collaborazioni valide"
    if Card=="11" and Orientation=="Up":
        Desc="🔮Attitudine interiore\n🔮Forza personale\n🔮Apertura\n🔮Fiducia in sè stessi\n🔮Coraggio\n🔮Trovare soluzioni\n🔮Situazioni da negative a positive\n🔮Tutto si aggiusta"
    if Card=="12" and Orientation=="Up":
        Desc="🔮Punti di vista differenti\n🔮Attaccamento\n🔮Sospensione\n🔮Anticonformismo\n🔮Blocco\n🔮Arresto\n🔮Periodo di riflessione"
    if Card=="13" and Orientation=="Up":
        Desc="🔮Fine di qualcosa\n🔮Trasformazione\n🔮Invito ad accettare gli eventi\n🔮Cambiamento\n🔮Rinascita dopo un periodo difficile"
    if Card=="14" and Orientation=="Up":
        Desc="🔮Agire con moderazione\n🔮Adottare la giusta misura\n🔮Pazienza\n🔮Azione lenta\n🔮Equilibrio\n🔮Lucidità"
    if Card=="15" and Orientation=="Up":
        Desc="🔮Eccesso\n🔮Tentazione\n🔮Dipendenza\n🔮Attaccamento(anche materiale)\n🔮Legami sessuali o materiali\n🔮Desiderio sessuale\n🔮Bisogna andare oltre la materialità"
    if Card=="16" and Orientation=="Up":
        Desc="🔮Evento inaspettato\n🔮Notizia shock\n🔮Fine di un rapporto\n🔮Rischio di tracollo emotivo\n🔮Arrivati al limite\n🔮Destabilizzazione"
    if Card=="17" and Orientation=="Up":
        Desc="🔮Risposta positiva\n🔮Momento favorevole\n🔮Comunicazione in arrivo\n🔮Desiderio\n🔮Idealizzazione"
    if Card=="18" and Orientation=="Up":
        Desc="🔮Confusione\n🔮Falsità\n🔮Cose non dette\n🔮Poca chiarezza\n🔮Qualcosa che non vediamo\n🔮Sotterfugi\n🔮Possibile gravidanza"
    if Card=="19" and Orientation=="Up":
        Desc="🔮Vittorie e successi\n🔮Chiarezza\n🔮Qualcosa viene alla luce\n🔮Pulizia mentale\n🔮Amore\n🔮Positività"
    if Card=="20" and Orientation =="Up":
        Desc="🔮Rinnovamento dopo una crisi\n🔮Ritorni dal passato\n🔮Chiamata\n🔮Eventi repentini\n🔮Rinascita\n🔮Giudizio\n🔮Annuncio\n🔮Richiamare l'attenzione su qualcuno o qualcosa"
    if Card=="21" and Orientation=="Up":
        Desc="🔮Completamento di un ciclo o percorso\n🔮Successo\n🔮Prosperità\n🔮Coltivare interessi e rapporti\n🔮Comunicazione con i social"

    #keyboard = InlineKeyboardMarkup(2)
    #keyboard.add(InlineKeyboardButton(Desc, None, 'Desc'))
    if Orientation=="Reversed":
        Card="R"+str(random.choice(Deck))
    bot.send_sticker(message.chat.id,open("/home/pi/PekaCoolBot-master/Tarot/"+Card+".webp","rb"))
    bot.send_message(message.chat.id,"_"+Desc+'_',parse_mode="Markdown")
    
    
@bot.message_handler(commands=['newcard'])
def newcard(message: Message):

    size=512,512
    isnew=False
    path="/home/pi/PekaCoolBot-master/"+str(message.from_user.id)
    message.text=message.text.replace('/newcard','')
    message.text=message.text.replace('@PekaCoolBot','')
    message.text=message.text.replace(' ','')
    Random=True
    try:
        os.mkdir(path)
        isnew=True
        PekaPoints=7
        with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP", 'w+') as f:
            f.write(str(PekaPoints))
        f.close()
    except OSError:
        print ("Creation of the directory %s failed" % path)
        with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP") as f:
            PekaPoints =int(f.readline())
        f.close()
        if len(message.text)>0:
            Random=False
            Hentai=message.text
        else:
            Hentai=random.randint(1,329922)
        if (PekaPoints<1) or (Hentai==message.text and PekaPoints<10):
            bot.reply_to(message,"Sorry, you need 1 PekaPoint for a random card and 10 PekaPoint for a Card of your choice" , parse_mode="Markdown")
            return False
        else:
            if Random==True:
                PekaPoints-=1
            else:
                PekaPoints-=10
        
    page="https://nhentai.net/g/"+str(Hentai)
    print (page)
    req = Request(url=page, headers={'User-Agent': 'Mozilla/5.0'}) 
    try:
        website = urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(e)
        bot.reply_to(message,"Sorry, something went wrong! Try again 👀" , parse_mode="Markdown")
        PekaPoints+=1
        with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP", 'w+') as f:
            f.write(str(PekaPoints))
        f.close()
        return False
    #print('WEBSITE\n'+str(type(website))+'\n'+str(website))
    website = website.split("Uploaded:", 1)[0]
    #print('WEBSITE AFTER REPLACE\n'+str(type(website))+'\n'+str(website))
    pat = re.compile(r'data-src\s*=\s*(.+?(cover.jpg))')
    
    imglist=pat.findall(website)
    #print('IMGLIST\n'+str(imglist))
    if len(imglist)>0 :
        img= ', '.join(map("".join, imglist[0]))
    else:
        
        pat = re.compile(r'data-src\s*=\s*(.+?(cover.png))')
    
        imglist=pat.findall(website)
        #print('IMGLIST\n'+str(imglist))
        if len(imglist)>0 :
            img= ', '.join(map("".join, imglist[0]))
        else:
            print("PARSING FAILED")
            bot.reply_to(message,"Sorry, something went wrong! Try again 👀" , parse_mode="Markdown")
            return False
    
    bot.send_chat_action(message.chat.id,'upload_photo')
    
    img=img.replace('data-src="', '')
    img=img.replace('"', '')
    img=img.replace(', cover.jpg', '')
    img=img.replace(', cover.png', '')
    print(img)
    response = requests.get(img)
    with open(path+"/"+str(Hentai)+".jpg", 'w+b') as f:
       f.write(response.content)
    f.close()
    im= Image.open(path+"/"+str(Hentai)+".jpg").convert("RGB")
    im.thumbnail(size, Image.BICUBIC)
    back = Image.new('RGBA', (512, 512), (255, 0, 0, 0))
    back.paste(im,(int((512-im.width)/2),int((512-im.height)/2)))
    back.save(path+"/"+str(Hentai)+".webp","webp")

    pat = re.compile(r'\s*Pages:\s*(.+?((\d*)*<\/))')
    pagelist=pat.findall(website)
    page=str(pagelist[0][1]) 
    page=page[:-2]
    
    
    
    with open(path+"/"+str(Hentai)+".stat", 'w+') as f:
        f.write(page+"\n")
    f.close()
    
    pat = re.compile(r'<a href="\/tag\/\s*\s*(.+?(\/"))')
    taglist=pat.findall(website)
    
    i=0
    tag=[]
    with open(path+"/"+str(Hentai)+".stat", 'a+') as f:
        for x in taglist:
            string=str(x[0])
            string=string[:-2]
            tag.append(string)
            f.write(string+"\n")
            i+=1
    TotalTag=i
    f.close()
    
    keyboard = InlineKeyboardMarkup(3)
    keyboard.add(InlineKeyboardButton("N° "+str(Hentai), None, 'Hentai'),InlineKeyboardButton("Tags " + str(TotalTag), None, 'TotalTag'),InlineKeyboardButton("Pages "+ str(page), None, 'page'))
    bot.send_sticker(message.chat.id,open(path+"/"+str(Hentai)+".webp","rb"),reply_markup=keyboard)
    
    with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP", 'w+') as f:
        f.write(str(PekaPoints))
    f.close()
    
    im= Image.open(path+"/"+str(Hentai)+".jpg").convert("RGB")
    im.thumbnail(size, Image.BICUBIC)
    back = Image.new('RGBA', (512, 512), (255, 0, 0, 0))
    back.paste(im,(int((512-im.width)/2),int((512-im.height)/2)))
    back.save(path+"/"+str(Hentai)+".png","png")
    mask=MaskPosition('eyes',float(Hentai),0.0,1.0)
    if isnew==True:
        print('New Deck Creation Peka'+str(message.from_user.username)+"_by_PekaCoolBot")
        try:
            (bot.create_new_sticker_set(user_id=message.from_user.id,name='Peka'+str(message.from_user.id)+"_by_PekaCoolBot",title='Peka'+str(message.from_user.id),emojis='🎱',png_sticker=open(path+"/"+str(Hentai)+".png","rb"),contains_masks=True,mask_position=mask))
            bot.send_message(message.from_user.id,"Here's your HentaiDeck! Don't share it! https://telegram.me/addstickers/"+'Peka'+str(message.from_user.id)+"_by_PekaCoolBot")
        except Exception as e:
            bot.reply_to(message,"Sorry, before getting your deck you must go on a private chat with me and press /start !" , parse_mode="Markdown")
    else:
        try:
            (bot.add_sticker_to_set(user_id=message.from_user.id,name='Peka'+str(message.from_user.id)+"_by_PekaCoolBot",emojis='🎱',png_sticker=open(path+"/"+str(Hentai)+".png","rb"),mask_position=mask))
        except Exception as e:
            print('New Deck Creation Peka'+str(message.from_user.username)+"_by_PekaCoolBot")
            (bot.create_new_sticker_set(user_id=message.from_user.id,name='Peka'+str(message.from_user.id)+"_by_PekaCoolBot",title='Peka'+str(message.from_user.id),emojis='🎱',png_sticker=open(path+"/"+str(Hentai)+".png","rb"),contains_masks=True,mask_position=mask))
            bot.send_message(message.from_user.id,"Here's your HentaiDeck! Don't share it! https://telegram.me/addstickers/"+'Peka'+str(message.from_user.id)+"_by_PekaCoolBot")
            bot.reply_to(message,"Sorry, before getting your deck you must go on a private chat with me and press /start !" , parse_mode="Markdown")
    os.remove(path+"/"+str(Hentai)+".jpg")
    
                    
@bot.message_handler(commands=['duel'])
def duel(message: Message):
    return False


@bot.message_handler(commands=['weekly'])
def warzone(message: Message):
    msg=message.text
    msg=msg.replace("/weekly ", '')
    
    msg=msg.replace("#", '%23')
    
    
    
    bot.send_chat_action(message.chat.id,'typing')
    if "vs" in msg:
        msg=msg.split()
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/"+ msg[0] + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson=response.json()
        time.sleep(1)
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/"+ msg[2] + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson2=response.json()
        space=" "
        kills="Kills = "+space*(27-(len("Kills =  ")))  + str(responsejson["wz"]["all"]["properties"]["kills"])+"     "+ str(responsejson2["wz"]["all"]["properties"]["kills"]) + "\n"
        deaths="Deaths = "+space*(27-(len("Deaths =  ")))  + str(responsejson["wz"]["all"]["properties"]["deaths"])+"     "+ str(responsejson2["wz"]["all"]["properties"]["deaths"]) + "\n"
        kdRatio="KDRatio = "+space*(27-(len("KDRatio =  ")))  + str(round(responsejson["wz"]["all"]["properties"]["kdRatio"],2))+"     "+ str(round(responsejson2["wz"]["all"]["properties"]["kdRatio"],2)) + "\n"
        executions="Executions = "+space*(27-(len("Executions =  ")))  + str(responsejson["wz"]["all"]["properties"]["executions"])+"     "+ str(responsejson2["wz"]["all"]["properties"]["executions"]) + "\n"
        headshotPercentage="HeadshotPercentage = "+space*(27-(len("HeadshotPercentage =  ")))  + str(round(float(responsejson["wz"]["all"]["properties"]["headshotPercentage"]),2))+"        "+ str(round(float(responsejson2["wz"]["all"]["properties"]["headshotPercentage"]),2)) + "\n"
        assists="Assists = "+space*(27-(len("Assists =  ")))  + str(responsejson["wz"]["all"]["properties"]["assists"])+"     "+ str(responsejson2["wz"]["all"]["properties"]["assists"]) + "\n"
        score="Score = "+space*(27-(len("Score =  ")))  + str(responsejson["wz"]["all"]["properties"]["score"])+"   "+ str(responsejson2["wz"]["all"]["properties"]["score"]) + "\n"
        matchesPlayed="MatchesPlayed = "+space*(27-(len("MatchesPlayed =  ")))  + str(responsejson["wz"]["all"]["properties"]["matchesPlayed"])+"        "+ str(responsejson2["wz"]["all"]["properties"]["matchesPlayed"]) + "\n"
    
        bot.reply_to(message,"`"+msg[0].replace("%23", '#')+"  VS  "+msg[2].replace("%23", '#')+"\n"+kills+deaths+kdRatio+executions+headshotPercentage+assists+score+matchesPlayed+"`", parse_mode="Markdown")
        
    else:
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/"+ msg + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson=response.json()
        space=" "
        kills="Kills = "+space*(27-(len("Kills =  "))) + str(responsejson["wz"]["all"]["properties"]["kills"]) + "\n"
        deaths="Deaths = "+space*(27-(len("Deaths =  "))) + str(responsejson["wz"]["all"]["properties"]["deaths"]) + "\n"
        kdRatio="KDRatio = "+space*(27-(len("KDRatio =  "))) + str(round(responsejson["wz"]["all"]["properties"]["kdRatio"],2)) + "\n"
        executions="Executions = "+space*(27-(len("Executions =  "))) + str(responsejson["wz"]["all"]["properties"]["executions"]) + "\n"
        headshotPercentage="HeadshotPercentage = "+space*(27-(len("HeadshotPercentage =  "))) + str(round(float(responsejson["wz"]["all"]["properties"]["headshotPercentage"]),2)) + "\n"
        assists="Assists = "+space*(27-(len("Assists =  "))) + str(responsejson["wz"]["all"]["properties"]["assists"]) + "\n"
        score="Score = "+space*(27-(len("Score =  "))) + str(responsejson["wz"]["all"]["properties"]["score"]) + "\n"
        matchesPlayed="MatchesPlayed = "+space*(27-(len("MatchesPlayed =  "))) + str(responsejson["wz"]["all"]["properties"]["matchesPlayed"]) + "\n"
    
        bot.reply_to(message, "`"+kills+deaths+kdRatio+executions+headshotPercentage+assists+score+matchesPlayed+"`", parse_mode="Markdown")
    


@bot.message_handler(commands=['warzone'])
def warzone(message: Message):
    msg=message.text
    msg=msg.replace("/warzone ", '')

    msg=msg.replace("#", '%23')
    
    
    
    bot.send_chat_action(message.chat.id,'typing')
    if "vs" in msg:
        msg=msg.split()
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/"+ msg[0] + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson=response.json()
        time.sleep(1)
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/"+ msg[2] + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson2=response.json()
        space=" "
        wins="Wins =  "+space*(27-(len("Wins =  "))) + str(responsejson["br_all"]["wins"]) +"        "+ str(responsejson2["br_all"]["wins"]) + "\n"
        kills="Kills = "+space*(27-(len("Kills =  ")))  + str(responsejson["br_all"]["kills"])+"     "+ str(responsejson2["br_all"]["kills"]) + "\n"
        deaths="Deaths = "+space*(27-(len("Deaths =  ")))  + str(responsejson["br_all"]["deaths"])+"     "+ str(responsejson2["br_all"]["deaths"]) + "\n"
        kdRatio="KDRatio = "+space*(27-(len("KDRatio =  ")))  + str(round(responsejson["br_all"]["kdRatio"],2))+"     "+ str(round(responsejson2["br_all"]["kdRatio"],2)) + "\n"
        downs="Downs = "+space*(27-(len("Downs =  ")))  + str(responsejson["br_all"]["downs"])+"     "+ str(responsejson2["br_all"]["downs"]) + "\n"
        revives="Revives = "+space*(27-(len("Revives =  ")))  + str(responsejson["br_all"]["revives"])+"        "+ str(responsejson2["br_all"]["revives"]) + "\n"
        contracts="Contracts = "+space*(27-(len("Contracts =  ")))  + str(responsejson["br_all"]["contracts"])+"     "+ str(responsejson2["br_all"]["contracts"]) + "\n"
        score="Score = "+space*(27-(len("Score =  ")))  + str(responsejson["br_all"]["score"])+"   "+ str(responsejson2["br_all"]["score"]) + "\n"
        gamesPlayed="GamesPlayed = "+space*(27-(len("GamesPlayed =  ")))  + str(responsejson["br_all"]["gamesPlayed"])+"        "+ str(responsejson2["br_all"]["gamesPlayed"]) + "\n"
    
        bot.reply_to(message,"`"+msg[0].replace("%23", '#')+"  VS  "+msg[2].replace("%23", '#')+"\n"+wins+kills+deaths+kdRatio+downs+revives+contracts+score+gamesPlayed+"`", parse_mode="Markdown")
        
    else:
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/"+ msg + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson=response.json()
        space=" "
        wins="Wins =  "+space*(27-(len("Wins =  ")))+ str(responsejson["br_all"]["wins"]) + "\n"
        kills="Kills = "+space*(27-(len("Kills =  "))) + str(responsejson["br_all"]["kills"]) + "\n"
        deaths="Deaths = "+space*(27-(len("Deaths =  "))) + str(responsejson["br_all"]["deaths"]) + "\n"
        kdRatio="KDRatio = "+space*(27-(len("KDRatio =  "))) + str(round(responsejson["br_all"]["kdRatio"],2)) + "\n"
        downs="Downs = "+space*(27-(len("Downs =  "))) + str(responsejson["br_all"]["downs"]) + "\n"
        revives="Revives = "+space*(27-(len("Revives =  "))) + str(responsejson["br_all"]["revives"]) + "\n"
        contracts="Contracts = "+space*(27-(len("Contracts =  "))) + str(responsejson["br_all"]["contracts"]) + "\n"
        score="Score = "+space*(27-(len("Score =  "))) + str(responsejson["br_all"]["score"]) + "\n"
        gamesPlayed="GamesPlayed = "+space*(27-(len("GamesPlayed =  "))) + str(responsejson["br_all"]["gamesPlayed"]) + "\n"
    
        bot.reply_to(message, "`"+wins+kills+deaths+kdRatio+downs+revives+contracts+score+gamesPlayed+"`", parse_mode="Markdown")
    
@bot.message_handler(commands=['multi'])
def multi(message: Message):
    msg=message.text
    msg=msg.replace("/multi ", '')
    

    
    msg=msg.replace("#", '%23')
    
    
    
    bot.send_chat_action(message.chat.id,'typing')
    if "vs" in msg:
        msg=msg.split()
        
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer/"+ msg[0] + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson=response.json()
        
        time.sleep(1)
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer/"+ msg[2] + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson2=response.json()        
        space=" "
        wins="Wins =  "+space*(27-(len("Wins =  "))) +str(responsejson["lifetime"]["all"]["properties"]["wins"])+"     "+str(responsejson2["lifetime"]["all"]["properties"]["wins"]) + "\n"
        losses="Losses =  "+space*(27-(len("Losses =  ")))+str(responsejson["lifetime"]["all"]["properties"]["losses"])+"     "+str(responsejson2["lifetime"]["all"]["properties"]["losses"]) + "\n"
        winLossRatio="WinLossRatio =  "+space*(27-(len("WinLossRatio =  ")))+str(round(responsejson["lifetime"]["all"]["properties"]["winLossRatio"],2))+"     "+str(round(responsejson2["lifetime"]["all"]["properties"]["winLossRatio"],2)) + "\n"
        kills="Kills = " +space*(27-(len("Kills =  ")))+str(responsejson["lifetime"]["all"]["properties"]["kills"])+"     "+str(responsejson2["lifetime"]["all"]["properties"]["kills"]) + "\n"
        deaths="Deaths = " + space*(27-(len("Deaths =  ")))+str(responsejson["lifetime"]["all"]["properties"]["deaths"])+"     "+ str(responsejson2["lifetime"]["all"]["properties"]["deaths"])+ "\n"
        kdRatio="KDRatio = " +space*(27-(len("KDRatio =  "))) +str(round(responsejson["lifetime"]["all"]["properties"]["kdRatio"],2))+"     "+str(round(responsejson2["lifetime"]["all"]["properties"]["kdRatio"],2)) + "\n"
        bestKD="BestKD = " +space*(27-(len("BestKD =  ")))+ str(responsejson["lifetime"]["all"]["properties"]["bestKD"])+"        "+ str(responsejson2["lifetime"]["all"]["properties"]["bestKD"])+ "\n"
        accuracy="Accuracy = " +space*(27-(len("Accuracy =  "))) + str(round(responsejson["lifetime"]["all"]["properties"]["accuracy"],2))+"     "+ str(round(responsejson2["lifetime"]["all"]["properties"]["accuracy"],2))+ "\n"
        recordKillsInAMatch="Record Kills = " +space*(27-(len("Record Kills =  "))) + str(responsejson["lifetime"]["all"]["properties"]["recordKillsInAMatch"])+"        "+str(responsejson2["lifetime"]["all"]["properties"]["recordKillsInAMatch"]) + "\n"
        headshots="Headshots = "  +space*(27-(len("Headshots =  ")))+ str(responsejson["lifetime"]["all"]["properties"]["headshots"])+"     "+str(responsejson2["lifetime"]["all"]["properties"]["headshots"]) + "\n"
        bestCaptures="BestCaptures = " +space*(27-(len("BestCaptures =  "))) + str(responsejson["lifetime"]["all"]["properties"]["bestCaptures"])+"        "+ str(responsejson2["lifetime"]["all"]["properties"]["bestCaptures"])+ "\n"
        score="Score = " +space*(27-(len("Score =  "))) + str(responsejson["lifetime"]["all"]["properties"]["score"])+"   "+ str(responsejson2["lifetime"]["all"]["properties"]["score"]) + "\n"
        gamesPlayed="GamesPlayed = " +space*(27-(len("GamesPlayed =  "))) + str(responsejson["lifetime"]["all"]["properties"]["gamesPlayed"])+"        "+ str(responsejson2["lifetime"]["all"]["properties"]["gamesPlayed"])+ "\n"
        bot.reply_to(message,"`"+msg[0].replace("%23", '#')+"  VS  "+msg[2].replace("%23", '#')+"\n"+wins+losses+winLossRatio+kills+deaths+kdRatio+bestKD+accuracy+recordKillsInAMatch+headshots+bestCaptures+score+gamesPlayed+"`", parse_mode="Markdown")
    
    else:
        url = "https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer/"+ msg + "/battle"
        headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "7da4344329mshd8c99e6703b461ep132daajsnb60baa04142c"
        }
        response = requests.request("GET", url, headers=headers)
        responsejson=response.json()
        space=" "
        wins="Wins =  "+space*(27-(len("Wins =  ")))+ str(responsejson["lifetime"]["all"]["properties"]["wins"]) + "\n"
        losses="Losses =  "+space*(27-(len("Losses =  ")))+ str(responsejson["lifetime"]["all"]["properties"]["losses"]) + "\n"
        winLossRatio="WinLossRatio =  "+space*(27-(len("WinLossRatio =  ")))+ str(round(responsejson["lifetime"]["all"]["properties"]["winLossRatio"],2)) + "\n"
        kills="Kills = " +space*(27-(len("Kills =  ")))+ str(responsejson["lifetime"]["all"]["properties"]["kills"]) + "\n"
        deaths="Deaths = " +space*(27-(len("Deaths =  ")))+ str(responsejson["lifetime"]["all"]["properties"]["deaths"]) + "\n"
        kdRatio="KDRatio = "+space*(27-(len("KDRatio =  "))) + str(round(responsejson["lifetime"]["all"]["properties"]["kdRatio"],2)) + "\n"
        bestKD="BestKD = "+space*(27-(len("BestKD =  "))) + str(responsejson["lifetime"]["all"]["properties"]["bestKD"]) + "\n"
        accuracy="Accuracy = "+space*(27-(len("Accuracy =  "))) + str(round(responsejson["lifetime"]["all"]["properties"]["accuracy"],2)) + "\n"
        recordKillsInAMatch="Record Kills = "+space*(27-(len("Record Kills =  "))) + str(responsejson["lifetime"]["all"]["properties"]["recordKillsInAMatch"]) + "\n"
        headshots="Headshots = "+space*(27-(len("Headshots =  "))) + str(responsejson["lifetime"]["all"]["properties"]["headshots"]) + "\n"
        bestCaptures="BestCaptures = "+space*(27-(len("BestCaptures =  "))) + str(responsejson["lifetime"]["all"]["properties"]["bestCaptures"]) + "\n"
        score="Score = "+space*(27-(len("Score =  "))) + str(responsejson["lifetime"]["all"]["properties"]["score"]) + "\n"
        gamesPlayed="GamesPlayed = "+space*(27-(len("GamesPlayed =  "))) + str(responsejson["lifetime"]["all"]["properties"]["gamesPlayed"]) + "\n"
        bot.reply_to(message, "`"+wins+losses+winLossRatio+kills+deaths+kdRatio+bestKD+accuracy+recordKillsInAMatch+headshots+bestCaptures+score+gamesPlayed+"`", parse_mode="Markdown")

@bot.message_handler(commands=['audio'])
def audio(message: Message):
    global ImagePng
    global Count
    global Stop
    DeleteMsg=False
    Stop=True
    Count=30
    lcd.clear
    # Prepare the text

    msg = message.text
    if ("/audio " in msg) or ("/audio" in msg) :
       DeleteMsg=True
    msg=msg.replace("/audio ", '')
    msg=msg.replace("/audio", '')
    screenmsg=MsgPrepare(msg)
    bot.send_chat_action(message.chat.id,'record_audio')
    # We load the font and prepare the the screen
    font = ImageFont.truetype("/home/pi/PekaCoolBot-master/CCFONT.ttf", 12)
    width, height = lcd.dimensions()
    spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
    image = Image.new('1', (width, height),"black")
    image.paste(spritemap,(width-32,33))
    draw = ImageDraw.Draw(image)
    lines = textwrap.wrap(screenmsg, width=16)
    y_text = 0
    for line in lines:
        w, h = font.getsize(line)
        draw.text(((width-w)/4, y_text), line,1, font=font)
        y_text += h
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)

    
    # Save the image for /png command
    ImagePng=image
    
    # Debug chat id printing
    print("Chat ID for Audio Request: "+str(message.chat.id))
    
    # We request Aws voice (in english or italian in this case)
    # I opted for .ogg cause the telegram vocals are .ogg
    if message.chat.id==1234:
        polly_client = boto3.Session(
                aws_access_key_id="",                     
                aws_secret_access_key="",
                region_name='us-east-1').client('polly')
        response = polly_client.synthesize_speech(VoiceId='Salli',
                OutputFormat='ogg_vorbis', 
                Text = msg)
    else:
        polly_client = boto3.Session(
                aws_access_key_id="",                     
                aws_secret_access_key="",
                region_name='us-east-1').client('polly')
        response = polly_client.synthesize_speech(VoiceId='Bianca',
                OutputFormat='ogg_vorbis', 
                Text = msg)
    # Save the received audio
    with open('/home/pi/PekaCoolBot-master/vocal.ogg', 'wb') as f:
       f.write(response['AudioStream'].read())
    f.close()
    # Send the saved vocal
    bot.send_voice(message.chat.id,voice=open("/home/pi/PekaCoolBot-master/vocal.ogg","rb"))
    # If Peka is an admin in the group or in private and the message is from a command she will delete the message
    if DeleteMsg==True:
        bot.delete_message(message.chat.id,message.message_id)
    
    pygame.mixer.music.load("/home/pi/PekaCoolBot-master/vocal.ogg")
    pygame.mixer.music.play()
    backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    backlight.show()
    lcd.show()
    # Release the Stop variable 
    Stop=False
    LedOnOff()


@bot.message_handler(commands=['png'])
def Png(message: Message):
    global ImagePng
    bot.send_chat_action(message.chat.id,'upload_photo')
    # Convert to RGB and save it
    ImagePng=ImagePng.convert('RGB')
    ImageConverted=ImageOps.invert(ImagePng)
    # Invert the image since the colors are inverted
    ImageConverted.save("/home/pi/PekaCoolBot-master/Screen.png")
    bot.send_photo(message.chat.id,photo=open("/home/pi/PekaCoolBot-master/Screen.png","rb"))
    LedOnOff()

@bot.message_handler(commands=['temp'])
def Temp(message: Message):
    # Get Temperature of the CPU
    bot.send_chat_action(message.chat.id,'typing')
    temp = os.popen("vcgencmd measure_temp").readline()
    bot.reply_to(message, temp, parse_mode="Markdown")
    LedOnOff()

@bot.message_handler(commands=['stats'])
def PIStats(message: Message):
    bot.send_chat_action(message.chat.id,'typing')
    
    # CPU info
    cpuUsage =  str(psutil.cpu_percent()) + '%'
    
    # RAM informations
    memory = psutil.virtual_memory()
    # Divide from Bytes -> KB -> MB
    available = round(memory.available/1024.0/1024.0,1)
    total = round(memory.total/1024.0/1024.0,1)
    memoryStats = str(available) + 'MB free / ' + str(total) + 'MB total ( ' + str(memory.percent) + '% )'

    # Disk informations
    disk = psutil.disk_usage('/')
    # Divide from Bytes -> KB -> MB -> GB
    free = round(disk.free/1024.0/1024.0/1024.0,1)
    total = round(disk.total/1024.0/1024.0/1024.0,1)
    diskStats = str(free) + 'GB free / ' + str(total) + 'GB total ( ' + str(disk.percent) + '% )'

    # generic local machine information
    temperature = os.popen("vcgencmd measure_temp").readline()
    temperature = temperature.replace("temp=", "")
    # compose the final message
    FinalMessage = "CPU info %s\nRAM info %s\nDisk info %s\nTemperature %s\n" % (cpuUsage, memoryStats, diskStats, temperature)
    
    bot.reply_to(message, FinalMessage, parse_mode="Markdown")
    LedOnOff()


    
@bot.message_handler(commands=['gnegne'])
def gnegne(message: Message):
    bot.send_chat_action(message.chat.id,'typing')
    Text=message.text.replace("/gnegne ", '')
    Text=Meme(Text)
    bot.delete_message(message.chat.id,message.message_id)
    bot.send_message(message.chat.id,Text, parse_mode="Markdown")
        
    
@bot.message_handler(commands=['uwu'])
def UwU(message: Message):
    bot.send_chat_action(message.chat.id,'typing')
    global UwUMode
    if UwUMode==False:
       UwUMode=True
       bot.reply_to(message, "UwU Mode Activated", parse_mode="Markdown")
    else:
       UwUMode=False
       bot.reply_to(message, "UwU Mode Deactivated", parse_mode="Markdown")
    LedOnOff()

def DrawTriangle(draw):
    # Draw the triangle on the Screen
    draw.line([(32,8),(96,8)],fill ="white",width=1)
    draw.line([(32,8),(64,56)],fill ="white",width=1)
    draw.line([(96,8),(64,56)],fill ="white",width=1)
    return draw
    
def Time():
    global Stop
    global ImagePng
    global Count
    global Volume
    
    Stop=True
    Count=10
    lcd.clear
    # Get the time
    time = os.popen("date +%R").readline()
    # Prepare the screen 
    font = ImageFont.truetype(fonts.FredokaOne, 26)
    width, height = lcd.dimensions()
    spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
    image = Image.new('1', (width, height),"black")
    image.paste(spritemap,(width-32,33))
    draw = ImageDraw.Draw(image)
    draw = DrawTriangle(draw)
    w, h = font.getsize(time)
    draw.text(((width-w+16)/2, 16), time,1, font=font)
    ImagePng=image
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    lcd.show()
    # If it's night lower the Led colour and brightness
    date=datetime.now()
    
    #if strftime("%A")==" " 
    
    if date.hour>23 or date.hour<11:
      backlight.set_all(0,0,0)
      Volume=0
    else:
      backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    backlight.show()
    Stop=False
    

@bot.message_handler(commands=['msg'])
def Msg(message: Message):
    global Stop
    global Count
    global ImagePng
    bot.send_chat_action(message.chat.id,'typing')
    Stop=True
    Count=30
    lcd.clear
    # Prepare the message
    msg = message.text
    msg = MsgPrepare(msg)
    # Prepare the screen 
    font = ImageFont.truetype("/home/pi/PekaCoolBot-master/CCFONT.ttf", 12)
    width, height = lcd.dimensions()
    spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
    image = Image.new('1', (width, height),"black")
    image.paste(spritemap,(width-32,33))
    draw = ImageDraw.Draw(image)
    lines = textwrap.wrap(msg, width=16)
    y_text = 0
    for line in lines:
        w, h = font.getsize(line)
        draw.text(((width-w)/4, y_text), line,1, font=font)
        y_text += h
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    backlight.show()
    lcd.show()
    # Save the image for /png command
    ImagePng=image
    # Let know the user that the message has been sent
    bot.reply_to(message, "✔️", parse_mode="Markdown")
    LedOnOff()
    Stop=False

@bot.message_handler(commands=['8'])
def Ball(message: Message):
    global Stop
    global Count
    global ImagePng
    bot.send_chat_action(message.chat.id,'typing')
    Stop=True
    Count=15
    lcd.clear
    # Create the 8Ball answers
    Ball = ["🎱 As I see it, yes 🎱","🎱 It is certain 🎱","🎱 It is decidedly so 🎱","🎱 Most likely 🎱","🎱 Outlook good 🎱","🎱 Signs point to yes 🎱","🎱 Without a doubt 🎱","🎱 Yes,Yes – definitely 🎱","🎱 You may rely on it 🎱","🎱 Reply hazy, try again 🎱","🎱 Ask again later 🎱","🎱 Better not tell you now 🎱","🎱 Cannot predict now 🎱","🎱 Concentrate and ask again 🎱","🎱 Don't count on it 🎱","🎱 My reply is no 🎱","🎱 My sources say no 🎱","🎱 Outlook not so good 🎱","🎱 Very doubtful 🎱"]
    # Decide a random answer
    choose=random.choice(Ball)
    #Prepare the screen
    font = ImageFont.truetype("/home/pi/PekaCoolBot-master/CCFONT.ttf", 12)
    width, height = lcd.dimensions()
    spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
    image = Image.new('1', (width, height),"black")
    image.paste(spritemap,(width-32,33))
    draw = ImageDraw.Draw(image)
    draw = DrawTriangle(draw)
    lines = textwrap.wrap(choose, width=16)
    y_text = 16
    for line in lines:
        w, h = font.getsize(line)
        draw.text(((width-w)/2, y_text), line,1, font=font)
        y_text += h
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    backlight.show()
    lcd.show()
    bot.reply_to(message, choose, parse_mode="Markdown")
    # Save the image for /png command
    ImagePng=image
    LedOnOff()
    Stop=False


@bot.message_handler(commands=['about'], func=is_private_chat)
def about(message: Message):
    bot.reply_to(message, about_message, parse_mode="Markdown")
########################################################

def get_statistics(user_obj: TGUserModel):
    message_count = user_obj.messages.count()
    generated_messages = user_obj.generated_messages.count()
    algorithm = user_obj.markov_algorithm
    method = "Random" if user_obj.random_autoreply else "Fixed"
    value = user_obj.autoreply_chance if user_obj.random_autoreply else user_obj.autoreply_fixed
    return settings_text.format(
        user=user_obj, messages=message_count, generated=generated_messages,
        algorithm=algorithm, method=method, value=value
    )


def generate_settings_keyboard(user_obj: TGUserModel):
    keyboard = InlineKeyboardMarkup(4)
    if(user_obj.random_autoreply):
        autoreply_type: InlineKeyboardButton = InlineKeyboardButton('Change autoreply to fixed', None, 'autoreply')
        chances: List[InlineKeyboardButton] = [
            InlineKeyboardButton(str(chance), None, str(chance)) for chance in [0, 20, 50, 90]
        ]
    else:
        autoreply_type: InlineKeyboardButton = InlineKeyboardButton('Change autoreply to random', None, 'autoreply')
        chances: List[InlineKeyboardButton] = [
            InlineKeyboardButton(str(chance), None, str(chance)) for chance in [0, 20, 200, 2000]
        ]
    keyboard.add(autoreply_type)
    keyboard.add(*chances)
    keyboard.add(InlineKeyboardButton("Markov Algorithm", None, 'algorithm'), InlineKeyboardButton("X", None, "close"))
    return keyboard


def get_group_statistics(group: GroupSettings):
    message_count = UserMessageModel.select().where(UserMessageModel.chat_id==group.chat_id).count()
    generated_messages = GeneratedMessageModel.select().where(GeneratedMessageModel.chat_id == group.chat_id).count()
    algorithm = group.user.markov_algorithm
    method = "Random" if group.user.random_autoreply else "Fixed"
    value = group.user.autoreply_chance if group.user.random_autoreply else group.user.autoreply_fixed
    return settings_text.format(
        user=group.user, messages=message_count, generated=generated_messages,
        algorithm=algorithm, method=method, value=value
    ) + "\nOverride User Settings: {}".format("YES" if group.override_settings else "NO")


def group_keyboard(group: GroupSettings, admin: TGUserModel):
    keyboard = InlineKeyboardMarkup(4)
    if(group.user.random_autoreply):
        autoreply_type: InlineKeyboardButton = InlineKeyboardButton('Change autoreply to fixed', None, 'group_autoreply')
        chances: List[InlineKeyboardButton] = [
            InlineKeyboardButton(str(chance), None, 'group_{}'.format(chance)) for chance in [0, 10, 50, 90]
        ]
    else:
        autoreply_type: InlineKeyboardButton = InlineKeyboardButton('Change autoreply to random', None, 'group_autoreply')
        chances: List[InlineKeyboardButton] = [
            InlineKeyboardButton(str(chance), None, 'group_{}'.format(chance)) for chance in [0, 20, 200, 2000]
        ]
    override_button: InlineKeyboardButton = InlineKeyboardButton('Toggle Override User Settings', None, 'group_override')
    keyboard.add(autoreply_type)
    keyboard.add(*chances)
    keyboard.add(InlineKeyboardButton("Markov Algorithm", None, 'group_algorithm'), override_button)
    keyboard.add(InlineKeyboardButton("See personal settings", None, "personal_{}".format(admin.chat_id)), InlineKeyboardButton("X", None, "close"))
    return keyboard


@bot.message_handler(commands=['settings'])
def send_user_statistics(message: Message):
    user_obj: TGUserModel = get_user_from_message(message)
    keyboard: InlineKeyboardMarkup = None
    stats: str = get_statistics(user_obj)
    # If private chat
    if(is_private_chat(message)):
        logging.debug('Settings in private chat')
        keyboard: InlineKeyboardMarkup = generate_settings_keyboard(user_obj)
    if(message.chat.type in ['group', 'supergroup']):
        group: GroupSettings = GroupSettings.get(GroupSettings.chat_id == message.chat.id)
        if (user_obj in group.admins):
            stats = get_group_statistics(group)
            keyboard = group_keyboard(group, user_obj)
    bot.reply_to(message, stats, reply_markup=keyboard)


# Mute is shortcut to setting all chances to zero, for groups and users.
@bot.message_handler(commands=['mute'])
def mute_bot(message: Message):
    user_obj: TGUserModel = get_user_from_message(message)
    if(message.chat.type in ['group', 'supergroup']):
        group: GroupSettings = GroupSettings.get(GroupSettings.chat_id == message.chat.id)
        if (user_obj in group.admins):
            group.override_settings = True
            group.user.autoreply_chance = 0
            group.user.autoreply_fixed = 0
            group.save()
            bot.reply_to(message, "I will not reply randomly anymore.")
        else:
            user_obj.autoreply_chance = 0
            user_obj.autoreply_fixed = 0
            bot.reply_to(message, "I will not randomly reply to your messages anymore.")
    else:
        user_obj.autoreply_chance = 0
        user_obj.autoreply_fixed = 0
        bot.reply_to(message, "I will not randomly reply to your messages anymore.")
    user_obj.save()


# Message fetching algorithm
def fetch_all_messages(user: TGUserModel, group: GroupSettings = None):
    if(group is None):
        logging.debug("Fetching {} messages from user {}".format(user.messages.count(), user.chat_id))
        return [message.message_text for message in user.messages]
    chat_messages = UserMessageModel.select().where(UserMessageModel.chat_id == group.chat_id)
    logging.debug("Fetching {} messages from chat {}".format(chat_messages.count(), group.chat_id))
    return [message.message_text for message in chat_messages]


def fetch_latest_messages(user: TGUserModel, group: GroupSettings = None):
    if(group is None):
        logging.debug("Fetching {} messages from user {}".format(user.messages.limit(100).count(), user.chat_id))
        return [message.message_text for message in user.messages.limit(100)]
    chat_messages = UserMessageModel.select().where(UserMessageModel.chat_id == group.chat_id).limit(100)
    logging.debug("Fetching {} messages from chat {}".format(chat_messages.count(), group.chat_id))
    return [message.message_text for message in chat_messages]


def fetch_all_included(user: TGUserModel, keyword: str, group: GroupSettings = None):
    if(group is None):
        selected_messages = UserMessageModel.select().where((UserMessageModel.user == user) & (UserMessageModel.message_text.contains(keyword)))
        logging.debug("Fetching {} messages from user {}".format(selected_messages.count(), user.chat_id))
        return [message.message_text for message in selected_messages]
    selected_messages = UserMessageModel.select().where((UserMessageModel.chat_id == group.chat_id) & UserMessageModel.message_text.contains(keyword))
    logging.debug("Fetching {} messages from chat {}".format(selected_messages.count(), group.chat_id))
    return [message.message_text for message in selected_messages]


def fetch_messages(user: TGUserModel, group: GroupSettings = None, keyword: str = None) -> List[str]:
    if(keyword):
        return fetch_all_included(user, keyword, group)
    if(user.markov_algorithm == "last_message"):
        return fetch_latest_messages(user, group)
    else:
        return fetch_all_messages(user, group)


# Tries to return a short dumb response, if it already exists, return none
def generate_markov(messages: List[str]) -> str:
    if(not messages):
        return None
    # More messages from db means more complex responses.
    if(len(messages) < 100):
        state_size = 1
    elif(500 > len(messages) >= 100):
        state_size = 2
    else:
        state_size = 3
    text_model = markovify.NewlineText(messages, state_size=state_size)
    result = text_model.make_short_sentence(1024)
    return result


def check_duplicated(message_text: str, user: TGUserModel, group: GroupSettings = None):
    chat_id = user.chat_id
    if(group):
        chat_id = group.chat_id
    response, created = GeneratedMessageModel.get_or_create(user=user, message_text=message_text, chat_id=chat_id)
    if(created):
        logging.debug("New message: %s" % response.message_text)
    return not created


def should_reply(user: TGUserModel, group: GroupSettings = None) -> bool:
    if(group and group.override_settings):
        if(group.user.random_autoreply and group.user.autoreply_chance is not 0):
            chances = random.randint(1, 100)
            logging.debug("random number: {} autoreply chance: {}".format(chances, group.user.autoreply_chance))
            return chances <= group.user.autoreply_chance
        else:
            counter = UserMessageModel.select().where(UserMessageModel.chat_id == group.chat_id).count()
            logging.debug("message counter: {} autoreply fixed: {}".format(counter, group.user.autoreply_fixed))
            return counter % group.user.autoreply_fixed is 0 if group.user.autoreply_fixed is not 0 else False
    else:
        if (user.random_autoreply and user.autoreply_chance is not 0):
            chances = random.randint(1, 100)
            logging.debug("random number: {} autoreply chance: {}".format(chances, user.autoreply_chance))
            return chances <= user.autoreply_chance
        else:
            counter = user.messages.count()
            logging.debug("message counter: {} autoreply fixed: {}".format(counter, user.autoreply_fixed))
            return counter % user.autoreply_fixed is 0 if user.autoreply_fixed is not 0 else False


@bot.message_handler(regexp='{}|{}'.format(bot_info.first_name, bot_info.username))
def reply_on_mention(message: Message):
    global Stop
    global Count
    global UwUMode
    global ImagePng
    global Vocal
    
    lcd.clear
    if random.randint(1, 100)<30:
         Vocal=True
    else:
         Vocal=False
    user_obj: TGUserModel = get_user_from_message(message)
    group: GroupSettings = get_group_from_message(message) if message.chat.type != 'private' else None
    if(group and group.override_settings):  # Use group's settings
        settings: TGUserModel = group.user
    else:
        group = None
        settings = user_obj
    generated_message = generate_markov(fetch_messages(settings, group))
    if (generated_message and not check_duplicated(generated_message, user_obj, group)):
            Stop=False
            Count=30
            bot.send_chat_action(message.chat.id,'typing')
            if UwUMode==True:
               generated_message=generated_message.replace("l", 'w')
               generated_message=generated_message.replace("r", 'w')
            generated_message=MsgPrepare(generated_message)
            if random.randint(1, 100)<10:
                generated_message=Meme(generated_message)
            width, height = lcd.dimensions()
            spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
            image = Image.new('1', (width, height),"black")
            image.paste(spritemap,(width-32,33))
            draw = ImageDraw.Draw(image)
            w, h = lcd.dimensions()
            font = ImageFont.truetype("/home/pi/PekaCoolBot-master/CCFONT.ttf", 12)
            lines = textwrap.wrap(generated_message, width=16)
            y_text = 0
            for line in lines:
                width, height = font.getsize(line)
                draw.text(((w- width)/4, y_text), line,1, font=font)
                y_text += height
            for x in range(128):
                for y in range(64):
                  pixel = image.getpixel((x, y))
                  lcd.set_pixel(x, y, pixel)
            backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            backlight.show()
            lcd.show()
            ImagePng=image
            if Vocal==False:
                LedOnOff()
                Stop=False
                bot.reply_to(message, generated_message)
            else:
                message.text=generated_message
                Stop=False
                audio(message)
            



@bot.message_handler(content_types=['sticker'])
def on_sticker(message: Message):
    if 'Peka' in str(message.sticker.set_name):
        #bot.delete_message(message.chat.id,message.message_id)
        path="/home/pi/PekaCoolBot-master/"+str(message.from_user.id)
        Hentai=str(int(message.sticker.mask_position.x_shift))
        with open(path+'/'+Hentai+'.stat') as f:
            page = f.readline()
        f.close()
        page=int(page)
        TotalTag=len(open(path+'/'+Hentai+'.stat').readlines(  ))-1
        keyboard = InlineKeyboardMarkup(3)
        keyboard.add(InlineKeyboardButton("N° "+str(Hentai), None, 'Hentai'),InlineKeyboardButton("Tags " + str(TotalTag), None, 'TotalTag'),InlineKeyboardButton("Pages "+ str(page), None, 'page'))
        bot.send_message(message.chat.id,"[Here's the sauce](https://nhentai.net/g/"+str(Hentai)+')',parse_mode="Markdown",reply_markup=keyboard)
        #bot.send_sticker(message.chat.id,open(path+"/"+str(Hentai)+".webp","rb"),reply_markup=keyboard)

@bot.message_handler(content_types=['text'], func=lambda m: m.reply_to_message and m.reply_to_message.from_user.id == bot_info.id)
def reply_on_reply(message: Message):
    reply_on_mention(message)  # I'm not lazy, i just realized that i was about to rewrite that function again but only for replies.

# Try to reply to every text message
@bot.message_handler(content_types=['text'])
def reply_intent(message: Message):
    global Vocal
    global ImagePng
    global Count
    global Stop
    
    if random.randint(1, 100)<30:
         Vocal=True
    else:
         Vocal=False
    lcd.clear
    user_obj: TGUserModel = get_user_from_message(message)
    group: GroupSettings = get_group_from_message(message) if message.chat.type != 'private' else None
    if (group and group.override_settings):  # Use group's settings
        settings: TGUserModel = group.user
    else:
        group = None
        settings = user_obj
    if(should_reply(settings, group)):
        generated_message = generate_markov(fetch_messages(settings, group))
        if (generated_message and not check_duplicated(generated_message, user_obj, group)):
            Stop=False
            Count=30
            bot.send_chat_action(message.chat.id,'typing')
            # Prepare the text
            msg = generated_message
            msg = MsgPrepare(msg)
            # We load the font and prepare the the screen
            width, height = lcd.dimensions()
            spritemap = Image.open("/home/pi/PekaCoolBot-master/Peka.png").convert("PA")
            image = Image.new('1', (width, height),"black")
            image.paste(spritemap,(width-32,33))
            draw = ImageDraw.Draw(image)
            w, h = lcd.dimensions()
            font = ImageFont.truetype("/home/pi/PekaCoolBot-master/CCFONT.ttf", 12)
            lines = textwrap.wrap(msg, width=16)
            y_text = 0
            for line in lines:
                width, height = font.getsize(line)
                draw.text(((w- width)/4, y_text), line,1, font=font)
                y_text += height
            for x in range(128):
                for y in range(64):
                  pixel = image.getpixel((x, y))
                  lcd.set_pixel(x, y, pixel)
            backlight.set_all(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            backlight.show()
            lcd.show()
            # Save the image for /png command
            ImagePng=image
            isnew=False
            path="/home/pi/PekaCoolBot-master/"+str(message.from_user.id)
            message.text=message.text.replace('/newcard','')
            message.text=message.text.replace('@PekaCoolBot','')
            message.text=message.text.replace(' ','')
            Random=True
            try:
                os.mkdir(path)
                isnew=True
                PekaPoints=7
                with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP", 'w+') as f:
                    f.write(str(PekaPoints))
                f.close()
            except OSError:
                print ("Creation of the directory %s failed" % path)
                with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP") as f:
                    PekaPoints =int(f.readline())
                f.close()
                PekaPoints+=2
                with open("/home/pi/PekaCoolBot-master/"+str(message.from_user.id)+'/'+"PekaPoints.PP", 'w+') as f:
                    f.write(str(PekaPoints))
                f.close()
                
            if Vocal==False:
                LedOnOff()
                Stop=False
                bot.reply_to(message, generated_message)
            else:
                message.text=generated_message
                Stop=False
                audio(message)
            


def get_user_from_callback(query: CallbackQuery) -> TGUserModel:
    try:
        db_user: TGUserModel = TGUserModel.get(chat_id=query.from_user.id)
    except DoesNotExist:
        db_user = TGUserModel.create(
            chat_id=query.from_user.id,
            first_name=query.from_user.first_name.lower(),
            username=query.from_user.username.lower() if query.from_user.username else None,
            language_code=query.from_user.language_code)
    return db_user

# INLINE BUTTONS
@bot.callback_query_handler(func=lambda q: q.data in ["0", "10", "20", "50", "90", "200", "2000"])
def set_autoreply_chance(query: CallbackQuery):
    db_user: TGUserModel = get_user_from_callback(query)
    if(db_user.random_autoreply):
        db_user.autoreply_chance = int(query.data)
        bot.answer_callback_query(query.id, "Random chances set to {}%".format(query.data))
    else:
        db_user.autoreply_fixed = int(query.data)
        bot.answer_callback_query(query.id, "Fixed chances set to {}%".format(query.data))
    db_user.save()

    bot.edit_message_text(
        get_statistics(db_user),
        query.from_user.id,
        query.message.message_id,
        reply_markup=generate_settings_keyboard(db_user))


@bot.callback_query_handler(func=lambda q: q.data == 'close')
def close_settings_keyboard(query: CallbackQuery):
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id, reply_markup=None)


@bot.callback_query_handler(func=lambda q: q.data == 'autoreply')
def toggle_autoreply_type(query: CallbackQuery):
    db_user: TGUserModel = get_user_from_callback(query)
    db_user.random_autoreply = not db_user.random_autoreply
    db_user.save()
    bot.edit_message_text(
        get_statistics(db_user),
        query.from_user.id,
        query.message.message_id,
        reply_markup=generate_settings_keyboard(db_user))


@bot.callback_query_handler(func=lambda q: q.data == 'algorithm')
def toggle_fetch_algorithm(query: CallbackQuery):
    db_user: TGUserModel = get_user_from_callback(query)
    logging.debug("user {} alg: {}".format(db_user.chat_id, db_user.markov_algorithm))
    db_user.markov_algorithm = "last_message" if db_user.markov_algorithm == "all_messages" else "all_messages"
    db_user.save()
    bot.edit_message_text(
        get_statistics(db_user),
        query.from_user.id,
        query.message.message_id,
        reply_markup=generate_settings_keyboard(db_user))

# GROUP INLINE BUTTONS FOR ADMINS
@bot.callback_query_handler(func=lambda q: q.data.startswith('group_') and q.data.split('_')[1] in ["0", "10", "20", "50", "90", "200", "2000"])
def set_autoreply_chance(query: CallbackQuery):
    user_obj: TGUserModel = get_user_from_callback(query)
    group: GroupSettings = get_group_from_message(query.message)
    chances = int(query.data.split('_')[1])
    if (user_obj in group.admins):
        if(group.user.random_autoreply):
            group.user.autoreply_chance = chances
            bot.answer_callback_query(query.id, "Random chances set to {}%".format(chances))
        else:
            group.user.autoreply_fixed = chances
            bot.answer_callback_query(query.id, "Fixed chances set to {}%".format(chances))
        group.user.save()
        bot.edit_message_text(
            get_group_statistics(group),
            query.message.chat.id,
            query.message.message_id,
            reply_markup=group_keyboard(group, user_obj))
    else:
        bot.answer_callback_query(query.id)


@bot.callback_query_handler(func=lambda q: q.data == "group_override")
def toggle_group_override(query: CallbackQuery):
    user_obj: TGUserModel = get_user_from_message(query.message)
    group: GroupSettings = get_group_from_message(query.message)
    if (user_obj in group.admins):
        group.override_settings = not group.override_settings
        group.save()
        bot.edit_message_text(
            get_group_statistics(group),
            query.message.chat.id,
            query.message.message_id,
            reply_markup=group_keyboard(group, user_obj))


@bot.callback_query_handler(func=lambda q: q.data == 'group_algorithm')
def toggle_group_fetch_algorithm(query: CallbackQuery):
    user_obj: TGUserModel = get_user_from_message(query.message)
    group: GroupSettings = get_group_from_message(query.message)
    if (user_obj in group.admins):
        group.user.markov_algorithm = "last_message" if group.user.markov_algorithm == "all_messages" else "all_messages"
        group.user.save()
        bot.edit_message_text(
            get_group_statistics(group),
            query.message.chat.id,
            query.message.message_id,
            reply_markup=group_keyboard(group, user_obj))


@bot.callback_query_handler(func=lambda q: q.data == "group_autoreply")
def toggle_group_autoreply_type(query: CallbackQuery):
    user_obj: TGUserModel = get_user_from_message(query.message)
    group: GroupSettings = get_group_from_message(query.message)
    if(user_obj in group.admins):
        group.user.random_autoreply = not group.user.random_autoreply
        group.user.save()
        bot.edit_message_text(
            get_group_statistics(group),
            query.message.chat.id,
            query.message.message_id,
            reply_markup=group_keyboard(group, user_obj))
    else:
        bot.answer_callback_query(query.id)


@bot.callback_query_handler(func=lambda q: q.data.startswith("personal_"))
def show_user_statistics(query: CallbackQuery):
    user_obj: TGUserModel = TGUserModel.get(TGUserModel.chat_id == query.data.split("_")[1])
    bot.edit_message_text(
        get_statistics(user_obj),
        query.message.chat.id,
        query.message.message_id,
        reply_markup=None)


def notify_exceptions(exception_instance: Exception):
    logging.warning('Exception at %s \n%s', asctime(), exception_instance)
    now = int(time())
    logging.debug('Trying to send exception message to owner.')
    while (1):
        error_text = 'Exception at %s:\n%s' % (
            asctime(),
            str(exception_instance) if len(str(exception_instance)) < 3600 else str(exception_instance)[:3600])
        try:
            offline_time = int(time()) - now
            bot.send_message(config('OWNER_ID'), error_text + '\nBot went offline for %s seconds' % offline_time)
            logging.debug('Message sent, returning to polling.')
            break
        except:
            sleep(3)


# This makes the bot unstoppable :^)
def safepolling():
    global rainbow
    global Stop
    global Count
    if(bot.skip_pending):
        last_update_id = bot.get_updates()[-1].update_id
    else:
        last_update_id = 0
    while(1):
        #bot.send_message(config('OWNER_ID'), str(Count)  + '\n SafePoll Count' )
        if Count>0:
            Count=Count-1
        else:
            if Stop==False:
                Time()
        if rainbow==True:
            Rainbow()
        logging.debug("Getting updates using update id %s", last_update_id)
        try:
            updates = bot.get_updates(last_update_id + 1, 50)
            logging.debug('Fetched %s updates', len(updates))
            if(len(updates) > 0):
                last_update_id = updates[-1].update_id
                bot.process_new_updates(updates)
        except ApiException as api_exception:
            logging.warning(api_exception)
        except Exception as exception_instance:
            if(debug_mode):
                notify_exceptions(exception_instance)

            
if(__name__ == '__main__'):
    # Setup the screen
    Volume=4
    LedOnOff()
    for x in range(6):
        backlight.set_pixel(x, 0, 0, 0)
        touch.on(x, handler)
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    lcd.show()
    backlight.show()
    pygame.mixer.music.set_volume(Volume/10)    
    # Tell owner the bot has started
    bot.remove_webhook()
    if(debug_mode):
        try:
            bot.send_message(config('OWNER_ID'), 'Bot Started')
        except ApiException:
            logging.critical('''Make sure you have started your bot https://telegram.me/%s.
                And configured the owner variable.''' % bot_info.username)
            exit(1)
    logging.info('Safepolling Start.')
    safepolling()
# Nothing beyond this line will be executed.

