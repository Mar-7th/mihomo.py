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
    language: Language = Language.EN
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
                            f"Download index {file} of {self.language} failed."
                        )
            self.index[self.language.value] = Index(
                self.index_path / self.language.value
            )
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
        if data.EquipmentID:
            light_cone = LightConeBasicInfo(
                id=str(data.EquipmentID.ID),
                rank=data.EquipmentID.Rank,
                level=data.EquipmentID.Level,
                promotion=data.EquipmentID.Promotion,
            )
        else:
            light_cone = None
        relics = []
        for relic in data.RelicList:
            sub_affix = []
            for affix in relic.RelicSubAffix:
                sub_affix.append(
                    SubAffixInfo(
                        id=str(affix.SubAffixID),
                        cnt=affix.Cnt,
                        step=affix.Step,
                    )
                )
            relic_data = RelicBasicInfo(
                id=str(relic.ID),
                level=relic.Level,
                main_affix_id=str(relic.MainAffixID),
                sub_affix_info=sub_affix,
            )
            relics.append(relic_data)
        skill_tree_levels = []
        for behavior in data.BehaviorList:
            skill_tree_levels.append(
                LevelInfo(
                    id=str(behavior.BehaviorID),
                    level=behavior.Level,
                )
            )
        character_basic = CharacterBasicInfo(
            id=str(data.AvatarID),
            rank=data.Rank,
            level=data.Level,
            promotion=data.Promotion,
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
        if not api_data:
            return None
        if not api_data.PlayerDetailInfo:
            return None
        if not language:
            language = self.language
        if self.language.value not in self.index:
            await self.ensure_index()
        avatar = self.index[language.value].avatars.get(
            str(api_data.PlayerDetailInfo.HeadIconID)
        )
        player_info = PlayerInfo(
            uid=str(api_data.PlayerDetailInfo.UID),
            nickname=api_data.PlayerDetailInfo.NickName,
            level=api_data.PlayerDetailInfo.Level,
            world_level=api_data.PlayerDetailInfo.WorldLevel,
            friend_count=api_data.PlayerDetailInfo.CurFriendCount,
            avatar=AvatarInfo(
                id=str(api_data.PlayerDetailInfo.HeadIconID),
                name=avatar.name if avatar else "",
                icon=avatar.icon if avatar else "",
            ),
            signature=api_data.PlayerDetailInfo.Signature,
            birthday=api_data.PlayerDetailInfo.Birthday,
            is_display=api_data.PlayerDetailInfo.IsDisplayAvatarList,
        )
        if api_data.PlayerDetailInfo.PlayerSpaceInfo:
            space_info = api_data.PlayerDetailInfo.PlayerSpaceInfo
            if space_info:
                if space_info.ChallengeData:
                    challenge_info = SpaceChallengeInfo(
                        maze_group_id=space_info.ChallengeData.MazeGroupID,
                        maze_group_index=space_info.ChallengeData.MazeGroupIndex,
                        pre_maze_group_index=space_info.ChallengeData.PreMazeGroupIndex,
                    )
                else:
                    challenge_info = None
                player_info.space_info = SpaceInfo(
                    challenge_data=challenge_info,
                    pass_area_progress=space_info.PassAreaProgress,
                    light_cone_count=space_info.LightConeCount,
                    avatar_count=space_info.AvatarCount,
                    achievement_count=space_info.AchievementCount,
                )
        character_ids = set()
        characters: List[CharacterInfo] = []
        if api_data.PlayerDetailInfo.AssistAvatar:
            character_info = self.character_parse(
                api_data.PlayerDetailInfo.AssistAvatar, language
            )
            if character_info:
                character_info.name = character_info.name.replace(
                    "{NICKNAME}", player_info.nickname
                )
                character_ids.add(character_info.id)
                characters.append(character_info)
        if api_data.PlayerDetailInfo.DisplayAvatarList:
            for character in api_data.PlayerDetailInfo.DisplayAvatarList:
                if str(character.AvatarID) in character_ids:
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
