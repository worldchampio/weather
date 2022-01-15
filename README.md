# WEATHER

Written on and for Ubuntu using bash. To authenticate your requests to the Frost API, a client id is needed:

https://frost.met.no/auth/requestCredentials.html

The client id can then assigned in `src/weather.py` to `client_id`. (Don't upload it anywhere, store it locally). Currently, it is read from a `.txt` that must be placed in `src` and named `secret.txt`, and first line from the first character should be your client id.

## Quick start
```console
user@root:~$ git clone https://github.com/worldchampio/weather.git
user@root:~$ cd weather/src
user@root:~/src$ python3 -m venv env
user@root:~/src$ source env/bin/activate
(env) user@root:~/src$ pip install <packages listed below>
(env) user@root:~/src$ deactivate && cd ..
user@root:~/weather$ bash woo.sh
```

Manually installing `pillow`,`pandas`,`matplotlib` and `requests` should install all sub-dependencies.

## Dependencies
|Package           |Version    |
|------------------|-----------|
|certifi           | 2021.10.8 |
|charset-normalizer| 2.0.10    |
|cycler            | 0.11.0    |
|fonttools         | 4.28.5    |
|idna              | 3.3       |
|kiwisolver        | 1.3.2     |
|matplotlib        | 3.5.1     |
|numpy             | 1.22.0    |
|packaging         | 21.3      |
|pandas            | 1.3.5     |
|Pillow            | 9.0.0     |
|pip               | 20.0.2    |
|pkg-resources     | 0.0.0     |
|pyparsing         | 3.0.6     |
|python-dateutil   | 2.8.2     |
|pytz              | 2021.3    |
|requests          | 2.27.1    |
|setuptools        | 44.0.0    |
|six               | 1.16.0    |
|urllib3           | 1.26.8    |
