from random import randrange
from config.config import VK_USER_TOKEN, VK_GROUP_TOKEN, VK_VERSION
from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from utils.vkinder_commands import get_photos, get_city, search_candidates
from utils.db_utils.db_api import create_tables, register_user, get_user, get_candidate, add_candidate
import requests


api = vk_api.VkApi(token=VK_GROUP_TOKEN)
longpoll = VkLongPoll(api)


def write_msg(user_id, message, attachment=None):
    api.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),
                                 'attachment': attachment})


class VKinder:
    def __init__(self, token, version, username):
        self.token = token
        self.version = version
        self.username = username
        self.user_data = dict()
        self.user_new_data = dict()
        self.city = 0
        self.offset = 0
        self.sex = 1
        self.age_from = 18
        self.age_to = 70
        self.match_id = 0
        self.match_name = ''
        self.match_lastname = ''
        self.relation = 0
        self.first_name = ''
        self.last_name = ''
        self.age = 14

    def get_user_info(self):
        params = {
            "user_ids": self.username,
            "access_token": self.token,
            "v": self.version,
            "fields": "sex, city, relation, bdate"
        }

        url = f"https://api.vk.com/method/users.get"
        response = requests.get(url, params=params).json()

        if "response" in response:
            for item in response['response']:
                user_id = item["id"]
                self.first_name = item["first_name"]
                self.last_name = item["last_name"]

                sex_key = item.get("sex", "nodata")
                if sex_key != "nodata":
                    self.sex = item["sex"]
                else:
                    self.sex = sex_key

                city_key = item.get("city",  "nodata")
                if city_key != "nodata":
                    self.city = item["city"]["id"]
                else:
                    self.city = city_key

                bdate_key = item.get("bdate", "nodata")
                if bdate_key != "nodata":
                    raw_bdate = bdate_key.split(".")
                    if len(raw_bdate) < 3:
                        self.age = bdate_key
                    else:
                        now = datetime.now()
                        tmp_date = f"{raw_bdate[2]}-{int(raw_bdate[1]):02d}-{int(raw_bdate[0]):02d}"
                        tmp_date = datetime.fromisoformat(tmp_date)
                        self.age = (now-tmp_date).days // 365
                else:
                    self.age = bdate_key
                if 'relation' in item:
                    self.relation = item["relation"]
                self.user_data[user_id] = {"first_name": self.first_name, "last_name": self.last_name,
                                           "sex": self.sex, "city": self.city,
                                           "age": self.age, "relation": self.relation}
            return self.user_data

    def registration(self):
        new_user_data = self.get_user_info()
        friendly_name = ''
        example = ''
        for _id, items in new_user_data.items():
            if _id not in self.user_new_data:
                self.user_new_data[_id] = dict()
                for item in items:
                    if item not in self.user_new_data[_id]:
                        if items[item] == 'nodata':
                            if item == 'age':
                                friendly_name = "возраст"
                                example = "25"
                            if item == 'city':
                                friendly_name = "город"
                                example = "Москва"

                            write_msg(_id, f'\n❗Укажите {friendly_name}❗\n'
                                           f'Например: {example} ')

                            if item in ("age", "city"):
                                for event in longpoll.listen():
                                    if event.type == VkEventType.MESSAGE_NEW:
                                        if event.to_me:
                                            res = event.text
                                            if item == 'city':
                                                res = get_city(_city=res)
                                                if res == 0:
                                                    write_msg(_id, f'\nНеверно указан {friendly_name}❗\n')
                                                    return False

                                            self.user_new_data[_id][item] = res
                                            break
                        else:
                            self.user_new_data[_id][item] = items[item]
        return self.user_new_data

    def searching_candidate(self):
        write_msg(self.username, f'\nДля начала поиска напиши СТАРТ\n'
                                 f'Для прекращения напиши СТОП')
        for candidate_event in longpoll.listen():
            if candidate_event.type == VkEventType.MESSAGE_NEW and candidate_event.to_me:
                if candidate_event.text.lower() == 'старт':

                    return self.next_candidate()
                elif candidate_event.text.lower() == "стоп":
                    write_msg(candidate_event.user_id, f"Bye! Пиши ПОИСК в любое время)")
                    break

    def next_candidate(self):
        write_msg(self.username, f'\nЕсли хочешь продолжить поиск напиши ДАЛЕЕ\n'
                                 f'Для прекращения напиши СТОП')
        while True:
            for next_candidate_event in longpoll.listen():
                if next_candidate_event.type == VkEventType.MESSAGE_NEW and next_candidate_event.to_me:
                    if next_candidate_event.text.lower() == 'далее':
                        write_msg(next_candidate_event.user_id, f"Если от увиденного, у тебя зародились бабочки в животе\n"
                                                                f"Напиши +, чтобы я добавил этого человека в избранное.")
                        user_sex = api.method('users.get', {'user_ids': next_candidate_event.user_id, 'fields': 'sex'})
                        if user_sex[0]['sex'] == 1:
                            self.sex = 2
                        else:
                            self.sex = 1
                        candidate = search_candidates(self.sex, self.city, self.offset, self.age_from, self.age_to)
                        self.offset = candidate['custom_offset'] + 1

                        output = f"""
                        Фамилия: {candidate['last_name']} Имя: {candidate['first_name']}
                        Профиль: https://vk.com/id{candidate['id']}
                        """
                        attachments = get_photos(candidate['id'])
                        write_msg(next_candidate_event.user_id, output, attachments)
                    elif next_candidate_event.message.lower() == '+':
                        candidate_exists = get_candidate(id_vk=candidate['id'])
                        if candidate_exists is None:
                            add_candidate(id_vk=candidate['id'], first_name=candidate['first_name'],
                                          last_name=candidate['last_name'],
                                          user_link=f"https://vk.com/id{candidate['id']}",
                                          id_user=next_candidate_event.user_id)
                            write_msg(next_candidate_event.user_id, f"Добавил в ⭐. Пиши ДАЛЕЕ, чтобы подыскать новую пару")
                        else:
                            write_msg(next_candidate_event.user_id, f"Пользователь уже в ⭐, пиши ДАЛЕЕ.")
                    elif next_candidate_event.text.lower() == "стоп":
                        write_msg(next_candidate_event.user_id, f"Bye! Пиши ПОИСК в любое время)")
                        break
            return False


