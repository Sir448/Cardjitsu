# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 02:06:45 2020

@author: Chris
"""

import discord
from discord.ext import commands
import asyncio
from random import randint
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

token = os.getenv("TOKEN")

bot = commands.Bot(command_prefix=";")

bot.remove_command('help')

cards = pd.read_excel("CardjitsuCards.xlsx",index_col=0)
collections = pd.read_excel("Collections.xlsx",index_col=0)
players = pd.read_excel("Players.xlsx",index_col=0)


fire = Image.open("Wins/Fire.png")
fire = fire.resize((int(fire.size[0]/11),int(fire.size[1]/11)), 0)
water = Image.open("Wins/Water.png")
water = water.resize((int(water.size[0]/14.5),int(water.size[1]/14.5)), 0)
snow = Image.open("Wins/Snow.png")
snow = snow.resize((int(snow.size[0]/11),int(snow.size[1]/11)), 0)
back = Image.open("Cards/Back.png")
back = back.resize((int(back.size[0]/8.4),int(back.size[1]/8.4)), 0)


starterDeck = []
starterCards = [0,5,8,13,16,19,21,22,25]
for i in range(len(cards)):
    if i in starterCards:
        starterDeck.append(1)
    else:
        starterDeck.append(0)

global player1, player2
challengeActive = False
duelActive = False
waitingForP1 = False
waitingForP2 = False
buying = False
showingResults = False
gui = True

def belt(colour):
    if colour == "white":
        return 0xFEFFFF
    elif colour == "yellow":
        return 0xFFF000
    elif colour == "orange":
        return 0xFF8700
    elif colour == "green":
        return 0x32CD32
    elif colour == "blue":
        return 0x000CFF
    elif colour == "red":
        return 0xFF0000
    elif colour == "purple":
        return 0x5A02DA
    elif colour == "brown":
        return 0x521D01
    elif colour == "black" or colour == "ninja":
        return 0x000000
    else:
        return 0xFF00F7
        

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    

@bot.command()
async def start(ctx):
    global players,collections
    player = str(ctx.message.author)
    if player not in collections.columns:
        collections.insert(len(collections.columns),player,starterDeck)
        powerCard = randint(1,3)
        if powerCard == 1:
            collections[player][72] = 1
        elif powerCard == 2:
            collections[player][88] = 1
        elif powerCard == 3:
            collections[player][80] = 1
        collections.to_excel("Collections.xlsx")
        players.insert(len(players.columns),player,["white",0,0,0,"gui"])
        players.to_excel("Players.xlsx")
        embed = discord.Embed(description="Sensei has presented you with your starter deck. Type `;collection` to see the cards in your collection.", color = belt(str(players[player][0])))
        await ctx.message.channel.send(embed=embed)
    else:
        embed = discord.Embed(description="You already have a starter deck.", color = belt(str(players[player][0])))
        await ctx.send(embed=embed)

"""
Belt
    White = 0
    Yellow = 1
    Orange = 2
    Green = 3
    Blue = 4
    Red = 5
    Purple = 6
    Brown = 7
    Black = 8
    Ninja = 9
Money
    Gained from talking or Battling
    Battling win = 100
    Talking
        1/30 chance of getting anything
        Number between 1 and 1 000 000
        Floor cube root of random number
    Card packs = 1000
        Dups = Number * 5
Wins
Losses
    Worth Quarter of a loss
