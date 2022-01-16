import time

import requests
import requests.adapters
import requests.packages.urllib3


def request(
    url: str,
    *,
    apikey: str = "",
    data: str = "",
    retries=6,
    session=None,
    timeout=30,
) -> dict:
    """Communicate with url and return response json dict. Handled
    retries, timeouts, and sticks to session if one is provided.

    Args:
        url (str): [description]
        apikey (str, optional): apikey to talk with url. Defaults to ''.
        data (str, optional): [description]. Defaults to None.
        retries (int, optional): [description]. Defaults to 6 tries.
        session ([type], optional): [description]. Defaults to None.
        timeout (int, optional): [description]. Defaults to 7 seconds.

    Raises:
        ValueError: Connection could not be established, check your
            values or internet connection to the target.

    Returns:
        dict: Response dictionary from url
    """

    if session:
        s = session
    else:
        s = requests.Session()
        # https://stackoverflow.com/a/35504626/8002464
        retries_adapter = requests.packages.urllib3.util.retry.Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retries_adapter)
        # register adapter for target
        s.mount("https://www.raidbots.com/", adapter)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Bloodmallet's shitty tool",
    }

    # post
    if data:
        body = {
            "advancedInput": data,
            "apiKey": apikey,
            "iterations": 100000,
            "reportName": "Bloodmallet's shitty tool",
            "simcVersion": "nightly",
            "type": "advanced",
        }

        response = s.post(url, json=body, headers=headers, timeout=timeout)

        while response.status_code == 429:
            time.sleep(10)
            response = s.post(url, json=body, headers=headers, timeout=timeout)

    # get
    else:
        response = s.get(url, headers=headers, timeout=timeout)

    # if unexpected status code returned, raise error
    response.raise_for_status()

    return dict(response.json())
