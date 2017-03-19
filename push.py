import requests


def push_link(title, body, url, access_token):
    data = {'type': 'link', 'title': title, 'body': body, 'url': url}
    headers = {'Access-Token': access_token}
    r = requests.post('https://api.pushbullet.com/v2/pushes', data=data,
                      headers=headers)
    return r


def get_access_token(filename):
    with open(filename) as f:
        token = f.readline().strip()
        if token:
            return token
    return None


if __name__ == "__main__":
    access_token = get_access_token('access_token')
    url = "https://raw.githubusercontent.com/diracdeltas/beatsbywatson/master/src/watson.jpg"
    if access_token:
        print(push_link('Change Your Mind', 'Fill out Mood Survey', url, access_token))
    else:
        print('No access token!')
