import argparse
import requests

from collections import OrderedDict

URL = "https://api.planningcenteronline.com"
API = ""
SUB_API = ""
PCO_ID = ""
USERNAME=""
PASSWORD=""

def get_args():
    parser = argparse.ArgumentParser(
        prog="PCO Setlist Scraper",
        description="Gets the high level setlist information for a service."
    )

    # parser.add_argument("-d", "--date")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--pco_id")
    return parser.parse_args()

def get_service_plans(service_id):
    url = f"{URL}/services/v2/service_types/{service_id}/plans"
    params={"order":"sort_date","filter":"future"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))

    return response.json()


def get_service_plan(service_id,plan_id):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}"
    params={"order":"sort_date","filter":"future"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))

    return response.json()


def get_service_plan_items(service_id,plan_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/items"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()


def get_service_plan_item_song(service_id,plan_id,item_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/items/{item_id}/song"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()

def get_service_plan_item_key(service_id,plan_id,item_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/items/{item_id}/key"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()

def get_service_plan_item_arrangement(service_id,plan_id,item_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/items/{item_id}/arrangement"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()

def get_service_plan_item_assingments(service_id,plan_id,item_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/items/{item_id}/assingments"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()

def get_service_plan_item_notes(service_id,plan_id,item_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/items/{item_id}/item_notes"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()


def get_service_plan_team_members(service_id,plan_id, offset=0):
    url = f"{URL}/services/v2/service_types/{service_id}/plans/{plan_id}/team_members"
    params={"offset":f"{offset}"}
    response = requests.get(url=url, params=params, auth=(USERNAME,PASSWORD))
    return response.json()

def get_service_team(team_id):
    url = f"{URL}/services/v2/teams/{team_id}"
    response = requests.get(url=url, auth=(USERNAME,PASSWORD))
    return response.json()


def get_service_info(service_id):
    plans = get_service_plans(service_id)
    plan = plans.get("data")[0]
    plan_id = plan.get("id")

    next = True
    offset = 0
    items=[]
    while next:

        items_response = get_service_plan_items(service_id, plan_id, offset=offset)
        # print(items_response)
        items.extend(items_response.get("data", []))

        meta = items_response.get("meta")
        # print(meta)
        offset = meta.get("next", {}).get("offset", 0)
        count = meta.get("count", 0)
        total_count = meta.get("total_count", {})
        # print(offset)
        # print(count)
        # print(total_count)
        next = meta.get("next", None) is not None
        # print(f"Next: {next}")

    songs = []

    for item in items:

        if item.get("attributes", {}).get("item_type", "") == "song":
            # print(item)
            songs.append(item)

    songs_dict = OrderedDict()

    for song in songs:
        # print(song.get("attributes", {}).get("title"))
        item_id = song.get("id")
        song_title = song.get("attributes", {}).get("title")
        song_info = get_service_plan_item_song(service_id,plan_id,item_id)
        song_key = get_service_plan_item_key(service_id,plan_id,item_id)
        song_arragement = get_service_plan_item_arrangement(service_id,plan_id,item_id)
        songs_dict[song_title] = {
            "title": song_title,
            "bpm": song_arragement.get("data",{}).get("attributes",{}).get("bpm", 0),
            "meter": song_arragement.get("data",{}).get("attributes",{}).get("meter", 0),
            "key": song_key.get("data",{}).get("attributes",{}).get("starting_key", 0),
        }

    print(plan.get("attributes",{}).get("title"))
    print(plan.get("attributes",{}).get("series_title"))
    print(plan.get("attributes",{}).get("dates"))

    for song in songs_dict:
        print(song)
        bpm = songs_dict[song].get("bpm")
        meter = songs_dict[song].get("meter")
        key = songs_dict[song].get("key")
        print(f"\tMeter: {meter}")
        print(f"\tBPM: {bpm}")
        print(f"\tKey: {key}")

    team_members_response = get_service_plan_team_members(service_id,plan_id)
    # print(team_members_response)
    team_members = team_members_response.get("data",[])

    team_info = {}

    for team_member in team_members:
        name = team_member.get("attributes").get("name")
        team_position_name = team_member.get("attributes").get("team_position_name")
        team_id = team_member.get("relationships").get('team').get("data").get("id")
        if team_id not in team_info.keys():
            team_info_response = get_service_team(team_id)
            team_info[team_info_response.get("data",{}).get("id")]={"name":team_info_response.get("data",{}).get("attributes",{}).get("name"),"members":[]}
        team_info[team_id]["members"].append({"position": team_position_name, "name": name})

    print("Teams")

    for team in team_info:
        team_name = team_info.get(team).get("name")
        print(team_name)
        members = team_info.get(team).get("members")
        for member in members:
            team_position_name = member.get("position")
            name = member.get("name")
            print(f"\t{team_position_name}: {name}")

if __name__ == "__main__":
    args = get_args()
    USERNAME = args.username
    PASSWORD = args.password
    PCO_ID = args.pco_id

    get_service_info(PCO_ID)
    # print(get_service_plans(PCO_ID))
