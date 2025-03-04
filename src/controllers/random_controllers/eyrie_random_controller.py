from __future__ import annotations
from controllers.base_controllers.eyrie_dynasties_controller import EyrieDynastiesController
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from utils.root_types import Suits

from typing import TYPE_CHECKING, List

import random

if TYPE_CHECKING:
    from board.clearing import Clearing


class EyrieRandomController(EyrieDynastiesController):

    def __init__(self) -> None:
        """A dummy controller that chooses all its options randomly"""
        super().__init__()

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        msg.available_ambush_cards.append(None)
        return AmbushResponse(random.choice(msg.available_ambush_cards))

    def _handle_battle_end(self, msg: BattleEndMessage):
        return super()._handle_battle_end(msg)

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        return PieceTargetingResponse(random.sample(msg.targets, msg.remaining_dmg))

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:
        move_choice_idx = random.randint(0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            units = random.sample(
                all_units, random.randint(1, len(all_units)))
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        return CraftResponse(random.choice(msg.crafting_options))

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        return StandAndDeliverResponse(random.choice(msg.available_players))

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        return TaxCollectorResponse(random.choice(msg.available_units))

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        return CodebreakersResponse(random.choice(msg.available_players))

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        return ClaimDominanceCardResponse(random.choice(msg.available_discard_cards))

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        return ClaimDominanceSuitResponse(random.choice(msg.available_dominance_cards))

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        return ActionChoiceResponse(random.choice(msg.available_actions))

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(random.choice([True, False]))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(random.choice(msg.available_players))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(random.choice(msg.available_cards))

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingResponse:
        return BattleClearingResponse(random.choice(msg.available_clearings))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(random.choice(msg.battle_target_list))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(random.sample(msg.discard_options, msg.num_to_discard))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(random.choice(msg.valid_cards))

# Eyrie Controller

    def _handle_roostless_message(self, msg: RoostlessMessage) -> RoostlessResponse:
        return RoostlessResponse(random.choice(msg.available_clearings))

    def _handle_roost_setup_message(self, msg: RoostSetupMessage) -> RoostSetupResponse:
        return RoostSetupResponse(random.choice(msg.available_clearings))

    def _handle_leader_setup_message(self, msg: LeaderSetupMessage) -> LeaderSetupResponse:
        return LeaderSetupResponse(random.choice(msg.leader_choices))

    def _handle_decree_recruit_message(self, msg: DecreeRecruitClearingMessage) -> DecreeRecruitClearingResponse:
        return DecreeRecruitClearingResponse(random.choice(msg.available_clearings))

    def _handle_extend_decree_message_1(self, msg: ExtendDecreeMessage1) -> ExtendDecreeResponse1:
        return ExtendDecreeResponse1(random.choice(msg.available_cards), random.choice(msg.decree_types))

    def _handle_extend_decree_message_2(self, msg: ExtendDecreeMessage2) -> ExtendDecreeResponse2:
        return ExtendDecreeResponse2(random.choice(msg.available_cards), random.choice(msg.decree_types))

    def _handle_decree_build_message(self, msg: DecreeBuildMessage) -> DecreeBuildResponse:
        return DecreeBuildResponse(random.choice(msg.available_clearings))

    def _handle_turmoil_leader_message(self, msg: TurmoilLeaderMessage) -> TurmoilLeaderResponse:
        return TurmoilLeaderResponse(random.choice(msg.available_leaders))
