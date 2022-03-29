import vkbot
import time
def get_id(text):
    num = 0
    for i in range(4, len(text)):
        if text[i] != '|':
            num = num * 10 + int(text[i])
        else:
            break
    return num

def baf_request(baf_name, apo_num, peer_id)
    vkbot.send_message(peer_id,'апо ' + apo_num)
    time.sleep(1.2)
    vkbot.send_message(peer_id, 'хочу баф ' + baf_name)
    time.sleep(1.2)