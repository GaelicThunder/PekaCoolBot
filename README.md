# Peka Bot based on https://github.com/sanguchi/TriggerBot
# 
Python 2.7/3.5 Bot for Telegram. 

#### Setup:
Run `sudo pip install -r requirements.txt` on your terminal.    (OBSOLETE, NEED TO ADD NEW PACKAGES)

Then just run one of the following: 

##### Peka.py:
-This version does not store triggers, it stores messages and tries to generate sentences.

Code is super messy, i putted her on a Pimoroni GFX Hat and Raspberry Pi Zero.
Usually, a clock is displayed, but everytime a sentence is generated it get shown on her screen.


Added some custom command :

/8 
- Simple 8 Ball 

/msg yourmessagehere
- Send a message to be displayed directly on Peka's Screen

/temp
- debug for seeing her temperature

/uwu
- start the UwU mode globally (not the best thing, but since the project is for me and some friends is ok, will change it if asked or get used by more people)

/audio
- Text to Speech using Polly from Amazon Aws (can delete the sender message if is Admin of groups) 

/png
- get a screenshot of Peka's Screen

/stats
- get a various stats from the py

![Image of Peka](https://github.com/GaelicThunder/PekaCoolBot/blob/master/Images/IMG_20200817_044753.jpg)
![Image of Peka](https://github.com/GaelicThunder/PekaCoolBot/blob/master/Images/IMG_20200817_044826.jpg)
![Image of Peka](https://github.com/GaelicThunder/PekaCoolBot/blob/master/Images/IMG_20200817_153957.jpg)
