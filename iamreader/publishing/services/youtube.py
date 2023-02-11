import glob
import threading
import webbrowser
from datetime import datetime
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads, dumps
from os import fstat
from pathlib import Path
from typing import Callable, Tuple, List, Optional
from urllib.parse import urlparse, parse_qs

import requests

from .base import Service
from .. import ProjectConfig
from ...annotations import Annotations
from ...exceptions import ServiceException
from ...utils import LOG, PATH_OUT_VIDEO


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


def read_config(path_base: Path, *, fname_tpl: str) -> Tuple[Optional[Path], Optional[dict]]:
    path_source = None

    for fpath in glob.glob(fname_tpl, root_dir=path_base):
        path_source = path_base / fpath

    if not path_source:
        return None, None

    LOG.debug(f"We'll try to use this config: {path_source}")

    with open(path_source) as f:
        config = loads(f.read())

    return path_source, config


class TokenFetcher:
    """This will fetch an OAuth 2 token.

    1. Go to https://console.cloud.google.com/apis/credentials
    2. Add OAuth 2.0 Client -- Web application
    3. Set 'http://localhost:8080' in 'Authorized redirect URIs'
    4. Download JSON config at Client's page to current working directory
    5. Run this fetcher

    Docs: https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps

    """

    def __init__(self, work_path: Path):
        self._path = work_path

        fname_tpl = 'client_secret_*.json'
        _, config = read_config(work_path, fname_tpl=fname_tpl)

        if config is None:
            assert config, f'No OAuth 2 json config found (searched for "{fname_tpl}" files)'

        self.config = config['web']

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

                token_file = self._path / f'client_token_{client_id}.json'
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


class YoutubeService(Service):

    alias = 'youtube'

    file_ext = 'avi'

    def __init__(self, *, config: ProjectConfig, annotations: Annotations, path_resources: Path):
        super().__init__(config=config, annotations=annotations, path_resources=path_resources)
        self._token = self._get_token()
        self._session = requests.Session()

    def materialize_template(self, path_sources: Path = None) -> List[dict]:
        return super().materialize_template(path_sources=path_sources or PATH_OUT_VIDEO)

    def add_to_playlist(self, *, video: str, playlist: str):

        LOG.debug(f'{self}: add video {video} to playlist {playlist} ...')

        response = self._session.post(
            'https://www.googleapis.com/youtube/v3/playlistItems',
            params={'part': 'snippet'},
            json={
                'snippet': {
                    'playlistId': playlist, 'resourceId': {'kind': 'youtube#video', 'videoId': video}
                }
            },
            headers={'Authorization': f'Bearer {self._token}'}
        )
        print(response.status_code)
        print(response.text)

    def upload(self, item: dict) -> str:

        LOG.debug(f'{self}: upload video ...')

        def sanitize(val: str) -> str:
            return val.replace('<', '').replace('>', '')

        response = self._session.post(
            'https://www.googleapis.com/upload/youtube/v3/videos',
            params={'part': 'snippet,status'},
            data=dumps({
                'snippet': {
                    'title': sanitize(item['title']),  # 100 ch no <>
                    'description': sanitize(item['description']),  # 5000 bytes no <>
                    'tags': item['tags'],  # 500 ch
                    'categoryId': '22',  # 22 People & Blogs  27 Education
                    'defaultLanguage': 'RUS',
                },
                'status': {
                    'privacyStatus': 'private',  # private public unlisted
                    'selfDeclaredMadeForKids': False,
                    # 'license': 'youtube',
                    'publishAt': item['dt_pub']
                    # (only for private) 1994-11-05T08:15:30-05:00 / 1994-11-05T13:15:30Z
                }
            }),
            headers={
                'Authorization': f'Bearer {self._token}',
            },
        )

        LOG.debug(f'HTTP {self}: {response.status_code}:\n{dict(response.headers)}\n{response.text}')

        status = response.status_code

        if status == 401:
            # token mismatch
            LOG.debug(f'{self}: token seems stale')
            self._token = self._get_token(drop=True)
            return self.upload(item)

        if not response.ok:
            raise ServiceException(f'{self}: {status} {response.text}')

        with open(item['fpath'], 'rb') as f:

            upload_data_url = response.headers['Location']

            response = self._session.put(
                upload_data_url,
                data=f,
                headers={
                    'Authorization': f'Bearer {self._token}',
                    'X-Upload-Content-Type': 'video/*',
                    'X-Upload-Content-Length': f'{fstat(f.fileno()).st_size}'
                },
            )

            LOG.debug(f'HTTP {self}: {response.status_code}:\n{dict(response.headers)}\n{response.text}')

            if not response.ok:
                raise ServiceException(f'{self}: {status} {response.text}')

    def _get_token(self, *, drop: bool = False) -> str:

        LOG.debug(f'{self}: getting token ...')

        read = partial(read_config, self._path_resources, fname_tpl='client_token_*.json')

        cfg_path, config = read()

        if drop and cfg_path:
            cfg_path.unlink(missing_ok=True)
            cfg_path, config = read()

        if config is None:
            LOG.debug(f'{self}: running token fetcher ...')
            fetcher = TokenFetcher(self._path_resources)
            fetcher.run()

            return self._get_token()

        return config['access_token']

    def _publish_item(self, item: dict) -> bool:

        # quota 10000 a day -- upload 1600 -- to playlist 50 -- read 1

        video_id = self.upload(item)

        for playlist in item['tags']:
            self.add_to_playlist(video=video_id, playlist=playlist)

        return True
