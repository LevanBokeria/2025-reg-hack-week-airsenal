import os
import pandas as pd

from airsenal.framework.utils import *


from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_AI_KEY"),
)


def get_previous_season(season):
    """
    Assuming season is in the format '2425' we
    want to return '2324'
    """
    first_year = int(season[:2])
    second_year = int(season[2:])
    return f"{first_year}{second_year}"



def get_historical_player_minutes(team, season):
    output = ""
    for gw in range(1,39):
        fixtures = get_fixtures_for_gameweek(gw, season=season)
        players = list_players(team=team, season=season, gameweek=gw)

        for fixture in fixtures:
            if fixture.home_team != team and fixture.away_team != team:
                continue
            output += "\n====================\n"
            if fixture.home_team == team:
                opponent = fixture.away_team
                home_or_away = "home"
            else:
                opponent = fixture.home_team
                home_or_away = "away"
            output += f"{opponent} ({home_or_away}) \n\n"
            for player in players:
                playerscore = get_player_scores(fixture, player)
                if playerscore:
                    output+= f"{player.name}: {playerscore.minutes} \n"
    return output


player_data = open("player_minutes_ARS_2324.txt").read()

players_to_predict = [p.name for p in list_players(team="ARS", season="2425", gameweek=1)]

# ---- Construct prompt ----
system_msg = (
    "You are a football analyst. Based on last season's match data, predict how many minutes "
    "each player is likely to play in the next match. Consider player availability and who typically "
    "replaces whom when someone is missing. Your output must be a valid CSV string with two columns: "
    "`player` and `predicted_minutes`. Do not include any explanation, markdown, or table formatting—"
    "just raw CSV content. The header row must be: player,predicted_minutes."
)


def get_players(gameweek=1, team="ARS", season="2425", ):
    players_to_predict = [p.name for p in list_players(team=team, season=season, gameweek=gameweek)]
    return players_to_predict

def get_minutes_injuries_for_players(player_list, gameweek, season):
    rows = []
    for player in player_list:
        availability = "unavailable" if get_player(player).is_injured_or_suspended(season, gameweek, gameweek) else "available"
        recent_minutes = get_recent_minutes_for_player(get_player(player), 4, season, gameweek, session)[:-1]
        row = f"{player}: {availability} {recent_minutes}"
        rows.append(row)
    return "\n".join(rows)


def construct_user_msg(gameweek, team, season, historical_mins_txt):
    user_msg = ""
    players = get_players(gameweek, team, season)
    if gameweek == 1:
        user_msg += f"Here is the data for last season:\n{historical_mins_txt}\n\n"
    else:
        recent_mins = get_minutes_injuries_for_players(players, gameweek, season)
        user_msg += f"Here is the player availability followed by a list of minutes played in the last few matches (most recent last):\n{recent_mins} \n\n"
    player_list = "\n".join(f"- {p}" for p in players)
    user_msg += f"Now predict the number of minutes each of the following players will play in the next match:\n"
    user_msg += f"{player_list}\n\n"
    user_msg += "Please return the result as a table with columns: player, predicted_minutes."
    return user_msg



def get_response(system_msg, user_msg):

    # ---- Send request to OpenAI ----
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.5
    )

    reply = response.choices[0].message.content
    return reply

def process_team(team="ARS", season="2425", historical_mins_txt):
    results_dict = {"player_id": [], "date": [], "minutes": [],  "predmin": []}
    for gameweek in range(1,39):
        print(f"Processing gamewek {gameweek}")
        players = list_players(team=team, season=season, gameweek=gameweek)
        fixtures = get_fixtures_for_player(players[0], gw_range=[gameweek], season=season)
        for fixture in fixtures:
            date = fixture.date

            # construct prompt for the OpenAI API
            user_message = construct_user_msg(gameweek, team, season, historical_mins_txt)
            # CALL THE API!!!!
            result = get_response(system_msg, user_msg)
            # debug output
            with open(f"predictions_{team}_{season}_{gameweek}_{date}.csv", "w") as outfile:
                outfile.write(result)
            # process output
            result_lines = result.split("\n")[1:]
            for line in result_lines:
                player_name, predicted_mins = line.split(",")
                player = get_player(player_name)
                player_score = get_player_scores(fixture, player)
                if not player_score:
                    continue
                results_dict["player_id"].append(player.player_id)
                results_dict["date"].append(date)
                results_dict["minutes"].append(player_score.minutes)
                results_dict["predmin"].append(predicted_mins)

    return results_dict


def process_season(season="2425"):
    team_dicts = list_teams(season)
    teams = [t["name"] for t in team_dicts]
    results_dicts = {}
    for team in teams:
        print(f"Processing {team}")
        historical_minutes_txt = get_historical_player_minutes(team, season)
        results_dicts[team] = process_team(team, season, historical_mins_txt)
    return results_dicts
