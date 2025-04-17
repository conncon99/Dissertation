from src.controllers.messages.game_messages import *
from src.controllers.messages.controller_messages import *
from src.controllers.base_controllers.controller import Controller
from abc import abstractmethod


class MarquiseController(Controller):

    def _handle_faction_messages(self, msg: GameMessage) -> ControllerMessage:
        match msg.type:
            case GameMessages.KEEP_CLEARING_MESSAGE:
                return self._handle_keep_clearing_choice(msg)
            case GameMessages.MARCH_AGAIN_MESSAGE:
                return self._handle_march_again(msg)
            case GameMessages.OVERWORK_CLEARING_MESSAGE:
                return self._handle_overwork_clearing(msg)
            case GameMessages.OVERWORK_DISCARD_MESSAGE:
                return self._handle_overwork_discard(msg)
            case GameMessages.MARQUISE_BUILDING_CLEARING_MESSAGE:
                return self._handle_marquise_building_clearing_choice(msg)
            case GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE:
                return self._handle_marquise_building_type_choice(msg)
            case GameMessages.WOOD_REMOVAL_MESSAGE:
                return self._handle_wood_removal_choice(msg)
            case GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE:
                return self._handle_marquise_setup_recruiter(msg)
            case GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE:
                return self._handle_marquise_setup_sawmill(msg)
            case GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE:
                return self._handle_marquise_setup_workshop(msg)
            case GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE:
                return self._handle_marquise_spend_bird_card_choice(msg)
            case GameMessages.FIELD_HOSPITAL_MESSAGE:
                return self._handle_field_hospital_choice(msg)
        raise TypeError(
            f"Invalid GameMessage Type {msg.type.name} for MarquiseController")

    @abstractmethod
    def _handle_keep_clearing_choice(
        self, msg: KeepClearingMessage) -> KeepClearingResponse: ...

    @abstractmethod
    def _handle_march_again(
        self, msg: MarchAgainMessage) -> MarchAgainResponse: ...

    @abstractmethod
    def _handle_overwork_clearing(
        self, msg: OverworkClearingMessage) -> OverworkClearingResponse: ...

    @abstractmethod
    def _handle_overwork_discard(
        self, msg: OverworkDiscardMessage) -> OverworkClearingResponse: ...

    @abstractmethod
    def _handle_marquise_building_clearing_choice(
        self, msg: MarquiseBuildingClearingMessage) -> MarquiseBuildingClearingResponse: ...

    @abstractmethod
    def _handle_marquise_building_type_choice(
        self, msg: MarquiseBuildingTypeMessage) -> MarquiseBuildingTypeResponse: ...

    @abstractmethod
    def _handle_wood_removal_choice(
        self, msg: WoodRemovalMessage) -> WoodRemovalResponse: ...

    @abstractmethod
    def _handle_marquise_setup_workshop(
        self, msg: MarquiseWorkshopSetupMessage) -> MarquiseWorkshopSetupResponse: ...

    @abstractmethod
    def _handle_marquise_setup_recruiter(
        self, msg: MarquiseRecruiterSetupMessage) -> MarquiseRecruiterSetupResponse: ...

    @abstractmethod
    def _handle_marquise_setup_sawmill(
        self, msg: MarquiseSawmillSetupMessage) -> MarquiseSawmillSetupResponse: ...

    @abstractmethod
    def _handle_marquise_spend_bird_card_choice(
        self, msg: MarquiseSpendBirdCardMessage) -> MarquiseSpendBirdCardResponse: ...

    @abstractmethod
    def _handle_field_hospital_choice(
        self, msg: FieldHospitalMessage) -> FieldHospitalResponse: ...
