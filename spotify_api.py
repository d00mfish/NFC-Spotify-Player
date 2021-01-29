import time
import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.cfg')

device_card_uid = config['UIDS']['device_card_uid']
learn_card_uid = config['UIDS']['learn_card_uid']

device_id = config['AUTH']['device_id']
client_id = config['AUTH']['client_id']
client_secret = config['AUTH']['client_secret']
redirect_uri = config['AUTH']['redirect_uri']
scope = config['AUTH']['scope']

#auth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope)
#sp = spotipy.Spotify(auth_manager=auth)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope,
                                               ))


# returns the URI für the Album or Playlist, the current track is played from.
def current_playback():
    playback = sp.current_playback()
    if playback != None:
        try:
            return [playback['context']['uri'], playback['item']['name'], playback['item']['artists'][0]['name']]
        except TypeError:   #Personal playlists cant be learned that easy. WIP
            return -1
    else:
        return -1


def current_device():
    data = sp.current_playback()
    if data != None:
        return (data['device']['id'],data['device']['name'])
    else:
        return -1
    
def check_available(d_id):
    return d_id in [device['id'] for device in sp.devices()['devices']]

def set_config_value(category: str, valname: str, value):
    config.set(category, valname, value)
    with open('config.cfg', 'w') as configfile:
        config.write(configfile)
        configfile.close()
        

def shuffle_on():
    sp.shuffle(state=True, device_id=config['AUTH']['device_id'])


def pause():
    sp.pause_playback(device_id=config['AUTH']['device_id'])


def skip():
    sp.next_track(device_id=config['AUTH']['device_id'])


def play_context_URI(uri: str):
    current = current_device()
    if current == -1:
        sp.transfer_playback(config['AUTH']['device_id'], force_play=False)#Workaround for permission problems when old playback was on other device
        time.sleep(0.5)
        sp.pause_playback()
    elif current[0] != config['AUTH']['device_id']:
        sp.transfer_playback(config['AUTH']['device_id'], force_play=False)#Workaround for permission problems when other device is currently in playback
        time.sleep(0.3)
        sp.pause_playback()
        time.sleep(0.3)
    if check_available(config['AUTH']['device_id']):#check if device is even online for playback
        shuffle_on()
        sp.start_playback(device_id=config['AUTH']['device_id'], context_uri=uri)
        return 1
    else:
        return -1
        #This program is meant for always on spotify connect devices. Using not always online devices results in problems with playback
        #Migrate play URIs

def play_URIs(uris: list):
    shuffle_on()
    sp.start_playback(device_id=config['AUTH']['device_id'], uris=uris)


def look_for_URI(hexstring: str):
    with open("learned.csv", "r") as f:
        data = f.readlines()
        data = [x.strip() for x in data]
        data = [x.split(";") for x in data]
        uri = [x for x in data if hexstring in x]
        if uri == []:
            return -1
        else:
            return uri[0][1]


if __name__ == "__main__":
    sp.me()
