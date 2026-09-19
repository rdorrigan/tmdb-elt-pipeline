import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.config import TMDB_API_TOKEN, TMDB_API_KEY, TMDB_BASE_URL

# (connect, read) timeouts in seconds, so a stalled connection can't hang the job.
REQUEST_TIMEOUT = (5, 30)


class TMDbClient:
    def __init__(self, api_token: str = TMDB_API_TOKEN, api_key: str = TMDB_API_KEY):
        self.api_token = api_token
        self.api_key = api_key
        self.base_url = TMDB_BASE_URL
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.headers.update({"Content-Type": "application/json"})
        assert any([x for x in [self.api_key, self.api_token]]), "API_KEY OR API_TOKEN ARE REQUIRED"
        if self.api_token:
            session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
            })
        else:
            session.params = {"api_key": self.api_key}

        return session

    def get_movie_details(self, movie_id: int) -> dict | None:
        """Fetch movie details including credits and keywords in 1 API call."""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "append_to_response": "credits,keywords"
        }
        response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()
