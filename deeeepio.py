import httpx

class Client:
    def __init__(self, chromev=None):
        self._initialize_session()
        self.chromev = chromev

    def _initialize_session(self):
        with httpx.Client() as client:
            init = client.get('https://apibeta.deeeep.io/auth/timezone')
            init.raise_for_status()

            timezone = init.json().get('t', '')

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

    def refresh_csrf_token(self):
        self._initialize_session()

    def _make_request(self, method, url, json=None, headers=None):
        with httpx.Client() as client:
            headers = headers or {}
            headers.update({
                'cookie': f'dinfo.schema={self.csrf_token["dinfo_schema"]}; CHROMEV={self.chromev}',
                'Twitch': self.csrf_token.get('twitch')
            })

            try:
                response = client.request(method, url, json=json, headers=headers)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                if response.json().get('message') != None:
                    raise APIException(f'{response.status_code}: {response.json().get("message")}')
                else:
                    match response.status_code:
                        case 401:
                            raise APIException('401: Unauthorized')
                        case 403:
                            raise APIException('403: Forbidden')
                        case 400:
                            raise APIException('400: Bad Request')
                        case 500:
                            raise APIException('500: Internal Server Error (most likely due to an invalid payload)')
                        case _:
                            raise APIException(str(e), e.response.json() if e.response else None)

    def login(self, username, password):
        response = self._make_request(
            'post',
            'https://apibeta.deeeep.io/auth/local/signin',
            json={'email': username, 'password': password}
        )

        self.chromev = response.json().get('token')

    def send_friend_request(self, username):
        if self.chromev is None:
            raise ClientException('Logging in is required for this operation.')

        response = self._make_request(
            'get',
            f'https://apibeta.deeeep.io/users/u/{username}'
        )

        self._make_request(
            'post',
            f'https://apibeta.deeeep.io/friendRequests/{response.json()["id"]}'
        )

    def get_friends_list(self, online: bool=False):
        if self.chromev is None:
            raise ClientException('Logging in is required for this operation.')

        response = self._make_request(
            'get',
            f'https://apibeta.deeeep.io/users/friends?online={str(online).lower()}'
        )

        users = [UserProfile(user) for user in response.json()]
        return users

    def remove_friend(self, username):
        if self.chromev is None:
            raise ClientException('Logging in is required for this operation.')

        response = self._make_request(
            'get',
            f'https://apibeta.deeeep.io/users/u/{username}'
        )

        self._make_request(
            'post',
            f'https://apibeta.deeeep.io/users/{response.json()["id"]}/unfriend'
        )

    def user_info(self, username):
        response = self._make_request(
            'get',  
            f'https://apibeta.deeeep.io/users/u/{username}?ref=profile'
        )

        user_profile = UserProfile(response.json())
        return user_profile

    def me(self):
        if self.chromev is None:
            raise ClientException('Logging in is required for this operation.')

        response = self._make_request(
            'get',
            'https://apibeta.deeeep.io/auth/me'
        )

        user_profile = UserProfile(response.json()['user'])
        return user_profile

    def update_self(self, username=None, death_message=None, about=None):
        if self.chromev is None:
            raise ClientException('Logging in is required for this operation.')
        
        json_payload = {}
        if username is not None:
            json_payload['username'] = username
        if death_message is not None:
            json_payload['description'] = death_message
        if about is not None:
            json_payload['about'] = about

        response = self._make_request(
            'put',
            'https://apibeta.deeeep.io/users/settings',
            json=json_payload
        )

        user_profile = self.user_info(response.json()['username'])
        return user_profile

class APIException(Exception):
    def __init__(self, message, response_json=None):
        super().__init__(message)
        self.response_json = response_json

class ClientException(Exception):
    def __init__(self, message):
        super().__init__(message)

class UserProfile:
    def __init__(self, data):
        self.id = data.get('id')
        self.username = data.get('username')
        self.description = data.get('description')
        self.about = data.get('about')
        self.team_id = data.get('team_id')
        self.team_role = data.get('team_role')
        self.date_created = data.get('date_created')
        self.date_last_played = data.get('date_last_played')
        self.profile_views = data.get('profile_views')
        self.kill_count = data.get('kill_count')
        self.play_count = data.get('play_count')
        self.highest_score = data.get('highest_score')
        self.picture = f'https://cdn.deeeep.io/uploads/avatars/{data.get("picture")}'
        self.display_picture = data.get('displayPicture')
        self.active = data.get('active')
        self.ban_message = data.get('ban_message')
        self.coins = data.get('coins')
        self.tier = data.get('tier')
        self.xp = data.get('xp')
        self.migrated = data.get('migrated')
        self.verified = data.get('verified')
        self.beta = data.get('beta')
        self.host = data.get('host')
