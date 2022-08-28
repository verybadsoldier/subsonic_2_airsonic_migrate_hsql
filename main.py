import argparse
import os.path
from pathlib import Path
from typing import Dict
import json

_BASE_DIR = Path(r'D:\airsonic_migrate')

_AS_MEDIAFILE = r'airsonic_MEDIA_FILE.json'
_SS_MEDIA = r'subsonic_media.json'
_SS_RATINGS = r'subsonic_ratings.json'
_SS_STARRED_MEDIA = r'subsonic_starred_media.json'

def _get_path(filename: Path):
    return os.path.join(_BASE_DIR, filename)

def _get_read_json(filename: Path):
    with open(_get_path(filename), encoding='utf-8') as f:
        return json.load(f)

def _get_starred(ss_starred, media: Dict[int, object]):
    starred = []
    for d in ss_starred:
        media_id = int(d['MEDIA_FILE_ID'])
        media_file = media.get(media_id)
        if media_file is None:
            continue
        starred.append((d, media_file))
    return starred


def _find_media_in_airsonic(ss_path, json_as_media):
    _SS_BASE = 'f:\\audio\\'
    _AS_BASE = '/var/music/'
    source_path = ss_path.lower()
    if not source_path.startswith(_SS_BASE):
        raise RuntimeError('Unexpected path')

    source_path = source_path.replace(_SS_BASE, _AS_BASE)
    source_path = source_path.replace('\\', '/')

    return json_as_media.get(source_path)


def _get_starred_sql(starred_media, json_as_media):
    sqls = []
    for ss_starred, ss_media in starred_media:
        as_media_id = _find_media_in_airsonic(ss_media['PATH'], json_as_media)
        if as_media_id is None:
            continue
        created = ss_starred['CREATED']
        username = ss_starred['USERNAME']
        media_id = as_media_id
        sql = f"INSERT INTO STARRED_MEDIA_FILE (MEDIA_FILE_ID, USERNAME, CREATED) VALUES({media_id}, '{username}','{created}')"
        sqls.append(sql)
    return sqls

def _get_user_rating_sql(ss_user_ratings, json_as_media):
    sqls = []
    for ss_rating in ss_user_ratings:
        as_media_id = _find_media_in_airsonic(ss_rating['PATH'], json_as_media)
        if as_media_id is None:
            continue
        rating = ss_rating['RATING']
        username = ss_rating['USERNAME']
        media_id = as_media_id
        sql = f"INSERT INTO USER_RATING (MEDIA_FILE_ID, USERNAME, RATING) VALUES({media_id}, '{username}','{rating}')"
        sqls.append(sql)
    return sqls

def main():
    json_as_media = _get_read_json(_AS_MEDIAFILE)
    json_ss_media = _get_read_json(_SS_MEDIA)
    json_ss_ratings = _get_read_json(_SS_RATINGS)
    json_ss_starred = _get_read_json(_SS_STARRED_MEDIA)

    json_as_media = list(json_as_media.values())[0]
    json_ss_ratings = list(json_ss_ratings.values())[0]

    json_as_media_dict = {}
    for v in json_as_media:
        full_path = v['MUSIC_FOLDER_PATH'] + '/' + v['MEDIA_FILE_PATH']
        json_as_media_dict[full_path.lower()] = v['ID']

    json_ss_starred = list(json_ss_starred.values())[0]
    ss_media_dict = {}
    for m in list(json_ss_media.values())[0]:
        ss_media_dict[m['ID']] = m

    # starred
    starred_media_ss = _get_starred(json_ss_starred, ss_media_dict)
    starred_sqls = _get_starred_sql(starred_media_ss, json_as_media_dict)

    for s in starred_sqls:
        print(s)

    # user ratings
    rating_sqls = _get_user_rating_sql(json_ss_ratings, json_as_media_dict)
    for s in rating_sqls:
        print(s)


if __name__ == '__main__':
    main()
