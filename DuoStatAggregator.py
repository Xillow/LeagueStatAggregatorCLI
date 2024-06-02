#DuoStatAggregator - Collects the Match History of a Specific Match and Transfers it to a Google Sheet
#Copyright (C) 2023 Matthew Brown

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.


#TODO: Convert to PYQT
#TODO: Create a Settings Dictionary
#TODO: Create Data Dragon Functions
#TODO: Create a String Variable that outputs what's being done by the program for logging and progress
#TODO: add in more options for player match info to payload
#TODO: add in Toggles for player match info.
#TODO: Add in Signals to QT UI use placeholder for Receiver Value or PyQTConfig



from __future__ import print_function

import os.path
from re import I

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, InvalidNotificationError

from datetime import datetime
from riotwatcher import LolWatcher, ApiError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



# The api key for riot
LOLWATCHER = LolWatcher(#APIKEY)


def main():
    spreadsheetURL = '' #spreadsheetURL in PYQT
    
    #add confirm button for options remakes the variables
    splitSSURL = spreadsheetURL.split('/')
    spreadsheetID = splitSSURL[5]
    #sheetName = "IBSG Match History"
    sheetName = "GP Match History"
    while True:
        creds = googleLogin()
        region = 'na1'
        matchIdRegion = 'NA1_'

        while True:
            matchName = 'Week 1: ' + input("Match Name: Week 1: ")
            blueTeam = input('Blue Team: ')
            redTeam = input('Red Team: ')
            matchId = matchIdRegion + input('Match Input: ')
            confirm = input('Ok? ')

            if confirm == 'y':
                   break
    
        
        serviceSheets = build('sheets', 'v4', credentials=creds)
        upload(serviceSheets, matchName, blueTeam, redTeam, region, matchId , spreadsheetID, sheetName)


    

    

#Load Button calls for this funtion
def matchRequest(region, matchId):
    try:
        requestURL = LOLWATCHER.match.by_id(region,matchId)
        return requestURL
    except ApiError as err:
        ddResponseCodeHandler(err)
    

def getDDVersion(region):
    try:
        version = LOLWATCHER.data_dragon.versions_for_region(region)
        return version['n']

    except  ApiError as err:
        ddResponseCodeHandler(err)
            
    
def getChampionName(version, championId):
    try:
        champions = LOLWATCHER.data_dragon.champions(version['champion'])
        champKeys = list(champions['data'].keys());
        
        for x in range(len(champKeys)):
            
            if(int(champions['data'][champKeys[x]]['key']) == championId ):
               return champions['data'][champKeys[x]]['name']
    except ApiError as err:
         ddResponseCodeHandler(err)
    

    return


def getItemNames(version, itemId):
    return

def ddResponseCodeHandler(err):
    msg = '' #add message to logging file

    match err.response.status_code:
        case 400:
            msg = 'Bad Request: Check your syntax\n\n'
        case 401:
            msg = 'Unauthorized: API Key may be missing\n\n'
            pass
        case 403:
            msg = 'Forbidden: There is an issue with the API Key\n\n'
            pass
        case 404:
            msg = 'Not Found: Given lookup does not exist\n\n'
            pass
        case 405:
            msg = 'Method not allowed\n\n'
            pass
        case 415:
            msg = 'Unsupported Media Types: body of request is in a unsupported format\n\n'
            pass
        case 429:
            msg = 'Rate Limit Exceeded: Exhausted maximum number of alloted\nAPI calls allowed for a given duration\n\n'
            pass
        case 500:
            msg = 'Internal Server Error: unexpected condition preventing the server from fulfilling \n\n'
            pass
        case 502:
            msg = 'Bad Gateway\n\n'
            pass
        case 503:
            msg = 'Service Unavailable: server is currently unavailable\n\n'
            pass
        case 504:
            msg = 'Gateway Timeout:\n\n'
            pass

    

    return


def googleLogin(creds = None):
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def firstEmptyCell(service, spreadsheet_id, sheetName):
    colA = sheetName + '!A:A'

    try:
        sheet = service.spreadsheets()
        cells = sheet.values().get(spreadsheetId=spreadsheet_id, range=colA).execute()
        rangeStart = len(cells['values']) + 1
        

    except HttpError as err:
        print(err)   #TODO: add err to logging file 


    return rangeStart


def payloadBuild(region, matchinfo, matchName, blueTeam, redTeam, sheetName, rangeStart):
    rangeMatchInfo = sheetName + '!A' + str(rangeStart)
    rangePlayerInfo = sheetName + '!A' + str(rangeStart+1)
    payload = {
        'value_input_option': 'USER_ENTERED',
        'data' : [
            {
              'range' : rangeMatchInfo,
              'values' : [[]]
            },
                        {
              'range' : rangePlayerInfo,

              'values' : [[],[],[],[],[],[],[],[],[],[]]
            }
            ]
        }

    version = getDDVersion(region)


    
    #Game Match Info
    ###########################################################################
    #Match Name
    payload['data'][0]['values'][0].append(matchName)
    #TODO: output appends data to a string

    #which team won
    if matchinfo['info']['teams'][0]['win'] == True:
        if matchinfo['info']['teams'][0]['teamId'] == 100:
            payload['data'][0]['values'][0].append('Blue')
        else:  
            payload['data'][0]['values'][0].append('Red')
          
    elif matchinfo['info']['teams'][1]['win'] == True:
        if matchinfo['info']['teams'][1]['teamId'] == 100:
            payload['data'][0]['values'][0].append('Blue')
        else:  
            payload['data'][0]['values'][0].append('Red')
           #TODO: output appends data to a string
    #Game Time
    gameDuration = int(matchinfo['info']['gameDuration'])

    gameTime = '0:' + str(gameDuration // 60) +  ':' + str(gameDuration % 60)
    #TODO: output appends data to a string

    payload['data'][0]['values'][0].append(gameTime)

    #VVVV if game time is wrong for a game before patch 11.20 this is why VVVV
    #VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
    #Prior to patch 11.20, this field returns the game length in milliseconds 
    #calculated from gameEndTimestamp - gameStartTimestamp. Post patch 11.20, 
    #this field returns the max timePlayed of any participant in the game 
    #in seconds,which makes the behavior of this field consistent with that 
    #of match-v4.The best way to handling the change in this field is to treat 
    #the value as milliseconds if the gameEndTimestamp field isn't in the response
    #and to treat the value as seconds if gameEndTimestamp is in the response.
  
    

    #Game Date 

    gameDateUnix = int(matchinfo['info']['gameCreation'])/1000
    
    gameDate = datetime.utcfromtimestamp(gameDateUnix).strftime('%m-%d-%Y')
    #TODO: output appends data to a string

    payload['data'][0]['values'][0].append(gameDate)

    #Game Version

    gameVersion = matchinfo['info']['gameVersion']
    #TODO: output appends data to a string

    payload['data'][0]['values'][0].append(gameVersion)


    #Game Player Info
    ###########################################################################
    for x in range(10):
        if True: #Player Name 
            playerName = matchinfo['info']['participants'][x]['summonerName']
            payload['data'][1]['values'][x].append(playerName)

        if True: #Team Name
            teamName = matchinfo['info']['participants'][x]['teamId']

            if teamName == 100:
                payload['data'][1]['values'][x].append(blueTeam)
            else:
                payload['data'][1]['values'][x].append(redTeam)

        if True: #(Transform)Champion
            transformChamp = ''

            transform = matchinfo['info']['participants'][x]['championTransform']
            
            champion = matchinfo['info']['participants'][x]['championId']

            match transform:
                case 0:
                    pass
                case 1:
                    transformChamp += 'Darkin ' 
                case 2:
                    transformChamp += 'Shadow Assassin ' 

            transformChamp += getChampionName(version, champion) 

            payload['data'][1]['values'][x].append(transformChamp)

        if True: #Position
            position = matchinfo['info']['participants'][x]['teamPosition']

            match position:
                case 'TOP':
                    payload['data'][1]['values'][x].append('Top')
                
                case 'JUNGLE':
                    payload['data'][1]['values'][x].append('Jungle')

                case 'MIDDLE':
                    payload['data'][1]['values'][x].append('Mid')
                
                case 'BOTTOM':
                    payload['data'][1]['values'][x].append('Bot')    

                case 'UTILITY':
                    payload['data'][1]['values'][x].append('Support')   

        if True: #First Blood
            firstBlood = matchinfo['info']['participants'][x]['firstBloodKill']
            payload['data'][1]['values'][x].append(firstBlood)

        if True: #Kills
            kills = matchinfo['info']['participants'][x]['kills']
            payload['data'][1]['values'][x].append(kills)


        if True: #Deaths
           deaths = matchinfo['info']['participants'][x]['deaths']
           payload['data'][1]['values'][x].append(deaths)


        if True: #Assists
            assists = matchinfo['info']['participants'][x]['assists']
            payload['data'][1]['values'][x].append(assists)


        if True: #Largest Multikill
            largestMKill= matchinfo['info']['participants'][x]['largestMultiKill']
            payload['data'][1]['values'][x].append(largestMKill)


        if True: #Total Damage to Champions
            totDamToChamp = matchinfo['info']['participants'][x]['totalDamageDealtToChampions']
            payload['data'][1]['values'][x].append(totDamToChamp)
        
        if True: #Obj Damage
            totDamToObj = matchinfo['info']['participants'][x]['damageDealtToObjectives']
            payload['data'][1]['values'][x].append(totDamToObj)
        
        if True: #Vision Score
            visionScore = matchinfo['info']['participants'][x]['visionScore']
            payload['data'][1]['values'][x].append(visionScore)

        if True: #Wards Placed
            wardsPlaced = matchinfo['info']['participants'][x]['wardsPlaced']
            payload['data'][1]['values'][x].append(wardsPlaced)

        if True: #Wards Killed
            wardskilled = matchinfo['info']['participants'][x]['wardsKilled']
            payload['data'][1]['values'][x].append(wardskilled)

        if True: #Control Wards Purchased
            visionWardsBought = matchinfo['info']['participants'][x]['visionWardsBoughtInGame']
            payload['data'][1]['values'][x].append(visionWardsBought)

        if True: #Gold Earned
            goldEarned = matchinfo['info']['participants'][x]['goldEarned']
            payload['data'][1]['values'][x].append(goldEarned)

        if True: #Minions Killed
            totalMinionsKilled = matchinfo['info']['participants'][x]['totalMinionsKilled']
            payload['data'][1]['values'][x].append(totalMinionsKilled)

        if True: #Neutral Minions Killed
            neutralMinionsKilled = matchinfo['info']['participants'][x]['neutralMinionsKilled']
            payload['data'][1]['values'][x].append(neutralMinionsKilled)

        if True: #First Tower
            firstTowerKill = matchinfo['info']['participants'][x]['firstTowerKill']
            payload['data'][1]['values'][x].append(firstTowerKill)

        if True: #Turret Kills
            turretKills = matchinfo['info']['participants'][x]['turretKills']
            payload['data'][1]['values'][x].append(turretKills)

        if True: #Baron Kills
            baronKills = matchinfo['info']['participants'][x]['baronKills']
            payload['data'][1]['values'][x].append(baronKills)

        if True: #Dragon Kills
            dragonKills = matchinfo['info']['participants'][x]['dragonKills']
            payload['data'][1]['values'][x].append(dragonKills)


        if True: #Rift Herald Kills for now only being outputted to first player of team 
            riftKills = ''
            if x == 0:
                riftKills += str(matchinfo['info']['teams'][0]['objectives']['riftHerald']['kills'])
            elif x == 5:
                riftKills += str(matchinfo['info']['teams'][1]['objectives']['riftHerald']['kills'])
            else:
                riftKills += '0'
            payload['data'][1]['values'][x].append(riftKills)

        if True: #Ban Info
            banInfo = ''
            if x < 5:
                try:
                    banInfo += getChampionName(version, matchinfo['info']['teams'][0]['bans'][x]['championId'])
                except:
                    pass
            else:
                try:
                    banInfo += getChampionName(version, matchinfo['info']['teams'][1]['bans'][x-5]['championId'])
                except:
                    pass

            payload['data'][1]['values'][x].append(banInfo)


        if True: #side won
            if x <5:
                sideWon = matchinfo['info']['teams'][0]['win']
            else:
                sideWon = matchinfo['info']['teams'][1]['win']

            payload['data'][1]['values'][x].append(sideWon)

        if True: #Game Time for spreadsheet functions
            payload['data'][1]['values'][x].append(gameTime)
       
        if True: #Side
            teamId = matchinfo['info']['participants'][x]['teamId']
            payload['data'][1]['values'][x].append(teamId)

        if True: #Player ID: Allows for player info to be split by team

            if teamName == 100:
                playerId = blueTeam + '!'
            else:
                playerId = redTeam + '!'

            playerId += matchinfo['info']['participants'][x]['puuid']
            payload['data'][1]['values'][x].append(playerId)

        if True: #match name

            payload['data'][1]['values'][x].append(matchName)




    return payload





def upload(service, matchName, blueTeam, redTeam, region, matchId, spreadsheet_id, sheetName):
    try:

        matchinfo = matchRequest(region, matchId)
        rangeStart = firstEmptyCell(service, spreadsheet_id, sheetName)
        batch_update_values_request_body = payloadBuild(region, matchinfo, matchName, blueTeam, redTeam, sheetName, rangeStart)


        request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_values_request_body)
        request.execute()


    except HttpError as err:
        print(err) #TODO: add err to logging file


if __name__ == '__main__':
    main()
    #append info gathered to a string and save it to a txt file this will be used for user facing info in desktop program.
