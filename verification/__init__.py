from essentials import tokening, TimeStamp
from hashlib import md5

class types(object):
    NONCE = "nonce"



def create_NONCE(password):
    challenge = {
        "challenge": {
            "nonce": tokening.CreateToken(40),
            "ts": str(TimeStamp())
        }            
    }

    challenge['verify'] = md5((str(challenge['challenge']['ts']) + ":" + password + ":" + challenge['challenge']['nonce']).encode()).hexdigest()

    return challenge

def solve_NONCE(challenge, password):
    return md5((challenge['ts'] + ":" + password + ":" + challenge['nonce']).encode()).hexdigest()