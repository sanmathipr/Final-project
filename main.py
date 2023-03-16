import json
import math
import sys

import requests
import base64
from urllib.parse import urlencode


# client credentials
client_id = '5b0440bdbf3540d986edb59e71954553'
client_secret = '8acc737f528f486d8f130508ebe5c002'
redirect_uri = 'http://localhost:8888/callback'
scope = 'user-top-read'
scopePlaylist = 'playlist-modify-public playlist-modify-private'
scopePlaylistTracks = 'playlist-modify-public playlist-modify-private'
client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())

# authorization URL
oauth_url = 'https://accounts.spotify.com/authorize'
oauth_params = urlencode({
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scope,
    'client_id': client_id
})
oauth_paramsPlaylist = urlencode({
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scopePlaylist,
    'client_id': client_id
})
oauth_paramsPlaylistTracks = urlencode({
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scopePlaylistTracks,
    'client_id': client_id
})

auth_url = f"{oauth_url}?{oauth_params}"
print("Click on the following URL. Follow through Spotify's authentication steps, and when you are led to a blank screen, copy the authentication code from the URL. It will be whatever comes after 'code ='")
print(auth_url)


code = input("Enter the code parameter from the redirected URL: ")
token_url = 'https://accounts.spotify.com/api/token'
token_data = {
   'grant_type': 'authorization_code',
   'code': code,
    'redirect_uri': redirect_uri
}

token_headers = {
    'Authorization': f"Basic {client_creds_b64.decode()}"
}
token_response = requests.post(token_url, data=token_data, headers=token_headers)
access_token = token_response.json()['access_token']


def getUserTopArtists (access_token): #returns a list of a users top ten artists
    search_url = 'https://api.spotify.com/v1/me/top/artists?'
    searchForToken = {'Authorization': f'Bearer {access_token}'}
    searchParameter = {'time_range': 'medium_term', 'limit': 10, 'offset':0}
    searchResponse = requests.get(search_url, params=searchParameter, headers = searchForToken)
    #print(searchResponse)
    artistDictionary = searchResponse.json()
    count = 0
    top_ten_artists = []
    for aristInfo in artistDictionary['items']: #going through info about each artist
        top_ten_artists.append((artistDictionary['items'][count]["name"]))
        count = count + 1

    return top_ten_artists


def getTopTracksByArtists(access_token, top_artists):
    track_list = []
    for artist in top_artists:
        search_url = 'https://api.spotify.com/v1/search'
        search_params = {'q': f'artist:{artist}', 'type': 'track', 'limit': 10}
        search_headers = {'Authorization': f'Bearer {access_token}'}
        search_response = requests.get(search_url, params=search_params, headers=search_headers)
        if search_response.status_code == 200:
            search_results = search_response.json()['tracks']['items']
            for track in search_results:
                track_list.append(track['uri'].split(':')[-1])
    return track_list


#user input for playlist parameters
print()
print()
while True:
    danceability = input("Enter the desired danceability for your playlist. Danceability describes "
                     "how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm "
                     "stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.")
    try:
        danceability = float(danceability)
        if 0.0 <= danceability <= 1.0:
            break
        else:
            print("Please enter a number between 0.0 and 1.0.")
    except ValueError:
        print("Please enter a valid number.")
        print()
print()

while True:
    valence = input("Enter the desired valence for your playlist. Valence is a measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. "
                "Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), "
                "while tracks with low valence sound more negative (e.g. sad, depressed, angry).")
    try:
        valence = float(valence)
        if 0.0 <= valence <= 1.0:
            break
        else:
            print("Please enter a number between 0.0 and 1.0.")
    except ValueError:
        print("Please enter a valid number.")
        print()
print()

while True:
    energy = input("Enter the desired energy for your playlist. Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. "
               "Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale."
               " Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.")
    try:
        energy = float(energy)
        if 0.0 <= energy <= 1.0:
            break
        else:
            print("Please enter a number between 0.0 and 1.0.")
    except ValueError:
        print("Please enter a valid number.")
        print()
print()



