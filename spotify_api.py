import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.ini')

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
        return (playback['context']['uri'], playback['item']['name'], playback['item']['artists'][0]['name'])
    else:
        return -1


def current_device():
    playback = sp.current_playback()
    if playback != None:
        return (playback['device']['id'],playback['device']['name'])
    else:
        return -1

def set_config_value(cathegory: str, valname: str, value):
    config.set(cathegory, valname, value)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()
        

def shuffle_on():
    sp.shuffle(state=True, device_id=config['AUTH']['device_id'])


def pause():
    sp.pause_playback(device_id=config['AUTH']['device_id'])


def skip():
    sp.next_track(device_id=config['AUTH']['device_id'])


def play_context_URI(uri: str):
    shuffle_on()
    sp.start_playback(device_id=config['AUTH']['device_id'], context_uri=uri)


def play_URIs(uris: list):
    sp.start_playback(device_id=config['AUTH']['device_id'], uris=uris)


def look_for_URI(hexstring: str):
    with open("connections.csv", "r") as f:
        data = f.readlines()
        data = [x.strip() for x in data]
        data = [x.split(";") for x in data]
        uri = [x for x in data if hexstring in x]
        if uri == []:
            return -1
        else:
            return uri[0][1]


if __name__ == "__main__":
    import time
    #devices = sp.devices()
    # pp.pprint(devices)
    # shuffle_on()
    #sp.start_playback(device_id=device_id, context_uri='spotify:playlist:4ZkdemV8jqmSzdmXBV0dce')
    #uri = look_for_URI("4aa345aab4880")
    #print(uri,type(uri))
    #play_context_URI(uri)
    current_playback()
