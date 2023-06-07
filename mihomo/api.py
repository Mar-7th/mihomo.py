from pathlib import Path
from typing import Dict, List, Optional

import httpx
from msgspec.json import decode
from starrailres import (
    CharacterBasicInfo,
    CharacterInfo,
    Index,
    LevelInfo,
    LightConeBasicInfo,
    RelicBasicInfo,
    SubAffixInfo,
)

from .model import (
    AvatarInfo,
    CharacterData,
    FormattedApiInfo,
    Language,
    MihomoApiData,
    PlayerInfo,
    SpaceChallengeInfo,
    SpaceInfo,
)

file_set = {
    "characters.json",
    "character_ranks.json",
    "character_skills.json",
    "character_skill_trees.json",
    "character_promotions.json",
    "light_cones.json",
    "light_cone_ranks.json",
    "light_cone_promotions.json",
    "relics.json",
    "relic_sets.json",
    "relic_main_affixes.json",
    "relic_sub_affixes.json",
    "paths.json",
    "elements.json",
    "properties.json",
    "avatars.json",
}


class MihomoApi:
    language = Language.EN
    i18n: bool = False
    index_path = Path.cwd() / "data" / "index"
    res_url = "https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/"
    api_url = "https://api.mihomo.me/sr_info/"
    proxy: Optional[str] = None
    index: Dict[str, Index] = {}

    def set_language(self, language: Language) -> None:
        self.language = language

    def set_i18n(self, i18n: bool) -> None:
        self.i18n = i18n

    def set_index_path(self, index_path: Path) -> None:
        self.index_path = index_path

    def set_res_url(self, res_url: str) -> None:
        self.res_url = res_url

    def set_api_url(self, api_url: str) -> None:
        self.api_url = api_url

    def set_proxy(self, proxy: Optional[str] = None) -> None:
        self.proxy = proxy

    async def ensure_index(self):
        if not self.i18n:
            for file in file_set:
                if not (self.index_path / self.language.value / file).exists():
                    if not (await self.download_index(file, self.language.value)):
                        raise Exception(
                            f"Download index {file} of {self.language.value} failed."
                        )
            self.index[self.language] = Index(self.index_path / self.language.value)
        else:
            for language in Language:
                for file in file_set:
                    if not (self.index_path / language.value / file).exists():
                        if not (await self.download_index(file, language.value)):
                            raise Exception(
                                f"Download index {file} of {language} failed."
                            )
                self.index[language.value] = Index(self.index_path / language.value)

    async def download_index(self, file: str, language: str) -> bool:
        url = self.res_url + "index_min/" + language + "/" + file
        response = await self.request(url)
        if not response:
            return False
        folder = Path(self.index_path / language)
        if not folder.exists():
            folder.mkdir(parents=True)
        with open(folder / file, "wb") as f:
            f.write(response.content)
        print(f"Succeed to download: {language} index {file}.")
        return True

    async def request(self, url):
        params = {}
        headers = {"User-Agent": "Mar-7th/mihomo.py"}
        if self.proxy:
            params["proxies"] = {"https": self.proxy, "http": self.proxy}
        params["headers"] = headers
        params["timeout"] = 10
        async with httpx.AsyncClient(**params) as client:
            try:
                response = await client.get(url)
            except:
                return None
            if response.status_code != 200:
                return None
            return response

    def character_parse(
        self, data: CharacterData, language: Optional[Language] = None
    ) -> Optional[CharacterInfo]:
        if data.equipment:
            light_cone = LightConeBasicInfo(
                id=str(data.equipment.tid),
                rank=data.equipment.rank,
                level=data.equipment.level,
                promotion=data.equipment.promotion,
            )
        else:
            light_cone = None
        relics = []
        for relic in data.relicList:
            sub_affix = []
            for affix in relic.subAffixList:
                sub_affix.append(
                    SubAffixInfo(
                        id=str(affix.affixId),
                        cnt=affix.cnt,
                        step=affix.step,
                    )
                )
            relic_data = RelicBasicInfo(
                id=str(relic.tid),
                level=relic.level,
                main_affix_id=str(relic.mainAffixId),
                sub_affix_info=sub_affix,
            )
            relics.append(relic_data)
        skill_tree_levels = []
        for behavior in data.skillTreeList:
            skill_tree_levels.append(
                LevelInfo(
                    id=str(behavior.pointId),
                    level=behavior.level,
                )
            )
        character_basic = CharacterBasicInfo(
            id=str(data.avatarId),
            rank=data.rank,
            level=data.level,
            promotion=data.promotion,
            skill_tree_levels=skill_tree_levels,
            light_cone=light_cone,
            relics=relics,
        )
        if not language:
            language = self.language
        character = self.index[language.value].get_character_info(character_basic)
        return character

    async def get_api_data(self, uid: str) -> Optional[MihomoApiData]:
        url = self.api_url + uid
        response = await self.request(url)
        if not response:
            return None
        try:
            data = response.content
        except:
            return None
        if not data:
            return None
        api_data = decode(data, type=MihomoApiData)
        return api_data

    async def get_parsed_api_data(
        self, uid: str, language: Optional[Language] = None
    ) -> Optional[FormattedApiInfo]:
        api_data = await self.get_api_data(uid)
        return await self.parse_api_data(api_data, language)

    async def parse_api_data(
        self, api_data: Optional[MihomoApiData], language: Optional[Language] = None
    ) -> Optional[FormattedApiInfo]:
        if not api_data:
            return None
        if not api_data.detailInfo:
            return None
        if not language:
            language = self.language
        if self.language not in self.index:
            await self.ensure_index()
        avatar = self.index[language.value].avatars.get(
            str(api_data.detailInfo.headIcon)
        )
        player_info = PlayerInfo(
            uid=str(api_data.detailInfo.uid),
            nickname=api_data.detailInfo.nickname,
            level=api_data.detailInfo.level,
            world_level=api_data.detailInfo.worldLevel,
            friend_count=api_data.detailInfo.friendCount,
            avatar=AvatarInfo(
                id=str(api_data.detailInfo.headIcon),
                name=avatar.name if avatar else "",
                icon=avatar.icon if avatar else "",
            ),
            signature=api_data.detailInfo.signature,
            is_display=api_data.detailInfo.isDisplayAvatar,
        )
        if api_data.detailInfo.recordInfo:
            space_info = api_data.detailInfo.recordInfo
            if space_info:
                if space_info.challengeInfo:
                    challenge_info = SpaceChallengeInfo(
                        maze_group_id=space_info.challengeInfo.scheduleGroupId,
                        maze_group_index=space_info.challengeInfo.scheduleMaxLevel,
                        pre_maze_group_index=space_info.challengeInfo.noneScheduleMaxLevel,
                    )
                else:
                    challenge_info = None
                player_info.space_info = SpaceInfo(
                    challenge_data=challenge_info,
                    pass_area_progress=space_info.maxRogueChallengeScore,
                    light_cone_count=space_info.equipmentCount,
                    avatar_count=space_info.avatarCount,
                    achievement_count=space_info.achievementCount,
                )
        character_ids = set()
        characters: List[CharacterInfo] = []
        if api_data.detailInfo.assistAvatarDetail:
            character_info = self.character_parse(
                api_data.detailInfo.assistAvatarDetail, language
            )
            if character_info:
                character_info.name = character_info.name.replace(
                    "{NICKNAME}", player_info.nickname
                )
                character_ids.add(character_info.id)
                characters.append(character_info)
        if api_data.detailInfo.avatarDetailList:
            for character in api_data.detailInfo.avatarDetailList:
                if str(character.avatarId) in character_ids:
                    continue
                character_info = self.character_parse(character, language)
                if character_info:
                    character_info.name = character_info.name.replace(
                        "{NICKNAME}", player_info.nickname
                    )
                    characters.append(character_info)
        formatted_api_info = FormattedApiInfo(
            player=player_info,
            characters=characters,
        )
        return formatted_api_info
