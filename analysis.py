import json
import numpy as np
import matplotlib.pyplot as plt

# file paths
playable_classes_fp = "data\playable_classes_index.json"
playable_races_fp = "data\playable_races_index.json"
leaderboard_fp = "data\leaderboard.json"
# leaderboard_fp = "data\leaderboard_partial.json"

# helper classes and functions
class TeamData:
    def __init__(self,name,rating,rank,comp):
        self.name = name
        self.rating = rating
        self.rank = rank
        self.comp = comp

    def print(self):
        print('Team: {}'.format(self.name))
        print('\tRank: {}'.format(self.rank))
        print('\tRating: {}'.format(self.rating))
        print('\tComp: {}'.format(self.comp))

def _create_comp_name(class_1,class_2):
    if class_1 == "None" or class_2 == "None":
        return None
    if class_1 < class_2:
        return("{} - {}".format(class_1,class_2))
    return("{} - {}".format(class_2,class_1))

def _determine_team_comp(team_data_raw,verbosity=0):
    rating = team_data_raw['rating']
    rank = team_data_raw['rank']
    team_name = '{} ({})'.format(team_data_raw['team']['name'],team_data_raw['team']['realm']['slug'])
    team_games_played = team_data_raw['season_match_statistics']['played']
    if verbosity == 2:
        print('Team: {}'.format(team_name))
        print('\tRank: {}'.format(rank))
        print('\tRating: {}'.format(rating))
        print('\tTeam Games Played: {}'.format(team_games_played))
        print('\tMembers:')
    valid_member_list = []
    comp = None
    if 'members' in team_data_raw['team']:
        for member_data in team_data_raw['team']['members']:
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
            comp = _create_comp_name(sorted_valid_member_list[0][2],sorted_valid_member_list[1][2])
    
    team_data = TeamData(team_name,rating,rank,comp)
    if verbosity == 1:
        team_data.print()

    return(team_name,team_data)

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
f = open(leaderboard_fp, encoding="utf8")
# print(f)
data = json.load(f)
team_data_dict = {}
for team_data_raw in data['entries']:
    team_name, team_data = _determine_team_comp(team_data_raw,verbosity=0)
    team_data_dict[team_name] = team_data
f.close()

# calculate statistics and plot
rating_bracket_dict = {} # key of rating floored to nearest 100 with value of list of TeamData objects
rating_brackets = np.arange(0,3100,100)
for rating in rating_brackets:
    rating_bracket_dict[rating] = []
for team_name in team_data_dict:
    team_data = team_data_dict[team_name]
    rating_key = int(np.floor(team_data.rating/100)*100)
    rating_bracket_dict[rating_key].append(team_data)
# compute count of team comps in each rating bucket
rating_comp_dict = {} # {rounded_rating, {comp,percent}}
comp_dict = {}
for rating_bracket in rating_bracket_dict:
    # check for init
    if rating_bracket not in rating_comp_dict:
        rating_comp_dict[rating_bracket] = {}
    rating_bracket_count = len(rating_bracket_dict[rating_bracket])
    for team_data in rating_bracket_dict[rating_bracket]:
        team_comp = team_data.comp
        # check for init
        if team_comp not in rating_comp_dict[rating_bracket]:
            rating_comp_dict[rating_bracket][team_comp] = 0
        if team_comp not in comp_dict:
            comp_dict[team_comp] = True
        # count
        rating_comp_dict[rating_bracket][team_comp] += 1
    # normalize
    for team_comp in rating_comp_dict[rating_bracket]:
        rating_comp_dict[rating_bracket][team_comp] /= rating_bracket_count
        rating_comp_dict[rating_bracket][team_comp] *= 100
# print(rating_comp_dict)
print(comp_dict.keys())
# plot
plt.figure()
from itertools import cycle
lines = ["-","--","-.",":"]
linecycler = cycle(lines)
for team_comp in comp_dict:
    if team_comp == None:
        continue
    comp_occurrence = []
    for rating_bracket in rating_brackets:
        if team_comp not in rating_comp_dict[rating_bracket]:
            val = 0
        else:
            val = rating_comp_dict[rating_bracket][team_comp]
        comp_occurrence.append(val)
    if max(comp_occurrence) >= 1.0:
        plt.plot(rating_brackets,comp_occurrence,label=team_comp,linestyle=next(linecycler))

plt.legend(loc='upper left')
plt.xlabel('Rating')
plt.ylabel('Comp Frequency [%]')
plt.xticks(rating_brackets,rotation=45)
plt.xlim(1500,2600)
plt.ylim(0,7.5)
plt.grid()
plt.show()