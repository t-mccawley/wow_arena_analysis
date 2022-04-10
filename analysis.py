from audioop import reverse
import json
import struct
import numpy as np

playable_classes_fp = "data\playable_classes_index.json"
playable_races_fp = "data\playable_races_index.json"
leaderboard_fp = "data\leaderboard.json"

def _create_comp_name(class_1,class_2):
    if class_1 == "None" or class_2 == "None":
        return None
    if class_1 < class_2:
        return("{} - {}".format(class_1,class_2))
    return("{} - {}".format(class_2,class_1))

def _determine_team_comp(team_data,verbosity=0):
    rating = team_data['rating']
    rank = team_data['rank']
    name = team_data['team']['name']
    realm = team_data['team']['realm']['slug']
    team_games_played = team_data['season_match_statistics']['played']
    if verbosity == 2:
        print('Team: {} ({})'.format(name,realm))
        print('\tRank: {}'.format(rank))
        print('\tRating: {}'.format(rating))
        print('\tTeam Games Played: {}'.format(team_games_played))
        print('\tMembers:')
    valid_member_list = []
    for member_data in team_data['team']['members']:
        member_name = member_data['character']['name']
        member_class_id = member_data['character']['playable_class']['id']
        member_class = playable_classes_dict[member_class_id]
        member_race_id = member_data['character']['playable_race']['id']
        member_race = playable_races_dict[member_race_id]
        member_games_played = member_data['season_match_statistics']['played']
        if member_class_id != 0 and member_games_played > 0:
            valid_member_list.append((member_games_played,member_name,member_class))
        if verbosity == 2:
            print('\t\tName: {}'.format(member_name))
            print('\t\tClass: {}'.format(member_class))
            print('\t\tRace: {}'.format(member_race))
            print('\t\tGames Played: {}'.format(member_games_played))
            print('\t\tFraction Games Played: {:0.0f}%'.format(member_games_played/team_games_played*100))
            print()
    if len(valid_member_list) >= 2:
        sorted_valid_member_list = sorted(valid_member_list,reverse=True)
        comp_name = _create_comp_name(sorted_valid_member_list[0][2],sorted_valid_member_list[1][2])
        if verbosity == 1:
            print('Team: {} ({})'.format(name,realm))
            print('\tRank: {}'.format(rank))
            print('\tRating: {}'.format(rating))
            print('\tComp: {}'.format(comp_name))

# fetch playable classes
f = open(playable_classes_fp)
playable_classes_index = json.load(f)
playable_classes_dict = {}
for playable_class in playable_classes_index['classes']:
    playable_classes_dict[int(playable_class['id'])] = playable_class['name']
playable_classes_dict[0] = "None"
f.close()

# fetch race classes
f = open(playable_races_fp)
playable_races_index = json.load(f)
playable_races_dict = {}
for playable_race in playable_races_index['races']:
    playable_races_dict[int(playable_race['id'])] = playable_race['name']
playable_races_dict[0] = "None"
f.close()

# construct leaderboard data
f = open(leaderboard_fp)
# print(f)
data = json.load(f)
for team_data in data['entries']:
    _determine_team_comp(team_data,verbosity=1)
f.close()