import requests
import json
import tkinter as tk
from tkinter import filedialog
import pathlib


def get_collection_info(collection_id_list: list):
    """Gets a list of collection dicts from a list of collection ids
    :param collection_id_list: List of steam collection IDs
    :return: List of collection dicts
    """
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
    params = {
        'collectioncount': len(collection_id_list)
    }
    for i, col_id in enumerate(collection_id_list):
        params['publishedfileids[{}]'.format(i)] = col_id
    r = requests.post(url=url, data=params)
    json_content = json.loads(r.text)
    collections: list = json_content['response']['collectiondetails']
    return collections


def get_item_ids(collection_id_list: list, add_linked_collections: bool = True):
    """Gets the list of item IDs in a steam collection
    :param collection_id_list: List of steam collection IDs
    :param add_linked_collections: Whether to add items from linked collections or not
    :return: List of item ids
    """
    collections: list = get_collection_info(collection_id_list)
    id_set = set()
    col_count = 0
    while collections:
        cur_collection = collections.pop(0)
        col_count += 1
        col_name = cur_collection['publishedfileid']
        if cur_collection['result'] != 1:
            print("Collection {} not found. Skipping...".format(col_name))
            continue
        mod_count = 0
        for cur_item in cur_collection['children']:
            if cur_item['filetype'] == 0:
                id_set.add(cur_item['publishedfileid'])
                mod_count += 1
            elif cur_item['filetype'] == 2:
                if add_linked_collections:
                    collections += get_collection_info([cur_item['publishedfileid']])
                    added_col_name = cur_item['publishedfileid']
                    print("Found linked collection {}, adding to list of collections...".format(added_col_name))
        print("Added {} mods from collection {}".format(mod_count, col_name))
    print("Got {} mods in total from {} collections!".format(len(id_set), col_count))
    return list(id_set)


def get_path_to_disabled_addons_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title='Open the GarrysMod/garrysmod/cfg/addonnomount.txt file',
        filetypes=(('GMod disabled addons file', 'addonnomount.txt'),)
    )
    actual_path = pathlib.Path(file_path)
    if actual_path.name != 'addonnomount.txt':
        raise Exception("Wrong path")
    return actual_path


def main():
    input_collection = list(map(int, input().split()))
    ids = get_item_ids(input_collection)
    path = get_path_to_disabled_addons_file()
    print(path)


if __name__ == "__main__":
    main()
