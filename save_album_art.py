import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser()
config.read('config.ini')

device_card_uid = config['UIDS']['device_card_uid']
learn_card_uid = config['UIDS']['learn_card_uid']

device_id = config['AUTH']['device_id']
client_id = config['AUTH']['client_id']
client_secret = config['AUTH']['client_secret']
redirect_uri = config['AUTH']['redirect_uri']
scope = config['AUTH']['scope']

#auth = SpotifyOAuth(client_id, client_secret, redirect_uri, scope)
sp = spotipy.Spotify()
#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='user-read-currently-playing',
                                               ))


# returns the URI für the Album or Playlist, the current track is played from.
def current_playback():
    playback = sp.current_playback()
    if playback != None:
        return (playback['context']['uri'], playback['item']['name'], playback['item']['artists'][0]['name'])
    else:
        return -1

def playlist_image(uri):
    return sp.playlist_cover_image(uri)


if __name__ == "__main__":
    print(type(playlist_image("spotify:album:2kcUXoH9BvKltkRR61eEsQ")))