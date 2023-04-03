import csv
import pandas as pd

from pandas import read_csv, Series, DataFrame, concat
import pathlib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import requests
import json

def clean_data(x):
    if isinstance(x, str):
        return x.replace(" ", "")
    else:
        print(x)
        return x

def get_user_data(userId):
    apiKey = "E3ECE458BA26350EAF264840A63BF51E"
    steamId = userId
    ownedGameApi = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apiKey}&steamid={steamId}&format=json&include_appinfo=True"
    friendListApi = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={apiKey}&steamid={steamId}&relationship=friend"
    recentPlayedApi = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={apiKey}&steamid={steamId}&format=json"

    userDict = {'userid': steamId, 'recentPlayedGames':[], 'ownedGames' : [], 'friendList': []}
    userGameList = list()
        
    try:
        response = requests.get(recentPlayedApi).json()
        games = response['response']['games']
        for game in games:
            userDict['recentPlayedGames'].append((game['name'],game['playtime_forever']))
    except:
        print("no recently games")

    try:
        response = requests.get(ownedGameApi).json()
        games = response['response']['games']
        for game in games:
            userDict['ownedGames'].append((game['name'],game['playtime_forever']))
            userGameList.append(game['name'])
    except:
        print("no games found")

    try:
        response =  requests.get(friendListApi).json()
        friends = response['friendslist']['friends']
        for friend in friends:
            userDict['friendList'].append(friend['steamid'])
    except:
        print("Could not retrieve friends data")

    userDict['ownedGames'].sort(key = lambda x: x[1], reverse=True)

    return userGameList


def generate_recommendation(n_recommendation, userId):
    expanded_game_data = pd.read_csv('expanded_game_data.csv')
    expanded_game_data = expanded_game_data.rename(columns={"name_x": "name"})
    expanded_game_data = expanded_game_data.fillna('')
    expanded_game_data.drop_duplicates("name")
    indices = Series(expanded_game_data.index, index=expanded_game_data['name']).drop_duplicates()
    expanded_game_data['combined_feature'] = expanded_game_data['genre'] + expanded_game_data['publisher'] + expanded_game_data['developer'] + expanded_game_data['game_details']
    expanded_game_data.loc[:, 'genre'] = expanded_game_data['genre'].apply(clean_data)
    expanded_game_data.loc[:, 'game_details'] = expanded_game_data['game_details'].apply(clean_data)
    expanded_game_data.loc[:, 'popular_tags'] = expanded_game_data['popular_tags'].apply(clean_data)
    expanded_game_data.loc[:, 'publisher'] = expanded_game_data['publisher'].apply(clean_data)
    expanded_game_data.loc[:, 'developer'] = expanded_game_data['developer'].apply(clean_data)

    col_names = list(map(str, range(1, n_recommendation + 1)))
    col_names = ["user_id"] + col_names
    listGames = expanded_game_data['name'].unique()

    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(expanded_game_data['combined_feature'])
    cosine_sim_matrix = cosine_similarity(count_matrix, count_matrix)

    listSuggestion = list()
    userGameList = get_user_data(userId)

    for row in userGameList:
        if row not in listGames:
            continue
        
        idx = indices[row]

        if type(idx) is Series:
            return []

        sim_scores = list(enumerate(cosine_sim_matrix[idx]))

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:n_recommendation + 1]

        movie_indices = [i[0] for i in sim_scores]

        listSuggestion.extend(expanded_game_data['name'].iloc[movie_indices].tolist())

    recommendation = expanded_game_data.loc[expanded_game_data['name'].isin(listSuggestion)]
    recommendation = recommendation.loc[~recommendation['name'].isin(userGameList)]
    recommendation = recommendation.sort_values(by="score", ascending=False)
    recommendation = recommendation[['name', 'appid', 'url', 'summary', 'date', 'score', 'developer', 'genre']]
   
    if len(recommendation.index) < n_recommendation:
        #return recommendation.to_json(orient="split")
        return recommendation
    else:
        #return recommendation[0:n_recommendation].to_json(orient="split")
        return recommendation[0:n_recommendation]

def main():
    res = generate_recommendation(20)


if __name__ == "__main__":
    main()