from enum import Enum
from typing import List, Optional

from msgspec import Struct
from starrailres import AvatarInfo, CharacterInfo


class Language(str, Enum):
    EN = "en"
    CN = "cn"
    CHT = "cht"
    DE = "de"
    ES = "es"
    FR = "fr"
    ID = "id"
    JP = "jp"
    KR = "kr"
    PT = "pt"
    RU = "ru"
    TH = "th"
    VI = "vi"


class BaseData(Struct):
    def to_dict(self):
        result = {}
        for field in self.__struct_fields__:
            value = getattr(self, field)
            if hasattr(value, "to_dict"):
                result[field] = value.to_dict()
            elif isinstance(value, list) and all(hasattr(i, "to_dict") for i in value):
                result[field] = [i.to_dict() for i in value]
            else:
                result[field] = value
        return result


class SpaceChallengeData(BaseData):
    scheduleMaxLevel: int = 0
    scheduleGroupId: int = 0
    noneScheduleMaxLevel: int = 0


class SpaceData(BaseData):
    challengeInfo: Optional[SpaceChallengeData] = None
    maxRogueChallengeScore: int = 0
    equipmentCount: int = 0
    avatarCount: int = 0
    achievementCount: int = 0


class EquipmentData(BaseData):
    tid: Optional[int] = None
    rank: int = 1
    level: int = 1
    promotion: int = 0


class SkillTreeData(BaseData):
    pointId: int
    level: int = 0


class SubAffixData(BaseData):
    affixId: int
    cnt: int = 0
    step: int = 0


class RelicData(BaseData):
    tid: int
    mainAffixId: int
    type: int
    level: int = 0
    exp: int = 0
    subAffixList: List[SubAffixData] = []


class CharacterData(BaseData):
    avatarId: int
    rank: int = 0
    level: int = 1
    promotion: int = 0
    equipment: Optional[EquipmentData] = None
    skillTreeList: List[SkillTreeData] = []
    relicList: List[RelicData] = []


class PlayerData(BaseData):
    uid: int
    nickname: str
    level: int = 0
    worldLevel: int = 0
    friendCount: int = 0
    headIcon: int = 200001
    signature: str = ""
    isDisplayAvatar: bool = False
    recordInfo: Optional[SpaceData] = None
    assistAvatarDetail: Optional[CharacterData] = None
    avatarDetailList: List[CharacterData] = []


class MihomoApiData(BaseData):
    detailInfo: Optional[PlayerData] = None


class SpaceChallengeInfo(BaseData):
    maze_group_id: int = 0
    maze_group_index: int = 0
    pre_maze_group_index: int = 0


class SpaceInfo(BaseData):
    challenge_data: Optional[SpaceChallengeInfo] = None
    pass_area_progress: int = 0
    light_cone_count: int = 0
    avatar_count: int = 0
    achievement_count: int = 0


class PlayerInfo(BaseData):
    uid: str
    nickname: str
    level: int = 0
    world_level: int = 0
    friend_count: int = 0
    avatar: Optional[AvatarInfo] = None
    signature: str = ""
    is_display: bool = False
    space_info: Optional[SpaceInfo] = None


class FormattedApiInfo(BaseData):
    player: PlayerInfo
    characters: List[CharacterInfo] = []
