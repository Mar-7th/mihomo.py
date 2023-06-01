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
    MazeGroupID: int = 0
    MazeGroupIndex: int = 0
    PreMazeGroupIndex: int = 0


class SpaceData(BaseData):
    ChallengeData: Optional[SpaceChallengeData] = None
    PassAreaProgress: int = 0
    LightConeCount: int = 0
    AvatarCount: int = 0
    AchievementCount: int = 0


class EquipmentData(BaseData):
    ID: int
    Rank: int = 1
    Level: int = 1
    Promotion: int = 0


class BehaviorData(BaseData):
    BehaviorID: int
    Level: int = 0


class SubAffixData(BaseData):
    SubAffixID: int
    Cnt: int = 0
    Step: int = 0


class RelicData(BaseData):
    ID: int
    MainAffixID: int
    Type: int
    Level: int = 0
    EXP: int = 0
    RelicSubAffix: List[SubAffixData] = []


class CharacterData(BaseData):
    AvatarID: int
    Rank: int = 0
    Level: int = 1
    Promotion: int = 0
    EquipmentID: Optional[EquipmentData] = None
    BehaviorList: List[BehaviorData] = []
    RelicList: List[RelicData] = []


class PlayerData(BaseData):
    UID: int
    NickName: str
    Level: int = 0
    WorldLevel: int = 0
    CurFriendCount: int = 0
    HeadIconID: int = 200001
    Signature: str = ""
    Birthday: int = 0
    IsDisplayAvatarList: bool = False
    PlayerSpaceInfo: Optional[SpaceData] = None
    AssistAvatar: Optional[CharacterData] = None
    DisplayAvatarList: List[CharacterData] = []


class MihomoApiData(BaseData):
    PlayerDetailInfo: Optional[PlayerData] = None


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
    birthday: int = 0
    is_display: bool = False
    space_info: Optional[SpaceInfo] = None


class FormattedApiInfo(BaseData):
    player: PlayerInfo
    characters: List[CharacterInfo] = []
