from typing import Iterable

import requests


def get_overton_set(identifiers: Iterable[str], api_key: str) -> str:
	identifier_list = [identifier.strip() for identifier in identifiers if identifier and identifier.strip()]
	if not identifier_list:
		raise ValueError("'identifiers' must contain at least one non-empty value.")

	if not api_key or not api_key.strip():
		raise ValueError("'api_key' is required.")

	endpoint = "https://app.overton.io/generate_id_set.php?"
	params = {
		"api_key": api_key.strip(),
		"format": "json"
		}

	headers = {
		"Content-Type": "application/x-www-form-urlencoded",
	}

	payload = {
		"dois": "\n".join(identifier_list)
	}

	response = requests.post(endpoint, params=params, headers=headers, data=payload, timeout=30)
	response.raise_for_status()

	data = response.json()

	set_id = data.get("set")
	if not isinstance(set_id, str):
		raise ValueError("Unable to parse a set ID from Overton response.")

	return set_id

def get_overton_set_url(identifiers: Iterable[str], api_key: str) -> str:
    set_id = get_overton_set(identifiers, api_key)
    return f"https://app.overton.io/articles.php?identifiers={set_id}"