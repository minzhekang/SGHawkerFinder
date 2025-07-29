"""
© 2023 Kang Min Zhe <kangminzhe2@gmail.com>
@SGHawkerFinder_bot 
https://t.me/SGHawkerFinder_bot

2023 release

"""

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, AIORateLimiter
from telegram.error import (TelegramError, BadRequest, TimedOut, ChatMigrated, NetworkError)
import logging
import configparser
import pymysql
import pymysqlpool
from math import cos, asin, sqrt,radians,sin,cos, atan2
import re
import requests
from datetime import datetime
import time
from fuzzywuzzy import process

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                      level=logging.INFO)
# logger = logging.getLogger()

config = configparser.ConfigParser()
config.read('config.ini')

BOT_TOKEN = config.get('default','bot_token')
BOT_USERNAME = config.get('default', 'bot_username')
HOSTNAME = config.get('default','hostname')
USERNAME = config.get('default','username')
PASSWORD = config.get('default','password')
DATABASE = config.get('default','database')
TABLENAME = config.get('default','tablename')
TABLENAME_LOCATION = config.get('default','tablename_geolocation')
hawker_list = []
hawker_query = []

async def start_command(update= Update, context= ContextTypes.DEFAULT_TYPE):

    id = str(update.message.from_user.id)
    username = update.message.from_user.username
    conn = DBConnect()
    conn1 = conn.cursor(pymysql.cursors.DictCursor)
    with conn1 as cur:
        cur.execute()
    

    await update.message.reply_text("""😃 Hello! Welcome to SG Hawker Finder bot, created by someone with a passion for discovering and preserving our local hawker heritage. 🍚😋🍴\n\nUse this bot to easily find hawker stalls when you can't decide on what to eat, or discover it the old-fashioned way of walking around! 👀 The generation of hawker stall results is determined by a secret sauce algorithm that I have implemented in the backend 🥦.\n\nPlease note that the results are restricted to hawker stalls only and location sharing can only be done from a mobile phone.😁\n\nTo get started, you can use the following commands via the '☰ Menu' button:\n\n/start - Shows welcome message\n/findnearby - Discover top-rated hawker stalls nearest to you.\n/findonmap - Discover top-rated hawker stalls via address or map location.\n/search - Find via hawker centre name.\n/setresults - Sets the number of results to be returned.\n/feelinglucky - Discover a hawker stall in Singapore.\n/closure - Check which hawker centre is closed today.""", parse_mode= 'HTML')

