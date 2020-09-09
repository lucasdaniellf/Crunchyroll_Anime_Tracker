import cloudscraper
from bs4 import BeautifulSoup
import json
import copy
import time
from colorama import Fore, Style
import threading

# GENERAL
verif_sair = False

# if anime.json does not exist:

try:
    with open('anime.json', 'r') as anime_json:
        pass
except FileNotFoundError:
    print('Creating file...')
    with open('anime.json', 'w') as anime_json:
        json_data = []
        json.dump(json_data, anime_json)
    print('File created!')

# PARSING THE INFORMATION
scraper = cloudscraper.create_scraper()


# FUNCTIONS
def alpha_sort(dictionaries):
    for i in dictionaries:
        return i


def check_list():
    print('These are the animes you are tracking:')
    with open('anime.json', 'r') as anime_json:
        json_data = json.load(anime_json)

        # FOR ELEMENTOS (DICIONÁRIOS) IN LISTA -> FOR CHAVE EM CADA ELEMENTO(DICIONARIO)
        for anime in json_data:
            for name in anime:
                print(f'{Fore.BLUE}{Style.BRIGHT}{name}{Style.RESET_ALL}')


def check_anime():
    anime_check = input('>>> Which anime you want to check? ')
    anime_check = anime_check.strip()

    verif_anime = False

    with open('anime.json', 'r+') as anime_json:
        json_data = json.load(anime_json)
        # ABRINDO A LISTA DA CHAVE ANIME
        for anime in json_data:
            # PEGANDO A CHAVE DE CADA DICIONARIO, QUE É O NOME DO ANIME
            for name in anime:
                if name.lower() == anime_check.lower():
                    verif_anime = True

                    for i in range(0, len(anime[name])):
                        line = f"   Season: {anime[name][i]['season']} - Last Episode Released:" \
                               f" {anime[name][i]['last available episode']} - " \
                               f"Last episode you watched: {anime[name][i]['last watched episode']}"
                        print(line)

            if verif_anime is True:
                break
        if verif_anime is False:
            print(f'Anime {anime_check} is not in your list')


def add_to_list():
    verif_site = False
    verif_list = False

    anime_add = input('>>> Inform the anime you want to be tracked: ')
    anime_add = anime_add.strip()

    with open('anime.json', 'r+') as anime_json:

        json_data = json.load(anime_json)

        for anime in json_data:
            for name in anime:
                if anime_add.lower() == name.lower():
                    print('Anime already on the list!')
                    verif_list = True
                    break

    if verif_list is False:
        try:
            letter = anime_add[0]
        except IndexError:
            print('Invalid Anime')
        else:

            if str.isalpha(letter) is True:
                url = scraper.get('https://www.crunchyroll.com/pt-br/videos/anime/alpha',
                                  params={'group': letter.lower()})
            else:
                url = scraper.get('https://www.crunchyroll.com/pt-br/videos/anime/alpha', params={'group': 'numeric'})

            soup = BeautifulSoup(url.content, features='lxml')
            data = soup.find('ul', {'class': "landscape-grid"})
            data = data.find_all('li')

            for tag in data:
                anime_name = tag.div.a['title']
                if anime_name.lower() == anime_add.lower():
                    anime_add = anime_name
                    anime_url = ('https://www.crunchyroll.com' + tag.div.a['href'])
                    anime_url_s = scraper.get('https://www.crunchyroll.com' + tag.div.a['href'])

                    # CHECKING THE LAST EPISODE

                    soup = BeautifulSoup(anime_url_s.content, features='lxml')
                    data = soup.find('ul', {'class': "list-of-seasons cf"})
                    data_2 = data.find_all('li', {'class': "season small-margin-bottom"})

                    # MUDANÇA A PARTIR DAQUI!!

                    if len(data_2) == 0:
                        try:
                            episode_num = data.div.span.text.strip()
                            episode_title = data.div.p.text.strip()
                        except AttributeError:
                            pass
                        else:
                            dict_anime = {
                                anime_add: [{'season': '-', 'last available episode': episode_num + ' - ' + episode_title,
                                            'last watched episode': 'Episódio -', 'url': anime_url, 'season_id': 1}]}
                        finally:
                            with open('anime.json', 'r+') as anime_json:
                                json_data = json.load(anime_json)

                                json_data.append(dict_anime)

                                json_data.sort(key=alpha_sort)

                                anime_json.seek(0)

                                json.dump(json_data, anime_json, indent=2)

                            print(f'Anime {anime_add} is now being tracked!')
                            verif_site = True
                            break

                    elif len(data_2) > 0:

                        data = data_2
                        list_value = []
                        ordem = len(data_2) + 1

                        for tag_anime in data:
                            ordem = ordem - 1
                            sub_anime = tag_anime.a['title']

                            try:
                                episode_num = tag_anime.find('div').span.text.strip()
                                episode_title = tag_anime.find('div').p.text.strip()

                            except AttributeError:
                                episode_num = 'Episódio -'
                                episode_title = '-'
                            finally:
                                dict_value = {'season': sub_anime,
                                              'last available episode': episode_num + ' - ' + episode_title,
                                              'last watched episode': 'Episódio -', 'url': anime_url, 'season_id': ordem}

                                list_value.append(dict_value)
                                list_value.sort(key=lambda e: e['season_id'], reverse=True)

                        dict_anime = {anime_add: list_value}

                        with open('anime.json', 'r+') as anime_json:
                            json_data = json.load(anime_json)

                            json_data.append(dict_anime)

                            json_data.sort(key=alpha_sort)

                            anime_json.seek(0)

                            json.dump(json_data, anime_json, indent=2)

                        print(f'Anime {anime_add} is now being tracked!')
                        verif_site = True
                        break

            if verif_site is False:
                print(f'Anime {anime_add} is not on Crunchyroll')


