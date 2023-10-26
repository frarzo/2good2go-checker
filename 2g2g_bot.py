from urllib import response
import schedule
import tgtg
import requests
import traceback
import time
from urllib.parse import quote
import json

store26id = "45818"
msgId = None

try:
    with open('/home/rasp/Desktop/toogoodtogo/config.json', mode='r+') as file:
        config = json.load(file)
except FileNotFoundError:
    print("---Config file not found!---")
    exit(1)
except:
    print("---Something went wrong at when opening the config file---")
    exit(1)

# Creazione client 2g2g
try:
    tgtgClient = tgtg.TgtgClient(access_token=config['2g2g']['access_token'], refresh_token=config['2g2g']
                                 ['refresh_token'], user_id=config['2g2g']['user_id'], cookie=config['2g2g']['cookie'])
except KeyError:
    try:
        email = input(
            'Inserisci la mail per ottenere le credenziali tgtg e dopo controlla la casella di posta')
        tgtgClient = tgtg.TgtgClient(email=email)
        credentials = tgtgClient.get_credentials()
        print(credentials)
        config['2g2g'] = credentials
        with open('config.json', mode='r+') as file:
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()
            tgtgClient = tgtg.TgtgClient(access_token=config['2g2g']['access_token'], refresh_token=config['2g2g']
                                         ['refresh_token'], user_id=config['2g2g']['user_id'], cookie=config['2g2g']['cookie'])
    except:
        print(traceback.format_exc())
        exit(1)
except:
    print("---Error at creating the tgtg client---")
    print(traceback.format_exc())
    exit(1)

# Creazione client telegram
try:
    token = config['tg']['bot_token']
    if token in ["", "BOTTTOKEN", None]:
        raise KeyError
except KeyError:
    print('---Cannot get telegram bot token, check config.json---')
    exit(1)
except:

    print(traceback.format_exc())
    exit(1)

try:
    chatID = config['tg']['chatID']
    if chatID in ["0", "", 0, None]:
        raise KeyError
except KeyError:
    print('---Cannot get telegram chat id, check config.json---')
    exit(1)
except:
    print(traceback.format_exc())
    exit(1)
print(chatID)

# Sends a text message to the user
def telegram_bot_sendtext(bot_message, only_to_admin=True):
    send_text = 'https://api.telegram.org/bot' + str(token) + '/sendMessage?chat_id=' + \
        str(chatID) + '&parse_mode=Markdown&text=' + quote(bot_message)
    response = requests.get(send_text)
    return response.json()

# Sends an image message to the user
def telegram_bot_sendimage(image_url, image_caption=None):
    keyboard=json.dumps({"inline_keyboard" : [[{"text": "📲Open in app","url" : "share.toogoodtogo.com"}]]})
    send_text = 'https://api.telegram.org/bot' + str(token) + '/sendPhoto?chat_id=' + str(chatID) + '&photo=' + image_url+'&reply_markup='+keyboard
    if image_caption != None:
        send_text += '&parse_mode=Markdown&caption=' + quote(image_caption)
    response = requests.get(send_text)
    return response.json()

# Deletes the message from the chat
def telegram_bot_deletelast(msgId):
    send_text = 'https://api.telegram.org/bot' + str(token) + '/deleteMessage?chat_id=' + str(chatID)+'&message_id='+str(msgId)
    response = requests.get(send_text)
    return response.json()

def button(stringa):

    send_text= 'https://api.telegram.org/bot' + str(token) + '/sendMessage?chat_id=' + str(chatID)+'&text='+str(stringa)
    response= requests.get(send_text)
    return response.json()


def autoSendUpdate():
    global msgId
    if msgId is not None:
        r = telegram_bot_deletelast(msgId)
    message = auto_checker()
    if message is None:
        return
    else:
        tg = telegram_bot_sendimage(
            'https://images.tgtg.ninja/item/cover/92760c5d-b42a-45be-a792-192601264165.jpg', message)
        try:
            msgId = tg['result']['message_id']
        except:
            print(traceback.format_exc())


def auto_checker():
    global store26id

    stuff = tgtgClient.get_item(item_id=store26id)

    if stuff['items_available'] == 0:
        return None
    else:
        start = stuff['pickup_interval']['start'].split('T')
        end = stuff['pickup_interval']['end'].split('T')
        return f"{stuff['items_available']} 📦 @ {stuff['display_name']}\n📆 {start[0]}  🕜{start[1][0:5]}-{end[1][0:5]}\n{float(stuff['item']['price_including_taxes']['minor_units']/100)}💲"


def refresh():
    try:
        autoSendUpdate()
    except:
        print(traceback.format_exc())


# Create a schedule to check every 15 min avaiability of stores
schedule.every(15).minutes.do(refresh)

telegram_bot_sendtext("Bot TooGoodToGo inizializzato 🤖\nQuesto bot comunica la disponibilità di MagicBox \ndel Pane Quotidiano @ Via Giulia 26.\n",True)
refresh()
while True:
    schedule.run_pending()
    updates=requests.get('https://api.telegram.org/bot' + str(token) + '/getUpdates')
    time.sleep(4)
