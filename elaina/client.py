import json
import random
import re
from typing import Any, Dict, Optional, TYPE_CHECKING

import aiohttp

from .errors import HTTPException


JSON_URL = "https://raw.githubusercontent.com/PeterTADev/Elaina_ChatBot_API/main/main.json"
TRAILING_COMMA = re.compile(r",(?=\s*[\]}])")


class ElainaClient:
    """Represents a client that fetches utterances and answers data from
    the Elaina API.

    Note that all answers are fetched once during class initialization.
    If the remote git repository is updated during the instance's lifetime
    then you should call ``update()`` to load the changes.

    Parameters
    -----
    session: Optional[``aiohttp.ClientSession``]
        The session to perform data update. If not provided, a new session
        will be created for each update and closed automatically. If provided,
        you are responsible for closing it.
    """

    if TYPE_CHECKING:
        data: Dict[str, Any]
        _ready: bool
        _session: aiohttp.ClientSession

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        if session and not isinstance(session, aiohttp.ClientSession):
            raise TypeError(f"session must be aiohttp.ClientSession, not {session.__class__.__name__}")

        self.data = {}
        self._ready = False
        self._session = session

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        """The internal ``aiohttp.ClientSession`` to perform data update,
        or ``None`` if not provided during initialization.
        """
        return self._session

    @staticmethod
    async def __do_update(session: aiohttp.ClientSession) -> Dict[str, Any]:
        async with session.get(JSON_URL) as response:
            if response.status == 200:
                data = await response.text(encoding="utf-8")

                # Remove trailing commas
                data = TRAILING_COMMA.sub("", data)
                return json.loads(data)

            raise HTTPException(response.status)

    async def update(self) -> None:
        """This function is a coroutine

        Perform HTTP request to fetch the data.

        Raises
        -----
        ``HTTPException``
            The HTTP request failed somehow.
        """
        if self.session is None:
            async with aiohttp.ClientSession() as session:
                data = await self.__do_update(session)
        else:
            data = await self.__do_update(self.session)

        for category in data["data"]:
            answers = category["answers"]
            for utterance in category["utterances"]:
                self.data[utterance.casefold()] = answers

        self._ready = True

    async def get_answer(self, utterance: str) -> Optional[str]:
        """This function is a coroutine

        Generate a random answer for an utterance

        Parameters
        -----
        utterance: ``str``
            The utterance to get an answer for.

        Returns
        -----
        Optional[``str``]
            The answer for the given utterance, or ``None`` if no
            answer can be provided.
        """
        if not self._ready:
            await self.update()

        answers = self.data.get(utterance.casefold())
        if not answers:
            return

        return random.choice(answers)