def update_list():
    option_up = input('>>> Which anime do you want to update in your list? ')
    option_up = option_up.strip()

    verif_episode = False

    with open('anime.json', 'r+') as anime_json:
        json_data = json.load(anime_json)
        # ABRINDO A LISTA DA CHAVE ANIME
        for anime in json_data:
            # PEGANDO A CHAVE DE CADA DICIONARIO, QUE É O NOME DO ANIME
            for name in anime:
                if name.lower() == option_up.lower():
                    option_up = name
                    verif_episode = True

            if verif_episode is True:

                print(f'{option_up}:')
                for seasons in anime[option_up]:
                    print(f"{seasons['season']} - season ID: {seasons['season_id']}")

                print('')
                season_id = input('>>> Inform the season id of the season you want to update: ')

                try:
                    season_id = int(season_id)
                except ValueError:
                    print('Invalid ID')
                else:
                    verif_id = False

                    for seasons in anime[option_up]:
                        if season_id == seasons['season_id']:
                            anime_dict = seasons
                            verif_id = True
                            break

                    if verif_id is True:
                        try:
                            episode_update = input('>>> Inform the number of the last episode'
                                                   ' you watched from this anime: ')
                            episode_update_int = int(episode_update)
                        except ValueError:
                            print(f'>>> Invalid episode {episode_update}')
                        else:

                            a = (seasons['last available episode']).split(' ')
                            a = a[1]

                            if episode_update_int > int(a):
                                print(f'>>> Episode {episode_update} exceeds the last released episode')
                                break
                            else:
                                anime_dict_update = copy.deepcopy(anime_dict)
                                anime_dict_update['last watched episode'] = f'Episódio {episode_update}'

                                json_data.remove(anime)
                                anime[option_up].remove(anime_dict)
                                anime[option_up].append(anime_dict_update)
                                anime[option_up].sort(key=lambda e: e['season_id'], reverse=True)

                                json_data.append(anime)

                                json_data.sort(key=alpha_sort)

                                anime_json.seek(0)
                                json.dump(json_data, anime_json, indent=2)
                                anime_json.truncate()

                                print('Anime updated!')
                                break
                    else:
                        print('Invalid ID')
                        break
        if verif_episode is False:
            print(f'>>> Anime {option_up} is not in your list')


def delete_from_list():
    verif_del = False
    anime_del = input('>>>Inform the anime you want to stop tracking: ')
    anime_del = anime_del.strip()
    with open('anime.json', 'r+') as anime_json:
        json_data = json.load(anime_json)

        for anime in json_data:
            for name in anime:
                if name.lower() == anime_del.lower():
                    anime_dict = [i[name] for i in json_data if name in i]
                    anime_dict = {name: anime_dict[0]}

                    json_data.remove(anime_dict)

                    anime_json.seek(0)
                    json.dump(json_data, anime_json, indent=2)
                    anime_json.truncate()

                    print(f'Anime {name} deleted!')

                    verif_del = True
                    break
        if verif_del is False:
            print(f'Anime {anime_del} is not on your list')


def check_update_crunchy():
    url = scraper.get('https://www.crunchyroll.com/pt-br/videos/anime/updated')
    soup = BeautifulSoup(url.content, features='lxml')

    info = soup.find_all('a', {'itemprop': "url", 'token': "shows-portraits"})
    info_ep = []
    for tag in info[0: 15]:
        info_ep.append(tag.find('span', {'class': "series-data block ellipsis"}).text)
    print('These are the latest updated animes:')
    for i in range(0, 15):
        print(f" {Fore.MAGENTA}{info[i]['title']} => {info_ep[i].strip()}{Style.RESET_ALL}")


def check_alpha_crunchy():
    letter = input('>>> Type the letter or number you want to check: ')
    # IN CASE USER TYPES MORE THAN ONE LETTER:
    try:
        letter = letter[0]
    except IndexError:
        print('Invalid option')
    else:
        if str.isalpha(letter) is True:
            url = scraper.get('https://www.crunchyroll.com/pt-br/videos/anime/alpha', params={'group': letter.lower()})
        else:
            url = scraper.get('https://www.crunchyroll.com/pt-br/videos/anime/alpha', params={'group': 'numeric'})

        soup = BeautifulSoup(url.content, features='lxml')
        data = soup.find('ul', {'class': "landscape-grid"})
        data = data.find_all('li')

        for tag in data:
            print(tag.div.a['title'])


