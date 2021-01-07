# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 15:28:39 2020

@author: Chris
"""

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

shift = 1365

size = 6
size2 = 8.4
player = "Sir#4330"
cards = pd.read_excel("CardjitsuCards.xlsx")
redCard = Image.open("Wins/RedCard.png")
redCard = redCard.resize((int(redCard.size[0]/6),int(redCard.size[1]/6)), 0)
blueCard = Image.open("Wins/BlueCard.png")
blueCard = blueCard.resize((int(blueCard.size[0]/6),int(blueCard.size[1]/6)), 0)
orangeCard = Image.open("Wins/OrangeCard.png")
orangeCard = orangeCard.resize((int(orangeCard.size[0]/6),int(orangeCard.size[1]/6)), 0)
yellowCard = Image.open("Wins/YellowCard.png")
yellowCard = yellowCard.resize((int(yellowCard.size[0]/6),int(yellowCard.size[1]/6)), 0)
purpleCard = Image.open("Wins/PurpleCard.png")
purpleCard = purpleCard.resize((int(purpleCard.size[0]/6),int(purpleCard.size[1]/6)), 0)
greenCard = Image.open("Wins/GreenCard.png")
greenCard = greenCard.resize((int(greenCard.size[0]/6),int(greenCard.size[1]/6)), 0)
fire = Image.open("Wins/Fire.png")
fire = fire.resize((int(fire.size[0]/11),int(fire.size[1]/11)), 0)
water = Image.open("Wins/Water.png")
water = water.resize((int(water.size[0]/14.5),int(water.size[1]/14.5)), 0)
snow = Image.open("Wins/Snow.png")
snow = snow.resize((int(snow.size[0]/11),int(snow.size[1]/11)), 0)
back = Image.open("Cards/Back.png")
back = back.resize((int(back.size[0]/8.4),int(back.size[1]/8.4)), 0)

card = Image.open("Cards/PizzaChef.png")
card = card.resize((int(card.size[0]/size2),int(card.size[1]/size2)), 0)
rpbelt = "white"
bpbelt = "white"
height = 425
center = 875
split = 365

dojo = Image.open("BlankDojo.png")
rp = Image.open("RedPenguins/RP"+rpbelt.title()+"Belt.png")
dojo.paste(rp,(510,425),rp)
bp = Image.open("BluePenguins/BP"+bpbelt.title()+"Belt.png")
dojo.paste(bp,(1240,425),bp)
dojo.save("duelStart.png")
duel = Image.open("duelStart.png")


#card/back of card played
dojo.paste(back,(1147,376),back)
dojo.paste(card,(1147,376),card)
#dojo.paste(card,(583,376),card)

#powercard played
#dojo.paste(card,(1118,356),card)
#dojo.paste(card,(554,356),card)


#dojo.paste(redCard,(400,140),redCard) second win (each win +40 to y)
#dojo.paste(redCard,(400,100),redCard) #first win snow
#dojo.paste(fire,(433,125),fire) #+33, +25 fire icon
#dojo.paste(water,(427,132),water) #+27, +32 water icon
#dojo.paste(snow,(425,127),snow) #+25, +27 snow icon
#dojo.paste(redCard,(265,100),redCard) #first water win
#dojo.paste(redCard,(130,100),redCard) first fire win

#first wins for p2
#dojo.paste(redCard,(1765,100),redCard) 
#dojo.paste(redCard,(1630,100),redCard)
#dojo.paste(redCard,(1495,100),redCard)

"""
send blank on accept
send back on play
send front when both play
wait and reset with wins
"""
dojo.show()
"""
hand = Image.open("CardjitsuHand3.png")
#card = Image.open("Cards/"+cards["File"][71])
#card = card.resize((int(card.size[0]/11.2),int(card.size[1]/11.2)), 0)
#hand.paste(card,(963, 105),card)
for i in range(68,73):
    xshift = 0
    yshift = 0
    if cards["Number"][i] >= 9:
        xshift = 22
        yshift = 15
    card = Image.open("Cards/"+cards["File"][i])
    card = card.resize((int(card.size[0]/11.2),int(card.size[1]/11.2)), 0)
    hand.paste(card,(85+(i-68)*225-xshift, 120-yshift),card)
hand.show()
"""

#card.resize((int(card.size[0]/siz)))
"""
collections = pd.read_excel("Collections.xlsx")
starterDeck = []
starterCards = [0,5,8,13,16,19,21,22,25]
for i in range(len(cards)):
    if i in starterCards:
        starterDeck.append(1)
    else:
        starterDeck.append(0)


collections.insert(len(collections.columns),player,starterDeck)
print("Sir#4330" in collections.columns)
"""

"""
hand2 = Image.open("CardjitsuHand.png")
hand2.show()
"""
#print(cards["File"][0])