async def unknown(update= Update, context= ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry I didn't understand that command. Use the '☰ Menu' list to see the list of commands available!", parse_mode= 'HTML')

async def feelinglucky_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    conn = DBConnect()
    conn1 = conn.cursor(pymysql.cursors.DictCursor)
    with conn1 as cur:
        cur.execute()
    result = cur.fetchone()
    
    hawker_name = result['hawker']
    hawker_name = hawker_name.replace("’", "'").replace("•", "")
    hawker_type = result['type']
    hawker_stars = result['stars']
    hawker_votes = result['votes']
    hawker_status = result['status']
    hawker_address = result['address']

    messagebody = f"""Here's a recommendation for you:\n\n<a href="https://www.google.com/search?q={hawker_name} {hawker_address}"><b>{hawker_name} 🍚</b></a>\nAddress: {hawker_address}\nRatings: {hawker_stars}⭐️({hawker_votes} reviews)"""

    await update.message.reply_text(messagebody, parse_mode= 'HTML')

async def getlocation_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    location_keyboard = KeyboardButton(text="📍 Share my location once", request_location=True)
    reply_markup = ReplyKeyboardMarkup([[ location_keyboard ]],  one_time_keyboard= True, resize_keyboard= True)
    await update.message.reply_text(text="""👋😊 Hey there! We will require you to share with us your current location before we proceed.\n\nClick on the (📍 Share my location once) button below to share.\n\nRemember to enable location from your device! 😊""", reply_markup=reply_markup)

async def setqueries_btn_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("5", callback_data=5),
            InlineKeyboardButton("10", callback_data=10),
            InlineKeyboardButton("15", callback_data=15),
            InlineKeyboardButton("30", callback_data=30),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    keyboard_random = [
        [
            InlineKeyboardButton("Yes", callback_data="Yes"),
            InlineKeyboardButton("No", callback_data="No"),
        ]
    ]
    reply_markup_random = InlineKeyboardMarkup(keyboard_random)

    id = str(update.message.from_user.id)
    username = update.message.from_user.username
    conn = DBConnect()
    conn1 = conn.cursor(pymysql.cursors.DictCursor)
    with conn1 as cur:
        cur.execute()
        cur.execute()
        
    result = cur.fetchone()

    if result['number_queries'] == None:
        number_queries = 5
    else:
        number_queries = result['number_queries']

    if result['randomise'] == None:
        randomise = "No"
    else:
        randomise = result['randomise']

    await update.message.reply_text(text=f"""Please select how many hawker stall result(s) to be returned! 😊\n\nYou are currently showing: {number_queries} hawker stall result(s)""", reply_markup=reply_markup)

    await update.message.reply_text(text=f"""Would you like to randomise the results? (If yes is chosen, hawker stalls will not be shown in order of ratings)\n\nYour current option is: {randomise} """, reply_markup=reply_markup_random)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # number_of_results = query.data
    # context.user_data[query.from_user.id] = int(number_of_results)
    conn = DBConnect()
    conn1 = conn.cursor(pymysql.cursors.DictCursor)
    if query.data.isnumeric():
        
        with conn1 as cur:
            cur.execute()
        await query.edit_message_text(text=f"You have chosen: {query.data} hawker stall result(s) to be displayed!")

    elif query.data == "No" or query.data == "Yes":

        with conn1 as cur:
            cur.execute()
        await query.edit_message_text(text=f"Randomise: {query.data} selected!")

    #address search function based on searchaddr_command
    else:
        await query.edit_message_text(f"""Please wait while we search for: <a href="https://www.google.com/search?q={query.data}"><b>{query.data}</b></a>! 🍚""" , parse_mode= 'HTML')
        id = query.from_user.id
        username = query.from_user.username
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
            cur.execute()
        result = cur.fetchone()
        if result['number_queries'] == None:
            number_of_results = 5
        else:
            number_of_results = result['number_queries']

        if result['randomise'] == None:
            randomise = "No"
        else:
            randomise = result['randomise']

        await update.effective_message.reply_text("Don't forget to use the /closure command to check if the hawker centre is open today~")
        messagebody = searchaddr(hawker_address=query.data, randomise=randomise, number_of_results=number_of_results)
        await update.effective_message.reply_text(messagebody, parse_mode= 'HTML')
        
    await query.answer()
    
async def setqueries_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    #print(context.user_data)
    if context.args == []:
        await update.message.reply_text(f"""Please key in a suffix! For e.g /search Old Airport Road""")
    else:
        number_of_results = context.args[0]
        if re.search('^[1-9]$|^0[1-9]$|^1[0-9]$|^20$', number_of_results):
            context.user_data[update.message.from_user.id] = int(number_of_results)
            await update.message.reply_text(f"Settings changed!")
        else:
            await update.message.reply_text(f"I only accept non-negative values that are not texts and lesser than 20!")
        
async def find_handler(update = Update, context= ContextTypes.DEFAULT_TYPE):
    id = str(update.message.from_user.id)
    username = update.message.from_user.username
    conn = DBConnect()
    conn1 = conn.cursor(pymysql.cursors.DictCursor)
    with conn1 as cur:
        cur.execute()
        cur.execute()

    result = cur.fetchone()
    
    if result['number_queries'] == None:
        number_of_results = 5
    else:
        number_of_results = result['number_queries']

    if result['randomise'] == None:
        randomise = "No"
    else:
        randomise = result['randomise']

    # #context.user_data is specific to the individual sending the message
    # number_of_results = context.user_data.get(update.message.from_user.id, None)
    # if number_of_results == None:
    #     number_of_results = 5

    await update.message.reply_text("Please wait while we search for the nearest hawker! 🍚\n\nDon't forget to use the /closure command to check if the hawker centre is open today~")

    gps = update.message.location
    lat = float(gps.latitude)
    long = float(gps.longitude)
    current_location = {'lat': lat, 'long': long}
    dict_hawker = closest(hawker_list, current_location)
    closest_hawker = dict_hawker['address']
    closest_distance = dict_hawker['min_dist']
    
    await update.message.reply_text(f"""We have found the nearest hawker to be <a href="https://www.google.com/search?q={closest_hawker}"><b>{closest_hawker}</b></a>! (~{closest_distance} away from selected location) 🍚""" , parse_mode= 'HTML')
    
    # with conn.cursor() as cur:
    #     cur.execute()
    #     results = cur.fetchall()

    if randomise == "Yes":
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
        results = cur.fetchall()
        
    else:
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
        results = cur.fetchall()
        
    if len(results) < 3:
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
        results = cur.fetchall()
    

    messagelist = []
    for result in results:
        # Kang's Delights 4.5(200)
        hawker_name = result['hawker']
        hawker_name = hawker_name.replace("’", "'").replace("•", "")
        hawker_type = result['type']
        hawker_stars = result['stars']
        hawker_votes = result['votes']
        hawker_status = result['status']
        hawker_address = result['address']
        message = f"""<a href="https://www.google.com/search?q={hawker_name} {hawker_address}"><b>{hawker_name}</b></a>, {hawker_stars}⭐({hawker_votes} reviews)"""
        messagelist.append(message)

    messagebody = ""
    for id, message in enumerate(messagelist):
        messagebody += f"""👉 {message}\n"""

    await update.message.reply_text(messagebody, parse_mode= 'HTML')

def getclosurelist():
    total = []
    #today = datetime.today().strftime('%d/%m/%Y')
    today = datetime.today().strftime('%d/%m/%Y')
    today = datetime.strptime(today,'%d/%m/%Y')
    
    with requests.Session() as s:
        r = s.get('https://data.gov.sg/api/action/datastore_search?resource_id=b80cb643-a732-480d-86b5-e03957bc82aa&limit=999')
        r = r.json()
        hawker_closure_list = r['result']['records']
        
    for result in hawker_closure_list:
        hawker_closure_total = []
        hawker_closure_total.append(result['name'])
        if result['q1_cleaningstartdate'] == "NA" or result['q1_cleaningstartdate'] == "TBC" or result['q1_cleaningstartdate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q1_cleaningstartdate'])
        if result['q1_cleaningenddate'] == "NA" or result['q1_cleaningenddate'] == "TBC" or result['q1_cleaningenddate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q1_cleaningenddate'])

        if result['q2_cleaningstartdate'] == "NA" or result['q2_cleaningstartdate'] == "TBC" or result['q2_cleaningstartdate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q2_cleaningstartdate'])
        if result['q2_cleaningenddate'] == "NA" or result['q2_cleaningenddate'] == "TBC" or result['q2_cleaningenddate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q2_cleaningenddate'])

        if result['q3_cleaningstartdate'] == "NA" or result['q3_cleaningstartdate'] == "TBC" or result['q3_cleaningstartdate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q3_cleaningstartdate'])
        if result['q3_cleaningenddate'] == "NA" or result['q3_cleaningenddate'] == "TBC" or result['q3_cleaningenddate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q3_cleaningenddate'])

        if result['q4_cleaningstartdate'] == "NA" or result['q4_cleaningstartdate'] == "TBC" or result['q4_cleaningstartdate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q4_cleaningstartdate'])
        if result['q4_cleaningenddate'] == "NA" or result['q4_cleaningenddate'] == "TBC" or result['q4_cleaningenddate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['q4_cleaningenddate'])

        if result['other_works_startdate'] == "NA" or result['other_works_startdate'] == "TBC" or result['other_works_startdate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['other_works_startdate'])
        if result['other_works_enddate'] == "NA" or result['other_works_enddate'] == "TBC" or result['other_works_enddate'] == "#N/A":
            hawker_closure_total.append("01/01/0001")
        else:
            hawker_closure_total.append(result['other_works_enddate'])
        total.append(hawker_closure_total)

    format_date = '%d/%m/%Y'
    closed_now_list_total = []
    for hawker in total:
        closed_now_list = []
        q1s = datetime.strptime(hawker[1], format_date)
        q1e = datetime.strptime(hawker[2], format_date)
        
        q2s = datetime.strptime(hawker[3], format_date)
        q2e = datetime.strptime(hawker[4], format_date)

        q3s = datetime.strptime(hawker[5], format_date)
        q3e = datetime.strptime(hawker[6], format_date)

        q4s = datetime.strptime(hawker[7], format_date)
        q4e = datetime.strptime(hawker[8], format_date)

        os = datetime.strptime(hawker[9], format_date)
        oe = datetime.strptime(hawker[10], format_date)

        if (q1s<today<=q1e):
            closed_now_list.append(hawker[0])
            closed_now_list.append(q1s)
            closed_now_list.append(q1e)
        elif (q2s<=today<=q2e):
            closed_now_list.append(hawker[0])
            closed_now_list.append(q2s)
            closed_now_list.append(q2e)
        elif (q3s<=today<=q3e):
            closed_now_list.append(hawker[0])
            closed_now_list.append(q3s)
            closed_now_list.append(q3e)
        elif (q4s<=today<=q4e):
            closed_now_list.append(hawker[0])
            closed_now_list.append(q4s)
            closed_now_list.append(q4e)
        elif (os<=today<=oe):
            closed_now_list.append(hawker[0])
            closed_now_list.append(os)
            closed_now_list.append(oe)

        if closed_now_list != []:
            closed_now_list_total.append(closed_now_list)
    
    return(closed_now_list_total)

async def getclosure_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    closure_list = getclosurelist()

    if closure_list == []:
        messagetext = f"""No Hawker Centre(s) closed today!"""
        await update.message.reply_text(messagetext, parse_mode= 'HTML')
    else:

        today = datetime.today().strftime('%d/%m/%Y')
        messagetext = f"Based on today's date: {today}\n\n"
        for hawker in closure_list:
            start = hawker[1].strftime('%d/%m/%Y')
            end = hawker[2].strftime('%d/%m/%Y')
            messagetext += f"""👉<b>{hawker[0]}</b> is closed from <u>{start}</u> to <u>{end}</u>\n\n"""
        await update.message.reply_text(messagetext, parse_mode= 'HTML')
    time.sleep(1)
    # await update.message.reply_animation('map.gif')
    #await update.message.reply_text(text="👋😊 Hey there! We will require you to share with us your current location before we proceed.\n\n 📍 Remember to enable location from your device!", reply_markup=reply_markup)

async def searchaddr_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    #print(context.user_data)
    if context.args == []:
        await update.message.reply_text(f"Please key in a suffix! For e.g: /search Old Airport Road")
    else:
        search_query = ""
        for word in context.args:
            if word == "hawker" or word == "Hawker" or word == "centre" or word == "center" or word == "Centre" or word == "Center" or word == "Market" or word == "market":
                pass
            else:
                search_query += f"{word} " 

        return_results = process.extract(search_query, hawker_query,  limit=3)
        
        result1= (return_results[0][0])[0:63]
        result2= (return_results[1][0])[0:63]
        result3= (return_results[2][0])[0:63]

        keyboard = [
            [InlineKeyboardButton(return_results[0][0], callback_data=result1)],
            [InlineKeyboardButton(return_results[1][0], callback_data=result2)],
            [InlineKeyboardButton(return_results[2][0], callback_data=result3)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text=f"""Please select a hawker centre from one of these address! 😅""", reply_markup=reply_markup)

def searchaddr(hawker_address = None, randomise = None, number_of_results = None):

    if randomise == "Yes":
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
        results = cur.fetchall()
        
    else:
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
        results = cur.fetchall()
        
    if len(results) < 3:
        conn = DBConnect()
        conn1 = conn.cursor(pymysql.cursors.DictCursor)
        with conn1 as cur:
            cur.execute()
        results = cur.fetchall()
    

    messagelist = []
    for result in results:
        # Kang's Delights 4.5(200)
        hawker_name = result['hawker']
        hawker_name = hawker_name.replace("’", "'").replace("•", "")
        hawker_type = result['type']
        hawker_stars = result['stars']
        hawker_votes = result['votes']
        hawker_status = result['status']
        hawker_address = result['address']
        message = f"""<a href="https://www.google.com/search?q={hawker_name} {hawker_address}"><b>{hawker_name}</b></a>, {hawker_stars}⭐({hawker_votes} reviews)"""
        messagelist.append(message)

    messagebody = ""
    for id, message in enumerate(messagelist):
        messagebody += f"""👉 {message}\n"""

    return messagebody


async def getlocationmap_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""To search via location, click on the attachments 🧷 > location 📍 > slide down to search via address 🔍 or move the pin to anywhere on the map 🗺!""")
    # await update.message.reply_animation('map.gif')
    #await update.message.reply_text(text="👋😊 Hey there! We will require you to share with us your current location before we proceed.\n\n 📍 Remember to enable location from your device!", reply_markup=reply_markup)

async def support_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thank you for your interest in supporting me! Server hosting is not free and development work takes time and effort. 😅 Any amount of support will be greatly appreciated by me! 😁😁\n\nDatabase of hawker stalls will be available for sale at $15 SGD (Please screenshot transaction proof along with your name and email me at sghawkerfinder@gmail.com with subject: Hawker Stalls Database Request) \n\nAt your service, \nMZ 👽")
    await update.message.reply_photo('payment_paynow.jpg')

async def contact_command(update= Update, context= ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Thank you for your enthusiasm in participating in the hawker culture of Singapore! 😁\n\nHowever, since I am currently holding a full-time job, bug fixes and adding new hawkers can only be done whenever I am free. 😔 Nevertheless, I will do my best to fulfill the requests!\n\nYou can contact me at: \n🍚<sghawkerfinder@gmail.com>🍚""")

def loadGeolocations():

    conn = DBConnect()
    conn1 = conn.cursor(pymysql.cursors.DictCursor)
    with conn1 as cur:
        cur.execute()
    result = cur.fetchall()
    
    for geolocation in result:
        hawker_dictionary = {}
        hawker_dictionary['address'] = geolocation['address'].strip()
        hawker_dictionary['lat'] = float(geolocation['latitude'].strip())
        hawker_dictionary['long'] = float(geolocation['longitude'].strip())
        hawker_list.append(hawker_dictionary)

    for location in result:
        hawker_query.append(location['address'].strip())

    return None

#Haversine formula
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))

