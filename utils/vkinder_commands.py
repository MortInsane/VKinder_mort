from config.config import VK_USER_TOKEN, VK_VERSION
import requests


def get_city(_city):
    params = {"v": VK_VERSION, "access_token": VK_USER_TOKEN, 'country_id': 1, 'count': 1, 'q': _city}

    url = f"https://api.vk.com/method/database.getCities"
    response = requests.get(url, params=params).json()
    if not response['response']['items']:
        _city = 0
        return _city
    else:
        for search_city_id in response['response']['items']:
            _city = search_city_id['id']
            return _city


def search_candidates(_sex, _city, offset, age_from, age_to):

    params = {
        "v": VK_VERSION,
        "access_token": VK_USER_TOKEN,
        'offset': offset,
        "sex": _sex,
        "city": _city,
        "age_from": age_from,
        "age_to": age_to,
        "has_photo": 1,
        "fields": "relation"
    }

    url = f"https://api.vk.com/method/users.search"
    response = requests.get(url, params=params).json()

    for candidate in response['response']['items']:
        is_closed = candidate['is_closed']
        if is_closed or 'relation' not in candidate or candidate['relation'] not in (0, 1, 6):
            offset += 1
        else:
            candidate.update(custom_offset=offset)
            return candidate


def get_photos(user_id):
    show_photo = []
    params = {
        "album_id": "profile",
        "extended": 1,
        "access_token": VK_USER_TOKEN,
        "v": VK_VERSION,
        "owner_id": user_id,

    }

    url = f"https://api.vk.com/method/photos.get"
    response = requests.get(url, params=params, timeout=5).json()

    base_json = sorted(response['response']['items'], key=lambda like: like['likes']['count'], reverse=True)
    for item in base_json:
        photo_id = item['id']

        photo = f"photo{user_id}_{photo_id}"
        show_photo.append(photo)
    top_photos = ','.join(show_photo[:3])
    return top_photos
