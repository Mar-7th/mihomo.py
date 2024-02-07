import asyncio

from mihomo import MihomoApi
from mihomo.model import Language


async def main():
    api = MihomoApi()

    # Set proxy if needed
    # api.set_proxy("http://127.0.0.1:7890")

    # Set i18n if needed, default is False
    # api.set_i18n(True)

    # Set language, default is Language.EN, only works when i18n is False
    api.set_language(Language.JP)

    # Set data path, default is `./data`
    api.set_data_path("data")

    # Set resource url, default is shown below
    # api.set_res_url("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/")

    # Set api url, default is shown below
    # api.set_api_url("https://api.mihomo.me/sr_info/")
    # Set as Enka
    # api.set_api_url("https://enka.network/api/hsr/uid/")

    # Ensure index files are downloaded
    # This may take a while
    # If it is not called, index files will be downloaded when needed
    # This will also check update of index files
    # Call this regularly to auto update the index files
    await api.ensure_index()

    # # The following shows how to get original api data
    # data_origin = await api.get_api_data("100114514")
    # if data_origin:
    #     print(data_origin.detailInfo)

    # This will return a FormattedApiInfo object
    data = await api.get_parsed_api_data("101797189")
    if data:
        print("Player UID:", data.player.uid)
        print("Player Nickname:", data.player.nickname)
        print("Player Level:", data.player.level)
        print("Characters:", [c.name for c in data.characters])

    # # The following shows how to save as json file
    import msgspec

    data_json = msgspec.json.encode(data).decode()

    with open("./result.json", "w") as f:
        f.write(data_json)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
