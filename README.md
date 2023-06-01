# mihomo.py

## Introduction

This is a Python library for getting data from [mihomo.me](https://api.mihomo.me). It can also parse the data into a more readable format.

## Installation

```bash
pip install mihomo
```

## Usage

```python
import asyncio

from mihomo import MihomoApi
from mihomo.model import Language


async def main():
    api = MihomoApi()

    # # Set index file path, default is "data/index"
    # # Index files will be downloaded to this path
    # api.set_index_path("data/index")

    # # Set i18n if needed, default is False
    # api.set_i18n(True)

    # # Set proxy if needed
    # api.set_proxy("http://127.0.0.1:7890")

    # Set language, default is Language.EN
    api.set_language(Language.CN)

    # Ensure index files are downloaded
    # This may take a while
    # If it is not called, index files will be downloaded when needed
    await api.ensure_index()

    # # The following shows how to get original api data
    # data_origin = await api.get_api_data("100114514")
    # print(data_origin)

    # This will return a FormattedApiInfo object
    data = await api.get_parsed_api_data("100114514")
    print(data)

    # # The following shows how to export json text
    # import msgspec
    # data_json = msgspec.json.encode(data).decode()
    # print(data_json)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
