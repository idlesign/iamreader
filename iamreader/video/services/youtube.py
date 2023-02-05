import glob
import threading
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads, dumps
from pathlib import Path
from typing import Callable, Tuple
from urllib.parse import urlparse, parse_qs

import requests

from ...utils import LOG


class TokenCallbackServer(HTTPServer):

    def __init__(self, *args, response_hook: Callable, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.response_hook = response_hook

class TokenCallbackServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        success, data = self.server.response_hook(self.path)
        data = data.encode()

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', f'{len(data)}')
        self.end_headers()
        self.wfile.write(data)

        if success:
            self.wfile.flush()
            threading.Timer(3, self.server.shutdown).start()


class TokenFetcher:
    """This will fetch an OAuth 2 token.

    1. Go to https://console.cloud.google.com/apis/credentials
    2. Add OAuth 2.0 Client -- Web application
    3. Set 'http://localhost:8080' in 'Authorized redirect URIs'
    4. Download JSON config at Client's page to current working directory
    5. Run this fetcher

    Docs: https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps

    """

    def __init__(self):
        self.config = self.read_config()

    @classmethod
    def read_config(cls) -> dict:
        path_base = Path.cwd()
        path_source = None

        fname_tpl = 'client_secret_*.json'

        for fpath in glob.glob(fname_tpl, root_dir=path_base):
            path_source = path_base / fpath

        assert path_source, f'No OAuth 2 json config found (searched for "{fname_tpl}" files)'

        LOG.info(f"We'll try to use this config: {path_source}")

        with open(path_source) as f:
            config = loads(f.read())

        data = config['web']

        return data

    def run(self):
        config = self.config
        uri_redirect = config['redirect_uris'][0]

        assert 'localhost' in uri_redirect, f'We expect "localhost" to be used, but not "{uri_redirect}"'
        assert 'client_secret' in config, f'No "client_secret" found in configuration file'

        client_id = config['client_id']
        client_secret = config['client_secret']

        LOG.info(f'Expected redirect URI: {uri_redirect}')

        prepared_url = requests.Request('GET', config['auth_uri'], params={
            'redirect_uri': uri_redirect,
            'client_id': client_id,
            'scope': 'https://www.googleapis.com/auth/youtube',
            # https://www.googleapis.com/auth/youtube.readonly
            # https://www.googleapis.com/auth/youtube.upload
            'access_type': 'offline',
            'prompt': 'select_account',  # none
            'response_type': 'code',
            # 'include_granted_scopes': 'true',
        }).prepare().url

        LOG.info(f'OAuth code request URI: {prepared_url}')

        def response_hook(path: str) -> Tuple[bool, str]:
            LOG.info(f'Remote requested path: {path}')

            qs_parsed = parse_qs(urlparse(path).query)
            code = qs_parsed.get('code')

            if not code:
                return False, f'{datetime.now()}<br>Waiting for a remote request ...'

            code = code[0]

            LOG.info(f"Remote issued this code: {code}. Now we'll try to exchange it for token data.")

            response = requests.post(
                config['token_uri'],
                params={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': uri_redirect,
                },
                auth=(client_id, client_secret)
            )

            try:
                data = response.json()

                token_file = Path(f'client_token_{client_id}.json').absolute()
                dumped = dumps(data, indent=4)

                with open(f'{token_file}', 'w') as f:
                    f.write(dumped)

                msg_saved = f'Token config saved into: {token_file}'

                html = (
                    f'Access token:<br>'
                    f'<textarea rows="3" cols="150">{data["access_token"]}</textarea><hr>'
                    f'{msg_saved}<hr>'
                    f'<pre>{dumped}</pre>'
                )

                LOG.info(msg_saved)

                return True, html

            except Exception:
                msg = 'Error getting token for a given code.'
                LOG.exception(msg)
                return False, f'<b>{msg}</b><hr>{response.text}'

        LOG.info("We're launching your browser at a token issuing confirmation page ...")
        webbrowser.open(f'{prepared_url}')

        uri_parsed = urlparse(uri_redirect)
        address = (uri_parsed.hostname, uri_parsed.port)
        LOG.info(
            f"We're launching also your personal local webserver at {address} to get token data from a remote ...\n"
            "And we'll shut that server down as a token is received. Or you may kill it with CTRL+C."
        )

        httpd = TokenCallbackServer(address, TokenCallbackServerHandler, response_hook=response_hook)
        httpd.serve_forever()


class YoutubeService:

    @classmethod
    def publish(cls):
        fetcher = TokenFetcher()
        fetcher.run()
