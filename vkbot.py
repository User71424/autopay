import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sys, json
from vk_api.utils import get_random_id
from threading import Thread
from time import sleep
from me_class import *


# инициализация сессии #
vkBot = Bot(token='a1619d5400b0b5b215bea7b7186700a143f6538a80c9929f958cfff338cbb134f7bb756717414ee495d64')


def autopost():
    while True:
        if sleepMode is True:
            sleep(1)
            continue
        try:
            for msg in longpoll.listen():
                vkBot.send(sitisChatId, autoPostMessage)
                vkBot.send(mainChatId, autoPostMessage)
                sleep(1800)
                break;
        except Exception as e:
            print(e)


def reply_or_fwd(msg):
    i = vkBot.getByMsgId(msg.message_id)
    if i.get('reply_message'):
        return i['reply_message']
    elif i.get('fwd_messages'):
        return i['fwd_messages'][0]
    else:
        return None


def get_id(text):
    num = 0
    for i in range(0, len(text)):
        if text[i] != '|':
            num = num * 10 + int(text[i])
        else:
            break
    return num


def check_item_and_pay(msg):
    text = msg.text.lower()
    item = text[(text.find(":") + 3):(len(text) - text[::-1].find(":") - 1)]
    mult = 1

    if item.find("*") != -1:
        mult = int(item[:item.find("*")])
        item = item[item.find("*") + 1:]
    if items.get(item) is None:
        return

    price, currency = items[item]
    payment = mult * price
    personId = get_id(text[text.find("[") + 3:])
    if msgToPay is not None and personId == msgToPay.user_id:
        id = msgToPay.message_id
        vkBot.send(msgToPay.peer_id, 'Передать ' + str(payment) + ' ' + currency, id)
        vkBot.send(myId, 'Заплачено ' + str(payment) + ' ' + currency + ' за ' + str(mult) + ' ' + item)

def formatItems():
    s = ""
    for item in items:
        price, currency = items[item]
        s += str(price) + " " + currency + " " + item + "\n"
    return s

def parseItemsFromTxt():
    file = open('items.txt')
    f = file.read()
    temp_items = {}
    for line in f.split('\n'):
        s = line.split()
        if len(s) < 3: continue
        item = ""
        for i in range(2, len(s)):
           item += ' ' + s[i]
        item = item.replace(' ', '', 1)
        temp_items[item] = int(s[0]), s[1]
    return temp_items


def updateTxt(filename, text):
    with open(filename, 'w') as f:
        f.write(text)

def checkLotList(msg):
    s = msg.text.lower().split('\n')
    for i in range(0, len(s)):
        if s[i].find('*') != -1:
            line = s[i]
            mult = int(line.split('*')[0])
            item = line[line.find('*') + 1:line.find('-') - 1]
            totalPrice = int(line[line.find('-'):].split(' ')[1])
            if items.get(item) is None:
                continue
            else:
                price, currency = items[item]
                if price >= totalPrice/mult:
                    vkBot.send(gameGroupId, 'купить лот ' + line[line.find('(') + 1 : line.find(')')])
                    vkBot.send(myId, 'Заплачено ' +  price * mult + ' за ' + item + '(аукцион)')

##################################
# инициализация констант #
myId, mainChatId, sitisChatId, gildChatId, transferBotId, gameGroupId, alinaId = 246960404, 2000000064, 2000000070, 2000000076, -183040898, -182985865, 135076938
sleepMode = True
autoPostMessage = open('autopost.txt').read()
items = parseItemsFromTxt()
msgToPay = None
##################################


autoPostThread = Thread(target=autopost, daemon=True)
autoPostThread.start()

def main():
    global sleepMode, autoPostMessage, items, myId, sitisChatId, mainChatId, msgToPay

    while True:
        try:
            for msg in vkBot.listen():
                if msg.from_chat or msg.from_user or msg.from_group:
                    msg_id = msg.message_id
                    data = vkBot.getByMsgId(msg_id)
                    conv_id = data['conversation_message_id']
                    text = msg.text.lower()
                    # Диалог с собой - настройка
                    if msg.to_me is True and msg.from_user is True and msg.user_id == myId:
                        if text == 'пп':
                            vkBot.send(msg.peer_id, 'Жив')
                        if text == 'стартспам':
                            sleepMode = False
                        if text == 'не спамим':
                            sleepMode = True
                        if text == 'выкл':
                            exit()
                        if text.split()[0] == 'объявление':
                            autoPostMessage = msg.text[10:]
                            updateTxt('autopost.txt', autoPostMessage)
                            vkBot.send(msg.peer_id, 'Текст обновлен')
                        if text.split()[0] == 'предмет':
                            try:
                                s = text.split()
                                price = int(s[1])
                                currency = s[2]
                                item = ''
                                for i in range(3, len(s)):
                                    item += ' ' + s[i]
                                item = item.replace(' ', '', 1)
                                if items.get(item) is None:
                                    items[item] = price, currency
                                    vkBot.send(msg.peer_id, item + ' добавлен')
                                else:
                                    items[item] = price, currency
                                    vkBot.send(msg.peer_id, item + ' обновлен')
                                updateTxt('items.txt', formatItems())
                            except:
                                vkBot.send(msg.peer_id, 'Ошибка')
                                continue
                        if text.split()[0] == 'удали':
                            item = text[6:]
                            if items.get(item) is None:
                                vkBot.send(msg.peer_id, item + ' не найдено')
                            else:
                                items.pop(item)
                                vkBot.send(msg.peer_id, item + ' удалено')
                                updateTxt('items.txt', formatItems())
                        if text == "скуп":
                            message = "В данный момент в скупе:\n"
                            for item in items:
                                message += item + " за " + str((items[item])[0]) + " " + (items[item])[1] + "\n"
                            vkBot.send(msg.peer_id, message)

                    # Взаимодействие с чатами для оплаты если бот не в спящем режиме#
                    if sleepMode is not True and (msg.peer_id == mainChatId or msg.peer_id == sitisChatId or msg.from_group):
                        if data['from_id'] == transferBotId and text.find('продает через аукцион') != -1:
                            checkLotList(msg)
                        if text.find('передать') != -1 and reply_or_fwd(msg) is not None \
                                and reply_or_fwd(msg)['from_id'] == myId:
                            msgToPay = msg
                        if msg.from_group \
                                and len(text) > 8 \
                                and text[:8] == 'получено':
                            check_item_and_pay(msg)
                        if data['from_id'] == gameGroupId and 'возрождается где-то' in text:
                            notifBot = Bot(token='015ef2eaf71756ecdb2c1e82a03f9ddfb275cd2d7a1eb1c0805e1b8aa031b6497ac3a83e98d31178f0b52')
                            notifBot.send(2000000077, '@online ' + msg.text)
        except TypeError:
            print('Была ошибка в лонгполе')
        except IndexError:
            print('Была ошибка в reply_or_forward')
        except Exception as e:
            print(e)



mainThread = Thread(target=main, daemon=True)
mainThread.start()
mainThread.join()
