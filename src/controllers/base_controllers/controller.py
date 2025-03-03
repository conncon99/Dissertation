from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from abc import ABC, abstractmethod


class Controller(ABC):
    # Should have an assigned faction
    # Should know the game state
    # Should be prompted with certain types of decision making requests, e.g. daily actions, who to move, who to target in battle
    # Should then be able to view the action space for that decision and act accordingly

    def __init__(self) -> None:
        pass

    def send_game_message(self, msg: GameMessage) -> ControllerMessage:
        match msg.type:
            case GameMessages.AMBUSH_MESSAGE:
                return self._handle_ambushes(msg)
            case GameMessages.BATTLE_END_MESSAGE:
                return self._handle_battle_end(msg)
            case GameMessages.BATTLE_USE_CARD_MESSAGE:
                return self._handle_battle_card_message(msg)
            case GameMessages.PIECE_TARGETING_MESSAGE:
                return self._handle_piece_targeting(msg)
            case GameMessages.ACTION_CHOICE_MESSAGE:
                return self._handle_action_choice(msg)
            case GameMessages.BETTER_BURROW_BANK_MESSAGE:
                return self._handle_better_burrow_bank(msg)
            case GameMessages.CRAFT_MESSAGE:
                return self._handle_crafting(msg)
            case GameMessages.CHOOSE_DOMINANCE_MESSAGE:
                return self._handle_dominance_choice(msg)
            case GameMessages.BATTLE_CLEARING_CHOICE_MESSAGE:
                return self._handle_battle_clearing_choice(msg)
            case GameMessages.BATTLE_TARGET_CHOICE_MESSAGE:
                return self._handle_battle_target_choice(msg)
            case GameMessages.MOVE_MESSAGE:
                return self._handle_movement(msg)
            case GameMessages.DISCARD_CHOICE_MESSAGE:
                return self._handle_discard_choice(msg)
            case GameMessages.TRIGGERER_OUTRAGE_MESSAGE:
                return self._handle_triggerer_outrage_message(msg)
        return self._handle_faction_messages(msg)

    @abstractmethod
    def _handle_faction_messages(
        self, msg: GameMessage) -> ControllerMessage: ...

    @abstractmethod
    def _handle_battle_card_message(
        self, msg: BattleUseCardMessage) -> BattleUseCardResponse: ...

    @abstractmethod
    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse: ...

    @abstractmethod
    def _handle_battle_end(
        self, msg: BattleEndMessage) -> ControllerMessage: ...

    @abstractmethod
    def _handle_piece_targeting(
        self, msg: PieceTargetingMessage) -> PieceTargetingResponse: ...

    @abstractmethod
    def _handle_better_burrow_bank(
        self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse: ...

    @abstractmethod
    def _handle_movement(self, msg: MoveMessage) -> MoveResponse: ...

    @abstractmethod
    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse: ...

    @abstractmethod
    def _handle_dominance_choice(
        self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse: ...

    @abstractmethod
    def _handle_action_choice(
        self, msg: ActionChoiceMessage) -> ActionChoiceResponse: ...

    @abstractmethod
    def _handle_battle_clearing_choice(
        self, msg: BattleClearingChoiceMessage) -> BattleClearingResponse: ...

    @abstractmethod
    def _handle_battle_target_choice(
        self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse: ...

    @abstractmethod
    def _handle_discard_choice(
        self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse: ...

    @abstractmethod
    def _handle_triggerer_outrage_message(
        self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse: ...