def getAudioFeatures(access_token, track_ids):
    audio_features_url = 'https://api.spotify.com/v1/audio-features'
    audio_features_params = {'ids': ','.join(track_ids)}
    audio_features_headers = {'Authorization': f'Bearer {access_token}'}
    audio_features_response = requests.get(audio_features_url, params=audio_features_params, headers=audio_features_headers)
    if audio_features_response.status_code == 200:
        audio_features_results = audio_features_response.json()['audio_features']
        return audio_features_results
    return None


def filterTracksByAudioFeatures(tracks, danceability, valence, energy):
    filtered_tracks = []
    for track in tracks:
        if math.isclose(track['danceability'], danceability, rel_tol=0.3) and \
           math.isclose(track['valence'], valence, rel_tol=0.3) and \
           math.isclose(track['energy'], energy, rel_tol=0.3):
            filtered_tracks.append(track['uri'])
    if len(filtered_tracks) > 15:
        return filtered_tracks
    else:
        playlistWanted = input("Your specified parameters only qualify " + str(len(filtered_tracks))  + " songs. Would you still like to make a playlist? Input 'Y' for yes and 'N' for no.")
        if playlistWanted == "Y":
            return filtered_tracks
        else:
            sys.exit()
            return

def create_playlist(user_id, playlist_name, description):
    # Create empty playlist
    auth_urlPlaylist = f"{oauth_url}?{oauth_paramsPlaylist}"
    print()
    print()
    print("Click on the URL and provide the access code to allow Spotify to create a playlist.")
    print(auth_urlPlaylist)
    code = input("Enter the code parameter from the redirected URL: ")


    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    access_token = token_response.json()['access_token']
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "name": playlist_name,
        "description": description,
        "public": False
    }
    create_playlist_response = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, data=json.dumps(data))

    if create_playlist_response.status_code == 201:
        playlist_id = create_playlist_response.json()["id"]
        print()
        print()
        print(f"Playlist '{playlist_name}' created successfully!")
        return playlist_id
    else:
        print(f"Failed to create playlist. Error {create_playlist_response.status_code}: {create_playlist_response.text}")
        return None


def addTrackstoPlaylist(playlistID):
    # user to authenticate again
    auth_url = f"{oauth_url}?{oauth_paramsPlaylistTracks}"
    print("Click on the URL and provide the access code to allow Spotify to add tracks to your playlist.")
    print(auth_url)
    code = input("Enter the code parameter from the redirected URL: ")
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    access_token = token_response.json()['access_token']

    # Add tracks to playlist using new access token
    trackData = {"uris": filteredTracks, "position": 0}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"https://api.spotify.com/v1/playlists/{playlistID}/tracks", headers=headers,
                             data=json.dumps(trackData))

    if response.status_code == 201:
        print()
        print("Tracks added successfully! Take a look at your account!!!!!")
    else:
        print(f"Failed to add tracks to playlist. Error {response.status_code}: {response.text}")


topArtists = getUserTopArtists(access_token)
trackIds = getTopTracksByArtists(access_token,topArtists)

# get top tracks by artists
topArtists = getUserTopArtists(access_token)
trackIds = getTopTracksByArtists(access_token,topArtists)

# get audio features of tracks
audioFeatures = getAudioFeatures(access_token, trackIds)

# filter tracks based on user input for playlist parameters
filteredTracks = filterTracksByAudioFeatures(audioFeatures, float(danceability), float(valence), float(energy))

def getUserId(access_token):
    me_url = 'https://api.spotify.com/v1/me'
    me_headers = {'Authorization': f'Bearer {access_token}'}
    me_response = requests.get(me_url, headers=me_headers)
    if me_response.status_code == 200:
        return me_response.json()['id']
    return None

playlist_name = "Fire Playlist"
playlist_description = "New playlist description"
playlist_description = f'This playlist has songs from my fav artists with danceability of {danceability}, valence of {valence}, and energy of {energy}!!'
playlist_id = create_playlist(getUserId(access_token), playlist_name, playlist_description)
addTrackstoPlaylist(playlist_id)



