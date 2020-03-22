# %%
import requests
from time import sleep
from csv import DictReader, DictWriter
from tqdm import tqdm

# %%
base_url = "https://nominatim.openstreetmap.org/search?"

params = {"format": "json", "q": "Eiffel Tower"}

# %%
result = requests.get(base_url, params=params)
result.status_code

# %%
result.json()[:2]

# %%
params = {"format": "json", "q": "Cair Paravel, Narnia", "limit": 1}

requests.get(base_url, params=params).json()

# %%


def nominatim_geocode(address, format="json", limit=1, **kwargs):
    """thin wrapper around nominatim API.

    Documentation: https://wiki.openstreetmap.org/wiki/Nominatim#Parameters
    """
    params = {"q": address, "format": format, "limit": limit, **kwargs}

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    sleep(1)
    return response.json()


# %%
nominatim_geocode("Eiffel Tower")

# %%
nominatim_geocode(
    address=None, street="221B Baker Street", city="London", country="Great Britain"
)

# %%
read_path = "data/cities.csv"
write_path = "data/my_cities.csv"

# %%


def read_csv(path):
    """read csv and return it as a list of dictionaries, one per row"""
    with open(path, "r") as f:
        return list(DictReader(f))


def write_csv(data, path, mode="w"):
    """write data to csv or append to existing one"""
    if mode not in "wa":
        raise ValueError("mode should be either 'w' or 'a'")

    with open(path, mode) as f:
        writer = DictWriter(f, fieldnames=data[0].keys())
        if mode == "w":
            writer.writeheader()

        for row in data:
            writer.writerow(row)


# %%
cities = read_csv(read_path)
cities[0]

# %%
write_csv(cities, write_path)

# %%


def geocode_bulk(data, column="address", verbose=False):
    """assuming data is an iterable of dicts,
    will attempt to geocode each, treating {column} as an address.
    Returns 2 iterables - result and errored rows"""
    result, errors = [], []

    for row in tqdm(data):
        try:
            search = nominatim_geocode(row[column], limit=1)
            if len(search) == 0:  # no location found
                result.append(row)
                if verbose:
                    print(f"Can't find anything for {row[column]}")

            else:
                info = search[0]  # most "important" result
                info.update(row)  # merge two dicts
                result.append(info)
        except Exception as e:
            if verbose:
                print(e)
            row["error"] = e
            errors.append(row)

    if len(errors) > 0 and verbose:
        print(f"{len(errors)}/{len(data)} rows failed")

    return result, errors


# %%
result, errors = geocode_bulk(cities, column="name", verbose=True)

# %%
result

# %%
errors

# %%