def closest(data, v):
    list1 = []
    for p in data:
        list1.append(distance(v['lat'],v['long'],p['lat'],p['long']))
    min_dist = min(list1)
    if min_dist < 1:
        min_dist = min_dist*1000
        min_dist = str('%.3g' % min_dist)+'m'
    else:
        min_dist = str('%.3g' % min_dist)+'km'

    hawker_dict = min(data, key=lambda p:distance(v['lat'],v['long'],p['lat'],p['long']))
    hawker_dict['min_dist'] = min_dist
    return(hawker_dict)

async def error_handler(update= Update, context= ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Something went wrong with the server... Please try again later", parse_mode= 'HTML')
        # remove update.message.chat_id from conversation list
    except BadRequest:
        # handle malformed requests - read more below!
        # usually SQL returns null will be this too
        await update.message.reply_text("Something went wrong with the server... Please try again later", parse_mode= 'HTML')
    except TimedOut:
        # handle slow connection problems
        await update.message.reply_text("Something went wrong with the server... Please try again later", parse_mode= 'HTML')
    except NetworkError:
        # handle other connection problems
        await update.message.reply_text("Something went wrong with the server... Please try again later", parse_mode= 'HTML')
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        await update.message.reply_text("Something went wrong with the server... Please try again later", parse_mode= 'HTML')
    except TelegramError:
        # handle all other telegram related errors
        await update.message.reply_text("Something went wrong with the server... Please try again later", parse_mode= 'HTML')

# def closeMySQL():
#     conn.close()

# async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Raise an error to trigger the error handler."""
#     await context.bot.wrong_method_name()  # type: ignore[attr-defined]

def DBConnect():
    config={'host':HOSTNAME, 'user':USERNAME, 'password':PASSWORD, 'database':DATABASE, 'autocommit':True}
    pool = pymysqlpool.ConnectionPool(size=2, maxsize=3, pre_create_num=2, name='pool', **config)
    conn = pool.get_connection(pre_ping = True)
    
    return conn

if __name__ == '__main__':

    # # Connection to MySQL DB
    # conn = pymysql.connect(host = HOSTNAME, 
    #                     user=USERNAME, 
    #                     password=PASSWORD, 
    #                     db=DATABASE)
    # config={'host':HOSTNAME, 'user':USERNAME, 'password':PASSWORD, 'database':DATABASE, 'autocommit':True}
    # pool = pymysqlpool.ConnectionPool(size=2, maxsize=3, pre_create_num=2, name='pool', **config)
    # conn = pool.get_connection()

    # Loads geolocation data
    loadGeolocations()
    # Polling of bot
    app = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter(overall_max_rate=20)).build()
    
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('support', support_command))
    app.add_handler(CommandHandler('contact', contact_command))
    app.add_handler(CommandHandler('feelinglucky', feelinglucky_command))
    app.add_handler(CommandHandler('findnearby', getlocation_command))
    app.add_handler(CommandHandler('findonmap', getlocationmap_command))
    app.add_handler(CommandHandler('closure', getclosure_command))
    app.add_handler(CommandHandler('search', searchaddr_command))
    app.add_handler(CommandHandler('setresults', setqueries_btn_command))
    app.add_handler(CallbackQueryHandler(button))
    # Message Handlers
    app.add_handler(MessageHandler(filters.LOCATION, find_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    # Error Handlers
    #app.add_error_handler(error_handler)
    #app.add_handler(CommandHandler("bad_command", bad_command))

    print(f"{BOT_USERNAME} has started")
    # Checks messages every 3 seconds
    app.run_polling(poll_interval= 3)
    # Closes MySQL connection at the end
    # closeMySQL()

 