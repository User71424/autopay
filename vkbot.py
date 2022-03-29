import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import threading
vk_session = vk_api.VkApi(login='89817166139', password='Sr55321q', app_id=2685278)
vk_session.auth(token_only=True)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_message(peer_id, message):
    vk.messages.send(peer_id=peer_id, message=message, random_id=random.randint(-100000000, 1000000000))



def autopost(peer_id, message):
    threading.Timer(20, autopost, [peer_id, message]).start()
    send_message(peer_id, message)


autopost(135076938, 'автопост')

for event in longpoll.listen():
    if event.type==VkEventType.MESSAGE_NEW and event.text.lower()=='пп':
        send_message(event.peer_id, '123123')
