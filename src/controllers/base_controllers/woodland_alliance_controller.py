from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.base_controllers.controller import Controller
from abc import abstractmethod


class AllianceController(Controller):

    def _handle_faction_messages(self, msg: GameMessage):
        match msg.type:
            case GameMessages.ALLIANCE_NO_BASE_MESSAGE:
                return self._handle_no_bases_message(msg)
            case GameMessages.MOBILIZE_MESSAGE:
                return self._handle_mobilize_message(msg)
            case GameMessages.TRAIN_MESSAGE:
                return self._handle_train_message(msg)
            case GameMessages.REVOLT_CLEARING_MESSAGE:
                return self._handle_revolt_clearing_message(msg)
            case GameMessages.REVOLT_DISCARD_MESSAGE:
                return self._handle_revolt_discard_message(msg)
            case GameMessages.SPREAD_SYMPATHY_CLEARING_MESSAGE:
                return self._handle_spread_sympathy_clearing_message(msg)
            case GameMessages.SPREAD_SYMPATHY_DISCARD_MESSAGE:
                return self._handle_spread_sympathy_discard_message(msg)
            case GameMessages.ALLIANCE_RECRUIT_MESSAGE:
                return self._handle_alliance_recruit_message(msg)
            case GameMessages.ORGANIZE_MESSAGE:
                return self._handle_organize_message(msg)
            case GameMessages.ALLIANCE_OUTRAGE_MESSAGE:
                return self._handle_alliance_outrage_message(msg)
        return None

    @abstractmethod
    def _handle_no_bases_message(
        self, msg: AllianceNoBaseMessage) -> AllianceNoBaseResponse: ...

    @abstractmethod
    def _handle_mobilize_message(
        self, msg: MobilizeMessage) -> MobilizeResponse: ...

    @abstractmethod
    def _handle_train_message(self, msg: TrainMessage) -> TrainResponse: ...

    @abstractmethod
    def _handle_revolt_clearing_message(
        self, msg: RevoltClearingMessage) -> RevoltClearingResponse: ...

    @abstractmethod
    def _handle_revolt_discard_message(
        self, msg: RevoltDiscardMessage) -> RevoltDiscardResponse: ...

    @abstractmethod
    def _handle_spread_sympathy_clearing_message(
        self, msg: SpreadSympathyClearingMessage) -> SpreadSympathyClearingResponse: ...

    @abstractmethod
    def _handle_spread_sympathy_discard_message(
        self, msg: SpreadSympathyDiscardMessage) -> SpreadSympathyDiscardResponse: ...

    @abstractmethod
    def _handle_alliance_recruit_message(
        self, msg: AllianceRecruitMessage) -> AllianceRecruitResponse: ...

    @abstractmethod
    def _handle_organize_message(
        self, msg: OrganizeMessage) -> OrganizeResponse: ...

    @abstractmethod
    def _handle_alliance_outrage_message(
        self, msg: AllianceOutrageMessage) -> AllianceOutrageResponse: ...
