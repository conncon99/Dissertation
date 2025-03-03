from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.base_controllers.controller import Controller
from abc import abstractmethod


class MarquiseController(Controller):

    def _handle_faction_messages(self, msg: GameMessage) -> ControllerMessage:
        match msg.type:
            case GameMessages.KEEP_CLEARING_MESSAGE:
                return self._handle_keep_clearing_choice(msg)
            case GameMessages.OVERWORK_MESSAGE:
                return self._handle_overwork_choice(msg)
            case GameMessages.MARCH_1_MESSAGE:
                return self._handle_march_1_choice(msg)
            case GameMessages.MARCH_2_MESSAGE:
                return self._handle_march_2_choice(msg)
            case GameMessages.MARQUISE_BUILDING_MESSAGE:
                return self._handle_marquise_building_choice(msg)
            case GameMessages.WOOD_REMOVAL_MESSAGE:
                return self._handle_wood_removal_choice(msg)
            case GameMessages.MARQUISE_SETUP_BUILDINGS_MESSAGE:
                return self._handle_marquise_building_setup_choice(msg)
            case GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE:
                return self._handle_marquise_spend_bird_card_choice(msg)
            case GameMessages.FIELD_HOSPITAL_MESSAGE:
                return self._handle_field_hospital_choice(msg)
        return None

    @abstractmethod
    def _handle_keep_clearing_choice(
        self, msg: KeepClearingMessage) -> KeepClearingResponse: ...

    @abstractmethod
    def _handle_march_1_choice(self, msg: March1Message) -> March1Response: ...

    @abstractmethod
    def _handle_march_2_choice(self, msg: March2Message) -> March2Response: ...

    @abstractmethod
    def _handle_overwork_choice(
        self, msg: OverworkMessage) -> OverworkResponse: ...

    @abstractmethod
    def _handle_marquise_building_choice(
        self, msg: MarquiseBuildingMessage) -> MarquiseBuildingResponse: ...

    @abstractmethod
    def _handle_wood_removal_choice(
        self, msg: WoodRemovalMessage) -> WoodRemovalResponse: ...

    @abstractmethod
    def _handle_marquise_building_setup_choice(
        self, msg: MarquiseBuildingSetupMessage) -> MarquiseBuildingSetupResponse: ...

    @abstractmethod
    def _handle_marquise_spend_bird_card_choice(
        self, msg: MarquiseSpendBirdCardMessage) -> MarquiseSpendBirdCardResponse: ...

    @abstractmethod
    def _handle_field_hospital_choice(
        self, msg: FieldHospitalMessage) -> MarquiseBuildingResponse: ...
