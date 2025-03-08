from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.base_controllers.controller import Controller
from abc import abstractmethod


class VagabondController(Controller):

    def _handle_faction_messages(self, msg: GameMessage):
        match msg.type:
            case GameMessages.CHOOSE_CHARACTER_MESSAGE:
                return self._handle_choose_character(msg)
            case GameMessages.VAGABOND_PLACEMENT_MESSAGE:
                return self._handle_vagabond_placement(msg)
            case GameMessages.RANGER_REPAIR_MESSAGE:
                return self._handle_ranger_repair(msg)
            case GameMessages.TINKER_CARD_MESSAGE:
                return self._handle_tinker_card(msg)
            case GameMessages.THIEF_STEAL_MESSAGE:
                return self._handle_thief_steal(msg)
            case GameMessages.SLIP_MESSAGE:
                return self._handle_slip_space(msg)
            case GameMessages.REFRESH_ITEM_MESSAGE:
                return self._handle_refresh_item(msg)
            case GameMessages.VAGABOND_MOVE_MESSAGE:
                return self._handle_vagabond_move(msg)
            case GameMessages.CHOOSE_QUEST_MESSAGE:
                return self._handle_choose_quest(msg)
            case GameMessages.QUEST_USE_ITEM_TRACK_MESSAGE:
                return self._handle_quest_use_item_track(msg)
            case GameMessages.CHOOSE_QUEST_REWARD_MESSAGE:
                return self._handle_choose_quest_reward(msg)
            case GameMessages.REPAIR_ITEM_MESSAGE:
                return self._handle_repair_item(msg)
            case GameMessages.EMPTY_SATCHEL_MESSAGE:
                return self._handle_empty_satchel(msg)
            case GameMessages.STRIKE_FACTION_CHOICE_MESSAGE:
                return self._handle_strike_faction_choice(msg)
            case GameMessages.STRIKE_PIECE_TARGETING_MESSAGE:
                return self._handle_strike_piece_targeting(msg)
            case GameMessages.AID_FACTION_CHOICE_MESSAGE:
                return self._handle_aid_faction_choice(msg)
            case GameMessages.AID_CARD_CHOICE_MESSAGE:
                return self._handle_aid_card_choice(msg)
            case GameMessages.AID_EXHAUST_ITEM_CHOICE_MESSAGE:
                return self._handle_aid_exhaust_item_choice(msg)
            case GameMessages.AID_TAKE_ITEM_CHOICE_MESSAGE:
                return self._handle_aid_take_item_choice(msg)
            case GameMessages.BATTLE_DAMAGE_ITEM_MESSAGE:
                return self._handle_battle_damage_item(msg)
            case GameMessages.COALITION_CHOICE_MESSAGE:
                return self._handle_coalition_choice(msg)
            case GameMessages.ALLY_MOVEMENT_MESSAGE:
                return self._handle_ally_movement(msg)
            case GameMessages.CHOOSE_ALLY_MESSAGE:
                return self._handle_choose_ally(msg)
            case GameMessages.ALLY_DAMAGE_SPLIT_MESSAGE:
                return self._handle_ally_damage_split(msg)
        return None

    @abstractmethod
    def _handle_choose_character(
        self, msg: ChooseCharacterMessage) -> ChooseCharacterResponse: ...

    @abstractmethod
    def _handle_vagabond_placement(
        self, msg: VagabondPlacementMessage) -> VagabondPlacementResponse: ...

    @abstractmethod
    def _handle_ranger_repair(
        self, msg: RangerRepairMessage) -> RangerRepairResponse: ...

    @abstractmethod
    def _handle_tinker_card(
        self, msg: TinkerCardMessage) -> TinkerCardResponse: ...

    @abstractmethod
    def _handle_thief_steal(
        self, msg: ThiefStealMessage) -> ThiefStealResponse: ...

    @abstractmethod
    def _handle_slip_space(self, msg: SlipMessage) -> SlipResponse: ...

    @abstractmethod
    def _handle_refresh_item(
        self, msg: RefreshItemMessage) -> RefreshItemResponse: ...

    @abstractmethod
    def _handle_vagabond_move(
        self, msg: VagabondMoveMessage) -> VagabondMoveResponse: ...

    @abstractmethod
    def _handle_choose_quest(
        self, msg: ChooseQuestMessage) -> ChooseQuestResponse: ...

    @abstractmethod
    def _handle_quest_use_item_track(
        self, msg: QuestUseItemTrackMessage) -> QuestUseItemTrackResponse: ...

    @abstractmethod
    def _handle_choose_quest_reward(
        self, msg: ChooseQuestRewardMessage) -> ChooseQuestRewardResponse: ...

    @abstractmethod
    def _handle_repair_item(
        self, msg: RepairItemMessage) -> RepairItemResponse: ...

    @abstractmethod
    def _handle_empty_satchel(
        self, msg: EmptySatchelMessage) -> EmptySatchelResponse: ...

    @abstractmethod
    def _handle_strike_faction_choice(
        self, msg: StrikeFactionChoiceMessage) -> StrikeFactionChoiceResponse: ...

    @abstractmethod
    def _handle_strike_piece_targeting(
        self, msg: StrikePieceTargetingMessage) -> StrikePieceTargetingResponse: ...

    @abstractmethod
    def _handle_aid_faction_choice(
        self, msg: AidFactionChoiceMessage) -> AidFactionChoiceResponse: ...

    @abstractmethod
    def _handle_aid_card_choice(
        self, msg: AidCardChoiceMessage) -> AidCardChoiceResponse: ...

    @abstractmethod
    def _handle_aid_exhaust_item_choice(
        self, msg: AidExhaustItemChoiceMessage) -> AidExhaustItemChoiceResponse: ...

    @abstractmethod
    def _handle_aid_take_item_choice(
        self, msg: AidTakeItemChoiceMessage) -> AidTakeItemChoiceResponse: ...

    @abstractmethod
    def _handle_battle_damage_item(
        self, msg: BattleDamageItemMessage) -> BattleDamageItemResponse: ...

    @abstractmethod
    def _handle_coalition_choice(
        self, msg: CoalitionChoiceMessage) -> CoalitionChoiceResponse: ...

    @abstractmethod
    def _handle_ally_movement(
        self, msg: AllyMovementMessage) -> AllyMovementResponse: ...

    @abstractmethod
    def _handle_choose_ally(
        self, msg: ChooseAllyMessage) -> ChooseAllyResponse: ...

    @abstractmethod
    def _handle_ally_damage_split(
        self, msg: AllyDamageSplitMessage) -> AllyDamageSplitResponse: ...
