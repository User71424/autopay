import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random, re, threading, time, sys, json
# инициализация сессии #
vk_session = vk_api.VkApi(login='89817166139', password='Sr55321q', app_id=2685278)
vk_session.auth(token_only=True)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
##################################
# инициализация констант #
myId, mainChatId, sitisChatId, gildChatId, transferBotId = 246960404, 2000000064, 2000000070, 2000000072, -183040898
sleepMode = True
autoPostMessage = '.'
items = {}
msgToPay = None
##################################


def send_message(peer_id, message, forward_msg=None):
    forward = None
    if forward_msg is not None:
        forward_msg = vk.messages.getById(message_ids=forward_msg.message_id)["items"][0]
        forward = json.dumps({"peer_id": forward_msg['peer_id'], "conversation_message_ids":forward_msg['conversation_message_id'], "is_reply": True})
    vk.messages.send(peer_id=peer_id, message=message, forward=forward, random_id=random.randint(-100000000, 1000000000))


def autopost(peer_id, message):
    if sleepMode: return
    threading.Timer(1800, autopost, [peer_id, message]).start()
    send_message(peer_id, message)


def baf_request(baf_name, apo_num, peer_id):
    send_message(peer_id, 'апо ' + str(apo_num))
    send_message(peer_id, 'хочу баф ' + baf_name)


def reply_or_fwd(msg):
    i = vk.messages.getById(message_ids=msg.message_id)["items"][0]
    if i.get("reply_message"):
        return i["reply_message"]
    elif i.get("fwd_messages"):
        return i["fwd_messages"][0]
    else:
        return None


def get_id(text):
    num = 0
    for i in range(4, len(text)):
        if text[i] != '|':
            num = num * 10 + int(text[i])
        else:
            break
    return num


def check_item_and_pay(msg):
    item = msg.text[(msg.text.find(":") + 3):(len(msg.text) - msg.text[::-1].find("[") - 12)]
    mult = 1
    if item.find("*") != -1:
        mult = int(item[:item.find("*")])
        item = item[item.find("*") + 1:]
    if items.get(item) is None:
        return
    price, currency = items[item]
    payment = mult * price
    send_message(peer_id=msgToPay.peer_id, message='Передать ' + str(payment) + ' ' + currency, forward_msg=msgToPay)
    send_message(myId, 'Заплачено ' + str(payment) + ' ' + currency + ' за ' + str(mult) + ' ' + item)

for msg in longpoll.listen():
    if msg.type == VkEventType.MESSAGE_NEW:
        #Диалог с собой - настройка
        if msg.to_me is True and msg.from_user is True and msg.user_id == myId:
            if msg.text.lower() == 'пп':
                send_message(msg.peer_id, 'Жив')
            if msg.text.lower() == 'стартспам':
                sleepMode = False
                #АВТОПОСТ В ЧАТЫ
                autopost(mainChatId, autoPostMessage)
                autopost(sitisChatId, autoPostMessage)
            if msg.text.lower() == 'не спамим':
                sleepMode = True
            if msg.text.lower() == 'выкл':
                vk.messages.delete(message_ids=msg.message_id, peerId=msg.peer_id)
                sys.exit(0)
            if msg.text.split()[0].lower() == 'объявление':
                autoPostMessage = msg.text[10:]
                send_message(msg.peer_id, 'Текст обновлен')
            if msg.text.split()[0].lower() == 'предмет':
                try:
                    s = msg.text.split()
                    price = int(s[1])
                    currency = s[2]
                    item = ''
                    for i in range(3, len(s)):
                        item += ' ' + s[i]
                    item = item.replace(' ', '', 1)
                    if items.get(item) is None:
                        items[item] = price, currency
                        send_message(msg.peer_id, item + ' добавлен')
                    else:
                        items[item] = price, currency
                        send_message(msg.peer_id, item + ' обновлен')
                except:
                    send_message(msg.peer_id, 'Ошибка')
                    continue
            if msg.text.split()[0].lower() == 'удали':
                item = msg.text[6:]
                if items.get(item) is None:
                    send_message(msg.peer_id, item + ' не найдено')
                else:
                    items.pop(item)
                    send_message(msg.peer_id, item + ' удалено')
        #Взятие бафов#
        if msg.from_me is True and len(msg.text.split()) > 0 and msg.text.split()[0].lower() == 'баф':
            for i in range(4, len(msg.text)):
                if msg.text[i] == 'а':
                    baf_request('атаки', 5, msg.peer_id)
                if msg.text[i] == 'з':
                    baf_request('защиты', 7, msg.peer_id)
                if msg.text[i] == 'у':
                    baf_request('удачи', 2, msg.peer_id)
                if msg.text[i] == 'ч':
                    baf_request('человека', 3, msg.peer_id)
                if msg.text[i] == 'н':
                    baf_request('нежити', 7, msg.peer_id)
        #Взаимодействие с чатами для оплаты если бот не в спящем режиме#
        if sleepMode is not True and (msg.peer_id == mainChatId or msg.peer_id == sitisChatId):
            if reply_or_fwd(msg) is not None and reply_or_fwd(msg)['from_id'] == myId and msg.text.lower().find('передать') != -1:
                msgToPay = msg
            if vk.messages.getById(message_ids=msg.message_id)['items'][0]['from_id'] == transferBotId \
                            and msg.text.lower().find("получено") != -1 and get_id(msg.text) == myId:
                check_item_and_pay(msg)