"""

@bot.command()
async def collection(ctx):
    player = str(ctx.message.author)
    if player in collections.columns:
        embed = discord.Embed(title="Your Collection", color = belt(str(players[player][0])))
        for i in range(len(collections[player])):
            if collections[player][i] == 1:
                embed.add_field(name=cards.iloc[i,1], value="Element: "+cards.iloc[i,2]+"|Number: "+str(cards.iloc[i,4])+"|Colour: "+cards.iloc[i,3], inline=False)
        await ctx.send(embed=embed) 
    else: 
        embed = discord.Embed(description="You haven't started yet. Type `;start` to get your starter deck.", color = 0xFFFFFF)        
        await ctx.send(embed=embed)

@bot.command()
async def challenge(ctx, arg):
    global challengeActive, player1, player2, battleChannel
    player = str(ctx.message.author)
    if player in collections.columns:
        if challengeActive == False and player != str(bot.get_user(int(arg[3:-1]))):
            battleChannel = ctx
            challengeActive = True
            player1 = ctx.message.author
            player2 = bot.get_user(int(arg[3:-1]))
            await ctx.send(player2.name.title()+"! "+player1.name.title()+" is challenging you to a duel. Type `;accept` or `;deny` to accept or deny the challenge.")
        elif challengeActive == True: await ctx.send("There is already an active challenge.")
        else: await ctx.send("You can't challenge yourself")
    else: 
        embed = discord.Embed(description="You haven't started yet. Type `;start` to get your starter deck.", color = 0xFFFFFF) 
        await ctx.send(embed=embed)
        
@bot.command()
async def deny(ctx):
    global challengeActive, battleChannel
    player = str(ctx.message.author)
    if player in collections.columns:
        if challengeActive == True and ctx.message.author == player2:
            challengeActive = False
            await battleChannel.send("<@!"+str(player1.id)+">, "+player2.name.title()+" has denied your challenge.")
        elif challengeActive == False:
            await ctx.send("There is no active challenge.")
        else:
            await ctx.send("You were not challenged.")
    else: 
        embed = discord.Embed(description="You haven't started yet. Type `;start` to get your starter deck.", color = 0xFFFFFF) 
        await ctx.send(embed=embed)
        
async def sendCards():
    if players[str(player1)][4] == "gui":
        hand = Image.open("CardjitsuHand.png")
        draw = ImageDraw.Draw(hand)
        font = ImageFont.truetype("acmeexplosive", 45)
        draw.text((85,70), player1.name.upper(), (0,0,0), font=font)
        for i in range(5):
            xshift = 0
            yshift = 0
            if cards["Number"][player1Hand[i]] >= 9:
                xshift = 22
                yshift = 15
            card = Image.open("Cards/"+cards["File"][player1Hand[i]])
            card = card.resize((int(card.size[0]/11.2),int(card.size[1]/11.2)), 0)
            hand.paste(card,(85+i*225-xshift, 120-yshift),card)
        hand.save("P1Hand.png")
        await player1.send(file = discord.File("P1Hand.png"))
    else: 
        embed = discord.Embed(title="Your Hand", color = belt(str(players[str(player1)][0])))
        for i in player1Hand:    
            embed.add_field(name=cards.iloc[i,1], value="Element: "+cards.iloc[i,2]+"|Number: "+str(cards.iloc[i,4])+"|Colour: "+cards.iloc[i,3], inline=False)
        embed.set_footer(text = "`;play [card number 1-5]`")
        await player1.send(embed=embed)
        
    if players[str(player2)][4] == "gui":
        hand = Image.open("CardjitsuHand.png")
        draw = ImageDraw.Draw(hand)
        font = ImageFont.truetype("acmeexplosive", 45)
        draw.text((85,70), player2.name.upper(), (0,0,0), font=font)
        for i in range(5):
            xshift = 0
            yshift = 0
            if cards["Number"][player2Hand[i]] >= 9:
                xshift = 22
                yshift = 15
            card = Image.open("Cards/"+cards["File"][player2Hand[i]])
            card = card.resize((int(card.size[0]/11.2),int(card.size[1]/11.2)), 0)
            hand.paste(card,(85+i*225-xshift, 120-yshift),card)
        hand.save("P2Hand.png")
        await player2.send(file = discord.File("P2Hand.png"))
    else:
        embed = discord.Embed(title="Your Hand", color = belt(str(players[str(player2)][0])))
        for i in player2Hand:    
            embed.add_field(name=cards.iloc[i,1], value="Element: "+cards.iloc[i,2]+"|Number: "+str(cards.iloc[i,4])+"|Colour: "+cards.iloc[i,3], inline=False)
        embed.set_footer(text = "`;play [card number 1-5]`")
        await player2.send(embed=embed)
        
        
        
@bot.command()
async def accept(ctx):
    global challengeActive, player1Deck, player2Deck, player1Hand, player2Hand, waitingForP1, waitingForP2, P1Wins, P2Wins, duelActive, cardsPlayed, cardsPlayedMsg, roundsWon, roundsWonMsg, duel, battlefield, showingResults, battleGui
    player = str(ctx.message.author)
    if player in collections.columns:
        if challengeActive == True and ctx.message.author == player2:
            duelActive = True
            battleGui = gui
            await battleChannel.send("Starting the duel")
            P1Wins = {
                    "Fire":[],
                    "Water":[],
                    "Snow":[]
                }
            P2Wins = {
                    "Fire":[],
                    "Water":[],
                    "Snow":[]
                }
            player1Deck = []
            player2Deck = []
            for i in range(len(collections[str(player1)])):
                if collections[str(player1)][i] == 1:
                    player1Deck.append(i)
                if collections[str(player2)][i] == 1:
                    player2Deck.append(i)
            player1Hand = []
            player2Hand = []
            for i in range(5):
                card = randint(0,len(player1Deck)-1)
                player1Hand.append(player1Deck[card])
                player1Deck.pop(card)
                card = randint(0,len(player2Deck)-1)
                player2Hand.append(player2Deck[card])
                player2Deck.pop(card)
            waitingForP1 = True
            waitingForP2 = True
            showingResults = False
            
            if battleGui == True:
                dojo = Image.open("BlankDojo.png")
                rp = Image.open("RedPenguins/RP"+str(players[str(player1)][0]).title()+"Belt.png")
                dojo.paste(rp,(510,425),rp)
                bp = Image.open("BluePenguins/BP"+str(players[str(player2)][0]).title()+"Belt.png")
                dojo.paste(bp,(1240,425),bp)
                
                dojo.save("duelStart.png")
                duel = Image.open("duelStart.png")
                battlefield = await battleChannel.send(file = discord.File("duelStart.png"))
            else:
                cardsPlayed = discord.Embed(title="Cards", color = belt(str(players[str(player1)][0])))
                cardsPlayed.add_field(name = "__**"+player1.name +"\'s Card**__", value = "No Card Played", inline = True)
                cardsPlayed.add_field(name = "__**"+player2.name +"\'s Card**__", value = "No Card Played", inline = True)
                cardsPlayed.set_footer(text = "Waiting")
                cardsPlayedMsg = await battleChannel.send(embed=cardsPlayed)
                
                roundsWon = discord.Embed(title = "Rounds Won", color = belt(str(players[str(player1)][0])))
                roundsWon.add_field(name = "\u200b", value = player1.name, inline = False)    
                roundsWon.add_field(name = "**Fire**", value = "\u200b", inline = True)
                roundsWon.add_field(name = "**Water**", value = "\u200b", inline = True)
                roundsWon.add_field(name = "**Snow**", value = "\u200b", inline = True)        
                roundsWon.add_field(name = "\u200b", value = player2.name , inline = False)
                roundsWon.add_field(name = "**Fire**", value = "\u200b", inline = True)
                roundsWon.add_field(name = "**Water**", value = "\u200b", inline = True)
                roundsWon.add_field(name = "**Snow**", value = "\u200b", inline = True)
                roundsWonMsg = await battleChannel.send(embed=roundsWon)
            
            await sendCards()
        elif challengeActive == False:
            await ctx.send("There is no active challenge.")
        else:
            await ctx.send("You were not challenged.")
    else: 
        embed = discord.Embed(description="You haven't started yet. Type `;start` to get your starter deck.", color = 0xFFFFFF) 
        await ctx.send(embed=embed)

async def addWin(ctx,won,element):
    index = 1
    if element == "Water":
        index+=1
    elif element == "Snow":
        index+=2
    if won == 2:
        index += 4
    value = ""
    if won == 1:
        P1Wins[element].sort()
        for i in P1Wins[element]:
            value+= i +"\n"
    elif won == 2:
        P2Wins[element].sort()
        for i in P2Wins[element]:
            value+= i +"\n"
    roundsWon.set_field_at(index,name = "**"+element+"**", value = value, inline = True)
    await roundsWonMsg.edit(embed = roundsWon)
    
            
async def beltCheck(ctx,player):
    points = players[str(player)][2] + players[str(player)][3]/4
    if points >= 13 and points < 21 and players[str(player)][0] != "yellow":
        players[str(player)][0] = "yellow"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 21 and points < 30 and players[str(player)][0] != "orange":
        players[str(player)][0] = "orange"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 30 and points < 40 and players[str(player)][0] != "green":
        players[str(player)][0] = "green"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 40 and points < 52 and players[str(player)][0] != "blue":
        players[str(player)][0] = "blue"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 52 and points < 64 and players[str(player)][0] != "red":
        players[str(player)][0] = "red"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 64 and points < 76 and players[str(player)][0] != "purple":
        players[str(player)][0] = "purple"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 76 and points < 88 and players[str(player)][0] != "brown":
        players[str(player)][0] = "brown"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
    elif points >= 88 and (players[str(player)][0] != "black" or players[str(player)][0] != "ninja"):
        players[str(player)][0] = "black"
        embed = discord.Embed(description = "Congratulations! Much like the fearsome earthquake, you have rocked the house. \nWell done. You have earned a "+str(players[str(player)][0]).title()+" Belt for our efforts. I am proud of you.", color = belt(str(players[str(player)][0])))
        await battleChannel.send(embed=embed)
        players.to_excel("Players.xlsx")
        
        
        
async def checkWin(ctx,won):
    global winner, waitingForP1, waitingForP2, duelActive, challengeActive, loser, duel, battlefield, fire, water, snow, showingResults
    winner = None
    loser = None
    if won == 1:
        P1WinCheck = {
                "Fire":[],
                "Water":[],
                "Snow":[]
            }
        for i in P1Wins:
            for j in P1Wins[i]:
                if j not in P1WinCheck[i]:
                    P1WinCheck[i].append(j)
                if len(P1WinCheck[i]) >= 3:
                    winner = player1
                    loser = player2
        if len(P1WinCheck["Fire"]) > 0 and len(P1WinCheck["Water"]) > 0 and len(P1WinCheck["Snow"]) > 0:
            for i in P1WinCheck["Fire"]:
                for j in P1WinCheck["Water"]:
                    for k in P1WinCheck["Snow"]:
                        if i != j and j != k and k != i:
                            winner = player1
                            loser = player2
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
    elif won == 2:
        P2WinCheck = {
                "Fire":[],
                "Water":[],
                "Snow":[]
            }
        for i in P2Wins:
            for j in P2Wins[i]:
                if j not in P2WinCheck[i]:
                    P2WinCheck[i].append(j)
                if len(P2WinCheck[i]) >= 3:
                    winner = player2
                    loser = player1
        if len(P2WinCheck["Fire"]) > 0 and len(P2WinCheck["Water"]) > 0 and len(P2WinCheck["Snow"]) > 0:
            for i in P2WinCheck["Fire"]:
                for j in P2WinCheck["Water"]:
                    for k in P2WinCheck["Snow"]:
                        if i != j and j != k and k != i:
                            winner = player2
                            loser = player1
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
    if winner == None:
        waitingForP1 = True
        waitingForP2 = True
        await sendCards()
        if battleGui == True:
            await asyncio.sleep(2)
            duel = Image.open("duelStart.png")
            for i in P1Wins:
                for j in range(len(P1Wins[i])):
                    square = Image.open("Wins/"+P1Wins[i][j].lower()+"Card.png")
                    square = square.resize((int(square.size[0]/6),int(square.size[1]/6)), 0)
                    if i == "Fire":
                        shift = 0
                    elif i == "Water":
                        shift = 1
                    elif i == "Snow":
                        shift = 2
                    duel.paste(square,(130+shift*135,60+40*len(P1Wins[i])-j*40),square)
                    if i == "Fire":                    
                        duel.paste(fire,(163,85+40*len(P1Wins[i])-j*40),fire)
                    elif i == "Water":
                        duel.paste(water,(292,92+40*len(P1Wins[i])-j*40),water)
                    elif i == "Snow":
                        duel.paste(snow,(425,87+40*len(P1Wins[i])-j*40),snow)
            for i in P2Wins:
                for j in range(len(P2Wins[i])):
                    square = Image.open("Wins/"+P2Wins[i][j].lower()+"Card.png")
                    square = square.resize((int(square.size[0]/6),int(square.size[1]/6)), 0)
                    if i == "Fire":
                        shift = 0
                    elif i == "Water":
                        shift = 1
                    elif i == "Snow":
                        shift = 2
                    duel.paste(square,(1495+shift*135,60+40*len(P2Wins[i])-j*40),square)
                    if i == "Fire":                    
                        duel.paste(fire,(1528,85+40*len(P2Wins[i])-j*40),fire)
                    elif i == "Water":
                        duel.paste(water,(1657,92+40*len(P2Wins[i])-j*40),water)
                    elif i == "Snow":
                        duel.paste(snow,(1790,87+40*len(P2Wins[i])-j*40),snow)
            
            
            if waitingForP1 == False: 
                duel.paste(back,(583,376),back)
            if waitingForP2 == False: 
                duel.paste(back,(1147,376),back)
            
            duel.save("duel.png")
            await battlefield.delete()
            battlefield = await battleChannel.send(file = discord.File("duel.png"))
            showingResults = False
        else:
            await asyncio.sleep(3)
            cardsPlayed.set_field_at(0,name = "__**"+player1.name +"\'s Card**__", value = "No Card Played", inline = True)
            cardsPlayed.set_field_at(1,name = "__**"+player2.name +"\'s Card**__", value = "No Card Played", inline = True)
            cardsPlayed.set_footer(text = "Waiting")
            await cardsPlayedMsg.edit(embed=cardsPlayed)
        
    else:
        await battleChannel.send(winner.name.title()+" wins! You were awarded with 100 coins for winning.")
        players[str(winner)][1] += 100
        players[str(winner)][2] += 1
        players[str(loser)][3] += 1
        players.to_excel("Players.xlsx")
        
        if battleGui == False:
            roundsWon.set_footer(text = winner.name.title()+" wins!")
            await roundsWonMsg.edit(embed=roundsWon)
        else:
            for i in P1Wins:
                for j in range(len(P1Wins[i])):
                    square = Image.open("Wins/"+P1Wins[i][j].lower()+"Card.png")
                    square = square.resize((int(square.size[0]/6),int(square.size[1]/6)), 0)
                    if i == "Fire":
                        shift = 0
                    elif i == "Water":
                        shift = 1
                    elif i == "Snow":
                        shift = 2
                    duel.paste(square,(130+shift*135,60+40*len(P1Wins[i])-j*40),square)
                    if i == "Fire":                    
                        duel.paste(fire,(163,85+40*len(P1Wins[i])-j*40),fire)
                    elif i == "Water":
                        duel.paste(water,(292,92+40*len(P1Wins[i])-j*40),water)
                    elif i == "Snow":
                        duel.paste(snow,(425,87+40*len(P1Wins[i])-j*40),snow)
            for i in P2Wins:
                for j in range(len(P2Wins[i])):
                    square = Image.open("Wins/"+P2Wins[i][j].lower()+"Card.png")
                    square = square.resize((int(square.size[0]/6),int(square.size[1]/6)), 0)
                    if i == "Fire":
                        shift = 0
                    elif i == "Water":
                        shift = 1
                    elif i == "Snow":
                        shift = 2
                    duel.paste(square,(1495+shift*135,60+40*len(P2Wins[i])-j*40),square)
                    if i == "Fire":                    
                        duel.paste(fire,(1528,85+40*len(P2Wins[i])-j*40),fire)
                    elif i == "Water":
                        duel.paste(water,(1657,92+40*len(P2Wins[i])-j*40),water)
                    elif i == "Snow":
                        duel.paste(snow,(1790,87+40*len(P2Wins[i])-j*40),snow)
                        
                        
            duel.save("duel.png")
            await battlefield.delete()
            battlefield = await battleChannel.send(file = discord.File("duel.png"))
        
        await beltCheck(ctx,winner)
        await beltCheck(ctx,loser)
        duelActive = False
        challengeActive = False


@bot.command()
async def play(ctx,arg):
    global P1Card, P2Card, waitingForP1, waitingForP2, duel, fire, water, snow, back, battlefield, showingResults
    player = str(ctx.message.author)
    if player in collections.columns:
        await ctx.message.delete(delay = 1)
        if duelActive == True and ord(arg) >= 49 and ord(arg) <=53:
            if ctx.message.author == player1:
                if waitingForP1 == True:
                    waitingForP1 = False
                    P1Card = player1Hand[int(arg)-1]
                    card = randint(0,len(player1Deck)-1)
                    player1Hand.insert(int(arg),player1Deck[card])
                    player1Deck.pop(card)
                    player1Deck.append(P1Card)
                    player1Hand.pop(int(arg)-1)
                    
                    if battleGui == True:
                        if showingResults == False:
                            duel.paste(back,(583,376),back)
                            duel.save("duel.png")
                            await battlefield.delete()
                            battlefield = await battleChannel.send(file = discord.File("duel.png"))
                    else:
                        cardsPlayed.set_field_at(0,name = "__**"+player1.name +"\'s Card**__", value = "Card Hidden", inline = True)
                        await cardsPlayedMsg.edit(embed=cardsPlayed)
                    
                else:
                    msg = await ctx.send("You already played a card.")
                    await msg.delete(delay = 3)
            elif ctx.message.author == player2:
                if waitingForP2 == True:
                    waitingForP2 = False
                    P2Card = player2Hand[int(arg)-1]
                    card = randint(0,len(player2Deck)-1)
                    player2Hand.insert(int(arg),player2Deck[card])
                    player2Deck.pop(card)
                    player2Deck.append(P2Card)
                    player2Hand.pop(int(arg)-1)
                    
                    if battleGui == True:
                        if showingResults == False:
                            duel.paste(back,(1147,376),back)
                            duel.save("duel.png")
                            await battlefield.delete()
                            battlefield = await battleChannel.send(file = discord.File("duel.png"))
                    else:
                        cardsPlayed.set_field_at(1,name = "__**"+player2.name +"\'s Card**__", value = "Card Hidden", inline = True)
                        await cardsPlayedMsg.edit(embed=cardsPlayed)
                    
                else:
                    msg = await ctx.send("You already played a card.")
                    await msg.delete(delay = 3)
            else:
                await ctx.send("You are not participating in the duel")
            if waitingForP1 == False and waitingForP2 == False:
                
                if battleGui == True:
                    card = Image.open("Cards/"+cards["File"][P1Card])
                    card = card.resize((int(card.size[0]/8.4),int(card.size[1]/8.4)), 0)
                    if cards["Number"][P1Card] >= 9: duel.paste(card,(554,356),card)
                    else: duel.paste(card,(583,376),card)
                    card = Image.open("Cards/"+cards["File"][P2Card])
                    card = card.resize((int(card.size[0]/8.4),int(card.size[1]/8.4)), 0)
                    if cards["Number"][P2Card] >= 9: duel.paste(card,(1118,356),card)
                    else: duel.paste(card,(1147,376),card)
                    
                    duel.save("duel.png")
                    await battlefield.delete()
                    battlefield = await battleChannel.send(file = discord.File("duel.png"))
                    showingResults = True
                else:
                    cardsPlayed.set_field_at(0, name = "__**"+player1.name +"\'s Card**__", value = cards.iloc[P1Card,1]+"\n"+ cards.iloc[P1Card,2]+" | "+str(cards.iloc[P1Card,4])+" | "+cards.iloc[P1Card,3], inline = True)
                    cardsPlayed.set_field_at(1, name = "__**"+player2.name +"\'s Card**__", value = cards.iloc[P2Card,1]+"\n"+ cards.iloc[P2Card,2]+" | "+str(cards.iloc[P2Card,4])+" | "+cards.iloc[P2Card,3], inline = True)
                    await cardsPlayedMsg.edit(embed=cardsPlayed)
                
                if cards.iloc[P1Card,2] == "Fire" and cards.iloc[P2Card,2] == "Snow" or cards.iloc[P1Card,2] == "Water" and cards.iloc[P2Card,2] == "Fire" or cards.iloc[P1Card,2] == "Snow" and cards.iloc[P2Card,2] == "Water" or cards.iloc[P1Card,2] == cards.iloc[P2Card,2] and cards.iloc[P1Card,4] > cards.iloc[P2Card,4]:
                    P1Wins[cards.iloc[P1Card,2]].append(cards.iloc[P1Card,3])
                    if battleGui == False:
                        cardsPlayed.set_footer(text = player1.name +" Wins")
                        await addWin(ctx,1,cards.iloc[P1Card,2])
                    await checkWin(ctx,1)
                elif cards.iloc[P2Card,2] == "Fire" and cards.iloc[P1Card,2] == "Snow" or cards.iloc[P2Card,2] == "Water" and cards.iloc[P1Card,2] == "Fire" or cards.iloc[P2Card,2] == "Snow" and cards.iloc[P1Card,2] == "Water" or cards.iloc[P2Card,2] == cards.iloc[P1Card,2] and cards.iloc[P2Card,4] > cards.iloc[P1Card,4]:
                    P2Wins[cards.iloc[P2Card,2]].append(cards.iloc[P2Card,3])
                    if battleGui == False:
                        cardsPlayed.set_footer(text = player2.name +" Wins")
                        await addWin(ctx,2,cards.iloc[P2Card,2])
                    await checkWin(ctx,2)
                else:
                    if battleGui == False:
                        cardsPlayed.set_footer(text = "Draw")
                        await cardsPlayedMsg.edit(embed=cardsPlayed)
                    
                    waitingForP1 = True
                    waitingForP2 = True
                    await sendCards()
                    
                    if battleGui == True:
                        await asyncio.sleep(2)
                        
                        duel = Image.open("duelStart.png")
                        
                        for i in P1Wins:
                            for j in range(len(P1Wins[i])):
                                square = Image.open("Wins/"+P1Wins[i][j].lower()+"Card.png")
                                square = square.resize((int(square.size[0]/6),int(square.size[1]/6)), 0)
                                if i == "Fire":
                                    shift = 0
                                elif i == "Water":
                                    shift = 1
                                elif i == "Snow":
                                    shift = 2
                                duel.paste(square,(130+shift*135,60+40*len(P1Wins[i])-j*40),square)
                                if i == "Fire":                    
                                    duel.paste(fire,(163,85+40*len(P1Wins[i])-j*40),fire)
                                elif i == "Water":
                                    duel.paste(water,(292,92+40*len(P1Wins[i])-j*40),water)
                                elif i == "Snow":
                                    duel.paste(snow,(425,87+40*len(P1Wins[i])-j*40),snow)
                        for i in P2Wins:
                            for j in range(len(P2Wins[i])):
                                square = Image.open("Wins/"+P2Wins[i][j].lower()+"Card.png")
                                square = square.resize((int(square.size[0]/6),int(square.size[1]/6)), 0)
                                if i == "Fire":
                                    shift = 0
                                elif i == "Water":
                                    shift = 1
                                elif i == "Snow":
                                    shift = 2
                                duel.paste(square,(1495+shift*135,60+40*len(P2Wins[i])-j*40),square)
                                if i == "Fire":                    
                                    duel.paste(fire,(1528,85+40*len(P2Wins[i])-j*40),fire)
                                elif i == "Water":
                                    duel.paste(water,(1657,92+40*len(P2Wins[i])-j*40),water)
                                elif i == "Snow":
                                    duel.paste(snow,(1790,87+40*len(P2Wins[i])-j*40),snow)
                                    
                        if waitingForP1 == False: 
                            duel.paste(back,(583,376),back)
                        if waitingForP2 == False: 
                            duel.paste(back,(1147,376),back)
                        
                        duel.save("duel.png")
                        await battlefield.delete()
                        battlefield = await battleChannel.send(file = discord.File("duel.png"))
                        showingResults = False
                    else:
                        await asyncio.sleep(3)
                        cardsPlayed.set_field_at(0,name = "__**"+player1.name +"\'s Card**__", value = "No Card Played", inline = True)
                        cardsPlayed.set_field_at(1,name = "__**"+player2.name +"\'s Card**__", value = "No Card Played", inline = True)
                        cardsPlayed.set_footer(text = "Waiting")
                        await cardsPlayedMsg.edit(embed=cardsPlayed)
                    
        elif duelActive == False: await ctx.send("There is no active duel")
        else: await ctx.send("Please play a card number between 1 and 5")
    else: 
        embed = discord.Embed(description="You haven't started yet. Type `;start` to get your starter deck.", color = 0xFFFFFF) 
        await ctx.send(embed=embed)
    
@bot.command()
async def endGame(ctx):
    duelActive = False
    challengeActive = False
    waitingForP1 = False
    waitingForP2 = False
    
@bot.command()
async def stats(ctx):
    player = str(ctx.message.author)
    if player in collections.columns:
        embed = discord.Embed(title = ctx.message.author.name, description="Belt: "+str(players[player][0]).title()+"\nCoins: "+str(players[player][1])+"\nWins: "+str(players[player][2])+"\nLosses: "+str(players[player][3]), color = belt(str(players[player][0])))
        await ctx.send(embed=embed)

            

    
    
@bot.command()
async def buyCardPack(ctx):
    global buying
    player = str(ctx.message.author)
    if player in collections.columns and players[player][1] >= 1000 and buying == False:
        buying = True
        players[player][1] -= 1000
        embed = discord.Embed(title = "Card Pack", description="Purchased Card Pack", color = belt(str(players[player][0])))
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title = "Card Pack", description="Opening", color = belt(str(players[player][0])))
        await msg.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title = "Card Pack", description="Opening\n**.**", color = belt(str(players[player][0])))
        await msg.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title = "Card Pack", description="Opening\n**.  .**", color = belt(str(players[player][0])))
        await msg.edit(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title = "Card Pack", description="Opening\n**.  .  .**", color = belt(str(players[player][0])))
        await msg.edit(embed=embed)
        embed = discord.Embed(title = "Card Pack", color = belt(str(players[player][0])))   
        card1 = randint(0,cards["Weight"].sum()-1)
        for i in range(len(cards["Weight"])):
            card1 -= cards["Weight"][i]
            if card1 <= 0:
                card1 = i
                break
        card2 = randint(0,cards["Weight"].sum()-1)
        for i in range(len(cards["Weight"])):
            card2 -= cards["Weight"][i]
            if card2 <= 0:
                card2 = i
                break
        card3 = randint(0,cards["Weight"].sum()-1)
        for i in range(len(cards["Weight"])):
            card3 -= cards["Weight"][i]
            if card3 <= 0:
                card3 = i
                break
        embed.add_field(name="**"+cards.iloc[card1,1]+"**", value="Element: "+cards.iloc[card1,2]+"\nNumber: "+str(cards.iloc[card1,4])+"\nColour: "+cards.iloc[card1,3], inline=True)
        embed.add_field(name="**"+cards.iloc[card2,1]+"**", value="Element: "+cards.iloc[card2,2]+"\nNumber: "+str(cards.iloc[card2,4])+"\nColour: "+cards.iloc[card2,3], inline=True)
        embed.add_field(name="**"+cards.iloc[card3,1]+"**", value="Element: "+cards.iloc[card3,2]+"\nNumber: "+str(cards.iloc[card3,4])+"\nColour: "+cards.iloc[card3,3], inline=True)
        dupMoney = 0
        if collections[player][card1] == 1:
            dupMoney += cards.iloc[card1,4]*5
        else:
            collections[player][card1] = 1
        if collections[player][card2] == 1:
            dupMoney += cards.iloc[card2,4]*5
        else:
            collections[player][card2] = 1
        if collections[player][card2] == 1:
            dupMoney += cards.iloc[card3,4]*5
        else:
            collections[player][card3] = 1
        if dupMoney != 0:
            players[player][1] += dupMoney
            embed.set_footer(text = str(dupMoney)+" coins were given to you in compensation for duplicates")
        collections.to_excel("Collections.xlsx")
        players.to_excel("Players.xlsx")
        await asyncio.sleep(1)
        await msg.edit(embed=embed)
        buying = False
    elif players[player][1] < 1000:
        await ctx.send("You do not have enough coins to buy a card pack. A card pack costs 1000 coins.")
        
        
@bot.command()
async def mode(ctx, arg):
    global gui
    if arg.lower() == "gui":
        players[str(ctx.message.author)][4] = "gui"
        await ctx.send("You have switched to gui mode")
    elif arg.lower() == "text":
        players[str(ctx.message.author)][4] = "text"
        await ctx.send("You have switched to text mode")
    elif arg.lower() == "server":
        gui = not gui
        if gui == True:
            await ctx.send("Graphical user interface on")
        elif gui == False:
            await ctx.send("Graphical user interface off")

bot.remove_command('set')
@bot.command()
async def set(ctx,arg1,arg2,arg3):
    if str(ctx.message.author) == "Sir#4330":
        try:
            players[arg1][int(arg2)] = int(arg3)
        except:
            players[arg1][int(arg2)] = str(arg3)
        players.to_excel("Players.xlsx")
        
@bot.command()
async def backup(ctx):
    playersDatabase = pd.read_excel("Players.xlsx",index_col=0)
    playersDatabase.to_excel("PlayersBackup.xlsx")
    collectionDatabase = pd.read_excel("Collections.xlsx",index_col=0)
    collectionDatabase.to_excel("CollectionsBackup.xlsx")
    print("Backed up")
    
@bot.command()
async def revert(ctx):
    playersDatabase = pd.read_excel("PlayersBackup.xlsx",index_col=0)
    playersDatabase.to_excel("Players.xlsx")
    collectionDatabase = pd.read_excel("CollectionsBackup.xlsx",index_col=0)
    collectionDatabase.to_excel("Collections.xlsx")
    print("Reverted to last back up")
    
        
            
@bot.command()
async def give(ctx, arg1, arg2):
    if str(ctx.message.author) == "Sir#4330":
        try:
            players[arg1][1] += int(arg2)
        except:
            print("test")
        players.to_excel("Players.xlsx")
            

@bot.command()
async def test(ctx):
    await ctx.send("hi")


@bot.event
async def on_message(message):
    if message.author.bot == False and str(message.author) in players.columns:
        if randint(1,30) == 30:
            gain = int(randint(1,1000000)**(1/3))
            players[str(message.author)][1] += gain
            players.to_excel("Players.xlsx")
            await message.channel.send("You found "+str(gain)+" coins!")
    await bot.process_commands(message)

    
@bot.command()
async def clear(ctx):
    global collections,players
    if str(ctx.message.author) == "Sir#4330":
        collections = collections.iloc[0:0]
        for i in collections.columns:
            del collections[i]
        collections.to_excel("Collections.xlsx")
        players = players.iloc[0:0]
        for i in players.columns:
            del players[i]
        players.to_excel("Players.xlsx")
        print("Everyone's stats have been reset")
    
    
bot.run(token)

"""
instructions
change belt requirements
check if player is has started the game - stats
more stuff shop
gui for collection
seeing individual cards
"""