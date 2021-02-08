import time
import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.cfg')

device_card_uid = config['UIDS']['device_card_uid']
learn_card_uid = config['UIDS']['learn_card_uid']
default_volume = int(config['DEVICE']['default_volume'])

#auth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope)
#sp = spotipy.Spotify(auth_manager=auth)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['AUTH']['client_id'],
                                               client_secret=config['AUTH']['client_secret'],
                                               redirect_uri=config['AUTH']['redirect_uri'],
                                               scope=config['AUTH']['scope'],
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

def current_device():   #returns two values, the id and name if there is a device currently playing
    data = sp.current_playback()
    if data != None:
        return data['device']['id'], data['device']['name']
    else:
        return -1, -1
    
def check_available(d_id):
    return d_id in [device['id'] for device in sp.devices()['devices']]

def get_shuffle_state():  #Needs a list of params
    playback = sp.current_playback()
    if playback != None:
        return playback['shuffle_state']
    else:
        raise Exception("shuffle_state returned invalid value")

def set_shuffle_state(state: bool):
    sp.shuffle(state=state)

def get_playpause_state():#dont know how :(
    return

def set_config_value(category: str, valname: str, value):
    config.set(category, valname, value)
    with open('config.cfg', 'w') as configfile:
        config.write(configfile)
        configfile.close()

def set_volume(value: int):
    sp.volume(device_id=config['DEVICE']['device_id'],volume_percent=value)


def play_context_URI(uri: str):
    current = current_device()
    
    if current == -1:#means no playback
        #Workaround for permission problems when old playback was on other device
        sp.transfer_playback(config['DEVICE']['device_id'], force_play=False)
        time.sleep(0.7)
        sp.pause_playback()
        set_volume(default_volume)
    elif current[0] != config['DEVICE']['device_id']:#means current playback on other device
        #Workaround for permission problems when other device is currently in playback
        sp.transfer_playback(config['DEVICE']['device_id'], force_play=False)
        time.sleep(2)
        sp.pause_playback()
        set_volume(default_volume)
        time.sleep(2)
        
    if check_available(config['DEVICE']['device_id']):#check if device is even online for playback
        sp.start_playback(device_id=config['DEVICE']['device_id'], context_uri=uri)
    else:
        return -1
        #This program is meant for always on spotify connect devices. Using not always online devices results in problems with playback
        #Migrate play URIs

def play_URIs(uris: list):
    sp.start_playback(device_id=config['DEVICE']['device_id'], uris=uris)


if __name__ == "__main__":
    sp.me()