def get_out():
    global verif_sair
    verif_sair = True


def interface():
    global verif_sair
    while verif_sair is False:
        # - USER INTERFACE - #
        print('')
        print('Choose your option \n'
              '1 - Check your list \n'
              '2 - Check a specific anime in your list \n'
              '3 - Add Anime to your list \n'
              '4 - Update your last watched episodes \n'
              '5 - Delete Anime from your list \n'
              '6 - Check all updated animes from Crunchy \n'
              '7 - Check all anime from Crunchy alphabetically \n'
              '0 - Quit')

        try:
            option = input('>>> ')
            print('')
            if int(option) < 0 or int(option) > 6:
                raise Exception
        except Exception:
            print(f'>>> Invalid {option} option')
            print('')
        else:
            if option == '1':
                check_list()
            elif option == '2':
                check_anime()
            elif option == '3':
                add_to_list()
            elif option == '4':
                update_list()
            elif option == '5':
                delete_from_list()
            elif option == '6':
                check_update_crunchy()
            elif option == '7':
                check_alpha_crunchy()
            elif option == '0':
                get_out()
    else:
        exit()


# --------------------------------------------------------------------------------------------------- #
def check_update_continually():
    global verif_sair
    while True:
        url = scraper.get('https://www.crunchyroll.com/pt-br/videos/anime/updated')
        soup = BeautifulSoup(url.content, features='lxml')

        info = soup.find_all('a', {'itemprop': "url", 'token': "shows-portraits"})
        info_dict_url = {}
        info_dict_num = {}

        for tag in info[0: 15]:
            info_dict_url[tag['title']] = tag['href']
            info_dict_num[tag['title']] = tag.find('span', {'class': "series-data block ellipsis"}).text.strip()

        with open('anime.json', 'r+') as anime_json:
            json_data = json.load(anime_json)

            for anime in json_data:
                for name in anime:
                    if name in info_dict_url:
                        last_watched = anime[name][0]['last watched episode'].split(' ')

                        last_watched = last_watched[1]
                        last_released = info_dict_num[name].split(' ')[1]

                        verif_episode = False

                        try:
                            if int(last_watched) != int(last_released):
                                verif_episode = True

                        except ValueError:
                            verif_episode = True

                        finally:
                            if verif_episode is True:
                                url = scraper.get('https://www.crunchyroll.com' + info_dict_url[name])
                                soup = BeautifulSoup(url.content, 'lxml')
                                data = soup.find('ul', {'class': "list-of-seasons cf"})

                                episode_num = data.div.span.text.strip()
                                episode_title = data.div.p.text.strip()

                                print(f'{Fore.BLUE}{Style.BRIGHT}{episode_num}-{episode_title}{Style.NORMAL} of '
                                      f'{Fore.YELLOW}{Style.BRIGHT}{name}{Style.NORMAL}{Fore.BLUE}'
                                      f' is available now!!{Style.RESET_ALL}')

        with open('anime.json', 'r+') as anime_json:
            json_data = json.load(anime_json)
            # dictionaries
            for animes in json_data:
                # keys
                for anime in animes:
                    anime_url = animes[anime][0]["url"]
                    url = scraper.get(anime_url)
                    soup = BeautifulSoup(url.content, features='lxml')

                    data = soup.find('ul', {'class': "list-of-seasons cf"})
                    data_2 = data.find_all('li', {'class': "season small-margin-bottom"})
                    data = data_2

                    ordem = len(data) + 1
                    list_value = []

                    for tag in data:
                        ordem = ordem - 1
                        sub_anime = tag.a['title']

                        try:
                            episode_num = tag.find('div').span.text.strip()
                            episode_title = tag.find('div').p.text.strip()
                        except AttributeError:
                            episode_num = 'Episódio -'
                            episode_title = '-'
                        finally:
                            dict_value = {'season': sub_anime,
                                          'last available episode': episode_num + ' - ' + episode_title,
                                          'last watched episode': 'Episódio -', 'url': anime_url, 'season_id': ordem}

                            list_value.append(dict_value)
                            list_value.sort(key=lambda e: e['season_id'], reverse=True)

                    if animes[anime] == list_value:
                        pass
                    else:
                        for season in animes[anime]:
                            season_site = list(filter(lambda e: e['season'] == season['season'], list_value))
                            season_site = season_site[0]

                            season['last available episode'] = season_site['last available episode']
                            season['season_id'] = season_site['season_id']
                            list_value.remove(season_site)

                        if list_value != 0:
                            for season in list_value:
                                animes[anime].append(season)

                    animes[anime].sort(key=lambda e: e['season_id'], reverse=True)

            anime_json.seek(0)
            json.dump(json_data, anime_json, indent=2)
            anime_json.truncate()

        for i in range(1, 1801):
            if verif_sair is False:
                time.sleep(1)
            elif verif_sair is True:
                exit(0)


threading.Thread(target=interface).start()
time.sleep(2)
threading.Thread(target=check_update_continually).start()