if __name__ == '__main__':
    create_tables()
    for new_event in longpoll.listen():
        if new_event.type == VkEventType.MESSAGE_NEW:
            if new_event.to_me:
                bot = VKinder(token=VK_USER_TOKEN, version=VK_VERSION, username=f"{new_event.user_id}")
                request = new_event.text
                if get_user(id_vk=new_event.user_id) is None:
                    if request.lower() == "нет":
                        write_msg(new_event.user_id, "Мне очень жаль\n"
                                                     "Если передумаешь, пиши ПРИВЕТ")
                    elif request.lower() == "да":
                        user_data = bot.registration()

                        if user_data is not False:
                            id_vk = new_event.user_id
                            first_name = user_data[new_event.user_id]["first_name"]
                            last_name = user_data[new_event.user_id]["last_name"]
                            city = user_data[new_event.user_id]["city"]
                            age = user_data[new_event.user_id]["age"]
                            sex = user_data[new_event.user_id]["sex"]
                            relation = user_data[new_event.user_id]["relation"]

                            register_user(id_vk=id_vk, first_name=first_name, last_name=last_name,
                                          city=city, age=age, sex=sex, relation=relation)
                            write_msg(new_event.user_id, f"Регистрация завершена, напиши ПОИСК")
                    else:
                        user = get_user(id_vk=new_event.user_id)
                        write_msg(new_event.user_id, f"Привет! "
                                                     f"Я VKinder, и я помогу тебе найти пару.\n "
                                                     f"Но для начала, необходимо пройти регистрацию,\n "
                                                     f"Напиши [да✅/нет⛔]?")
                else:
                    if request.lower() == 'поиск':
                        bot.searching_candidate()
                    else:
                        write_msg(new_event.user_id, "Вы уже зарегистрированы\n"
                                                     "Напиши ПОИСК, и я подыщу тебе пару❤")
