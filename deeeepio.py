import httpx

class Client:
    def __init__(self, chromev: str = None):
        with httpx.Client() as client:
            init = client.get('https://apibeta.deeeep.io/auth/timezone')
            timezone = init.json()['t']

        decoded_array = [int(hex_pair, 16) for hex_pair in [timezone[i:i+2] for i in range(0, len(timezone), 2)]]
        decoded_string = []
        for hex_value in decoded_array:
            key_chars = [ord(char) for char in 'CSRFRDRDNKNK']
            result = hex_value
            for char_code in key_chars:
                result = result ^ char_code
            decoded_string.append(result)

        dinfo_schema = init.headers.get('Set-Cookie').split(';')[0].split('=')[1]
        twitch = ''.join([chr(dec_value) for dec_value in decoded_string])

        self.csrf_token = {'dinfo_schema': dinfo_schema, 'twitch': twitch}
        self.chromev = chromev

    def login(self, username, password):
        with httpx.Client() as client:
            try:
                response = client.post(
                    'https://apibeta.deeeep.io/auth/local/signin',
                    headers={'cookie': f'dinfo.schema={self.csrf_token["dinfo_schema"]}', 'Twitch': self.csrf_token.get('twitch')},
                    json={'email': username, 'password': password}
                )

                if response.status_code == 401:
                    raise Exception('Invalid credentials')

                elif str(response.status_code).startswith('2'):
                    self.chromev = response.json()['token']

                else:
                    raise Exception(response.json())

            except Exception as e:
                print(e)
                pass

    def send_friend_request(self, username):
        with httpx.Client() as client:
            try:
                if self.chromev is None:
                    print('Logging in is required for this operation')
                    return

                response = client.get(
                    f'https://apibeta.deeeep.io/users/u/{username}',
                    headers={'cookie': f'dinfo.schema={self.csrf_token["dinfo_schema"]}; CHROMEV={self.chromev}', 'Twitch': self.csrf_token.get('twitch')}
                )

                if response.status_code == 400:
                    raise Exception('Invalid username')

                elif str(response.status_code).startswith('2'):
                    response2 = client.post(
                        f'https://apibeta.deeeep.io/friendRequests/{response.json()["id"]}',
                        headers={'cookie': f'dinfo.schema={self.csrf_token["dinfo_schema"]}; CHROMEV={self.chromev}', 'Twitch': self.csrf_token.get('twitch')}
                    )

                    if not str(response2.status_code).startswith('2'):
                        if response2.json()['message'] == 'Friend request already sent':
                            raise Exception('Friend request already sent')
                        else:
                            raise Exception(response2.json())

                else:
                    raise Exception(response.json())

            except Exception as e:
                print(e)
                pass

    def user_info(self, username):
        with httpx.Client() as client:
            try:
                response = client.get(
                    f"https://apibeta.deeeep.io/users/u/{username}"
                )

                if str(response.status_code).startswith('2'):
                    user_profile = UserProfile(response.json())
                    return user_profile
                
                else:
                    raise Exception('Invalid Username')

            except Exception as e:
                print(e)
                pass

    def me(self):
        with httpx.Client() as client:
            try:
                if self.chromev is None:
                    print('Logging in is required for this operation')
                    return

                response = client.get(
                    'https://apibeta.deeeep.io/auth/me',
                    headers={'cookie': f'dinfo.schema={self.csrf_token["dinfo_schema"]}; CHROMEV={self.chromev}', 'Twitch': self.csrf_token.get('twitch')}
                )

                if str(response.status_code).startswith('2'):
                    user_profile = self.user_info(response.json()['user']['username'])
                    return user_profile

                else:
                    raise Exception('Invalid credentials')

            except Exception as e:
                print(e)
                pass

class UserProfile:
    def __init__(self, data):
        self.id = data.get("id")
        self.username = data.get("username")
        self.description = data.get("description")
        self.about = data.get("about")
        self.team_id = data.get("team_id")
        self.team_role = data.get("team_role")
        self.date_created = data.get("date_created")
        self.date_last_played = data.get("date_last_played")
        self.kill_count = data.get("kill_count")
        self.play_count = data.get("play_count")
        self.highest_score = data.get("highest_score")
        self.picture = data.get("picture")
        self.display_picture = data.get("displayPicture")
        self.active = data.get("active")
        self.is_friend = data.get("is_friend")
        self.ban_message = data.get("ban_message")
        self.coins = data.get("coins")
        self.tier = data.get("tier")
        self.xp = data.get("xp")
        self.migrated = data.get("migrated")
        self.verified = data.get("verified")
        self.beta = data.get("beta")
