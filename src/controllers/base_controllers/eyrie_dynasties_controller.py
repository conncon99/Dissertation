from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.base_controllers.controller import Controller
from abc import abstractmethod


class EyrieDynastiesController(Controller):

    def _handle_faction_messages(self, msg: GameMessage) -> ControllerMessage:
        match msg.type:
            case GameMessages.ROOSTLESS_MESSAGE:
                return self._handle_roostless_message(msg)
            case GameMessages.ROOST_SETUP_MESSAGE:
                return self._handle_roost_setup_message(msg)
            case GameMessages.LEADER_SETUP_MESSAGE:
                return self._handle_leader_setup_message(msg)
            case GameMessages.DECREE_RECRUIT_CLEARING_MESSAGE:
                return self._handle_decree_recruit_message(msg)
            case GameMessages.EXTEND_DECREE_MESSAGE_1:
                return self._handle_extend_decree_message_1(msg)
            case GameMessages.EXTEND_DECREE_MESSAGE_2:
                return self._handle_extend_decree_message_2(msg)
            case GameMessages.DECREE_BUILD_MESSAGE:
                return self._handle_decree_build_message(msg)
            case GameMessages.TURMOIL_LEADER_MESSAGE:
                return self._handle_turmoil_leader_message(msg)
        return None

    @abstractmethod
    def _handle_roostless_message(
        self, msg: RoostlessMessage) -> RoostlessResponse: ...

    @abstractmethod
    def _handle_roost_setup_message(
        self, msg: RoostSetupMessage) -> RoostSetupResponse: ...

    @abstractmethod
    def _handle_leader_setup_message(
        self, msg: LeaderSetupMessage) -> LeaderSetupResponse: ...

    @abstractmethod
    def _handle_decree_recruit_message(
        self, msg: DecreeRecruitClearingMessage) -> DecreeRecruitClearingResponse: ...

    @abstractmethod
    def _handle_extend_decree_message_1(
        self, msg: ExtendDecreeMessage1) -> ExtendDecreeResponse1: ...

    @abstractmethod
    def _handle_extend_decree_message_2(
        self, msg: ExtendDecreeMessage2) -> ExtendDecreeResponse2: ...

    @abstractmethod
    def _handle_decree_build_message(
        self, msg: DecreeBuildMessage) -> DecreeBuildResponse: ...

    @abstractmethod
    def _handle_turmoil_leader_message(
        self, msg: TurmoilLeaderMessage) -> TurmoilLeaderResponse: ...
