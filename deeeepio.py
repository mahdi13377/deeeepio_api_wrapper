import httpx

class Client:
    def __init__(self, csrf_token: dict = {'dinfo_schema': None, 'twitch': None}, chromev:str = None):
        self.csrf_token = {'dinfo_schema': csrf_token.get('dinfo_schema'), 'twitch': csrf_token.get('twitch')}
        self.chromev = chromev

    def login(self, username, password):
        with httpx.Client() as client:
            try:
                if self.csrf_token["dinfo_schema"] == None or self.csrf_token['twitch'] == None:
                    print('The CSRF token is required for this operation')
                    return
                
                response = client.post('https://apibeta.deeeep.io/auth/local/signin', headers={'cookie': f'dinfo.schema={self.csrf_token["dinfo_schema"]}','Twitch': self.csrf_token.get('twitch')}, json={'email': username, 'password': password})
                if response.status_code == 401:
                    raise InvalidCredentialsException
                
                elif response.status_code == 403:
                    raise InvalidCSRFTokenException

                elif str(response.status_code).startswith('2'):
                    self.chromev = response.json()['token']

                else:
                    raise Exception(response.json())

            except Exception as e:
                print(e)
                pass


class InvalidCSRFTokenException(Exception):
    def __init__(self, message=f'Invalid CSRF token'):
        self.message = message
        super().__init__(self.message)

class InvalidCredentialsException(Exception):
    def __init__(self, message='Invalid credentials'):
        self.message = message
        super().__init__(self.message)