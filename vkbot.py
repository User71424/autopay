import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import  sys, json
from vk_api.utils import get_random_id
from threading import Thread
from time import sleep
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

def autopost():
    while True:
        if sleepMode is True:
            sleep(1)
            continue
        send_message(sitisChatId, autoPostMessage)
        send_message(mainChatId, autoPostMessage)
        sleep(1800)


def send_message(peer_id, message, forward_msg=None):
    try:
        if forward_msg is not None:
            forward_msg = vk.messages.getById(message_ids=forward_msg.message_id)["items"][0]
            forward = json.dumps(
                {"peer_id": forward_msg['peer_id'], "conversation_message_ids": forward_msg['conversation_message_id'],
                 "is_reply": True})
            vk.messages.send(peer_id=peer_id, message=message, forward=forward, random_id=get_random_id())
        else:
            vk.messages.send(peer_id=peer_id, message=message, random_id=get_random_id())
    except vk_api.exceptions.ApiError:
        print('Была ошибка при автопосте/автооплате')
        send_message(peer_id, message, forward_msg)


def baf_request(baf_name, apo_num, peer_id):
    send_message(peer_id, 'апо ' + str(apo_num))
    send_message(peer_id, 'хочу баф ' + baf_name)
    sleep(1.5)


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
    for i in range(0, len(text)):
        if text[i] != '|':
            num = num * 10 + int(text[i])
        else:
            break
    return num


def check_item_and_pay(msg):
    item = msg.text[(msg.text.find(":") + 3):(len(msg.text) - msg.text[::-1].find(":") - 1)]
    mult = 1
    print('tyt2')
    if item.find("*") != -1:
        mult = int(item[:item.find("*")])
        item = item[item.find("*") + 1:]
    if items.get(item) is None:
        return

    price, currency = items[item]
    payment = mult * price
    personId = get_id(msg.text[msg.text.find("[") + 3:])
    if msgToPay is not None and personId == msgToPay.user_id:
        send_message(peer_id=msgToPay.peer_id, message='Передать ' + str(payment) + ' ' + currency, forward_msg=msgToPay)
        send_message(myId, 'Заплачено ' + str(payment) + ' ' + currency + ' за ' + str(mult) + ' ' + item)


autoPostThread = Thread(target=autopost, daemon=True)
autoPostThread.start()

def main():
    global sleepMode, autoPostMessage, items, myId, sitisChatId, mainChatId, msgToPay
    try:
        for msg in longpoll.listen():
            if msg.type == VkEventType.MESSAGE_NEW:
                # Диалог с собой - настройка
                if msg.to_me is True and msg.from_user is True and msg.user_id == myId:
                    if msg.text.lower() == 'пп':
                        send_message(msg.peer_id, 'Жив')
                    if msg.text.lower() == 'стартспам':
                        sleepMode = False
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
                # Взаимодействие с чатами для оплаты если бот не в спящем режиме#
                if sleepMode is not True and (msg.peer_id == mainChatId or msg.peer_id == sitisChatId or msg.from_group):
                    if msg.text.lower().find('передать') != -1 and reply_or_fwd(msg) is not None \
                            and reply_or_fwd(msg)['from_id'] == myId:
                        msgToPay = msg
                    if msg.from_group \
                            and len(msg.text) > 8 \
                            and msg.text.lower()[:8] == "получено":
                        check_item_and_pay(msg)
    except TypeError:
        print('Была ошибка в лонгполе')
        main()
    except IndexError:
        print('Была ошибка в reply_or_forward из-за ["items"][0]')
        main()
    except:
        print('Другая ошибка')
        main()


main()