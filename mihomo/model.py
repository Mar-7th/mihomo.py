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


class SpaceChallengeData(Struct):
    scheduleMaxLevel: int = 0
    scheduleGroupId: int = 0
    noneScheduleMaxLevel: int = 0


class SpaceData(Struct):
    challengeInfo: Optional[SpaceChallengeData] = None
    maxRogueChallengeScore: int = 0
    equipmentCount: int = 0
    avatarCount: int = 0
    achievementCount: int = 0


class EquipmentData(Struct):
    tid: Optional[int] = None
    rank: int = 1
    level: int = 1
    promotion: int = 0


class SkillTreeData(Struct):
    pointId: int
    level: int = 0


class SubAffixData(Struct):
    affixId: int
    cnt: int = 0
    step: int = 0


class RelicData(Struct):
    tid: int
    mainAffixId: int
    type: int
    level: int = 0
    exp: int = 0
    subAffixList: List[SubAffixData] = []


class CharacterData(Struct):
    avatarId: int
    rank: int = 0
    level: int = 1
    promotion: int = 0
    equipment: Optional[EquipmentData] = None
    skillTreeList: List[SkillTreeData] = []
    relicList: List[RelicData] = []


class PlayerData(Struct):
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


class MihomoApiData(Struct):
    detailInfo: Optional[PlayerData] = None


class SpaceChallengeInfo(Struct):
    maze_group_id: int = 0
    maze_group_index: int = 0
    pre_maze_group_index: int = 0


class SpaceInfo(Struct):
    challenge_data: Optional[SpaceChallengeInfo] = None
    pass_area_progress: int = 0
    light_cone_count: int = 0
    avatar_count: int = 0
    achievement_count: int = 0


class PlayerInfo(Struct):
    uid: str
    nickname: str
    level: int = 0
    world_level: int = 0
    friend_count: int = 0
    avatar: Optional[AvatarInfo] = None
    signature: str = ""
    is_display: bool = False
    space_info: Optional[SpaceInfo] = None


class FormattedApiInfo(Struct):
    player: PlayerInfo
    characters: List[CharacterInfo] = []
