from typing import List
from controllers.base_controllers.marquise_controller import MarquiseController
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from cards.cards import *


class MarquisePlayerController(MarquiseController):

    def _get_response(self, response_mapping) -> str:
        response = input(
            f"Enter option from {list(response_mapping.items())}: ").upper()
        while response not in response_mapping.keys():
            response = input(
                f"Enter option from {list(response_mapping.items())}: ").upper()
        return response

    def setup_mapping(self, options):
        def get_sort_key(item):
            # Try to get a valid numeric id
            item_id = getattr(item, 'id', None)
            if isinstance(item_id, (int, float)):
                return item_id

            # If no valid id, try to get a valid numeric index
            item_index = getattr(item, 'index', None)
            if isinstance(item_index, (int, float)):
                return item_index

            # If neither is valid, return None to indicate no sorting
            return None

        # Check if all items have a valid sort key (either id or index)
        all_keys_valid = all(get_sort_key(
            item) is not None for item in options)

        # Sort if all items have a valid key, otherwise keep the original order
        if all_keys_valid:
            options = sorted(options, key=get_sort_key)

        return {str(i): item for i, item in enumerate(options)}

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        print("Choose Ambush Card:")
        msg.available_ambush_cards.append(None)
        response_mapping = self.setup_mapping(msg.available_ambush_cards)
        return AmbushResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_end(self, msg: BattleEndMessage):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        print("Choose Piece to Destroy:")
        response_mapping = self.setup_mapping(msg.targets)
        return PieceTargetingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:

        print("Choose Move From Clearing:")
        from_clearings = set([move[0] for move in msg.available_moves])
        from_response_mapping = self.setup_mapping(from_clearings)
        from_clearing = from_response_mapping[self._get_response(
            from_response_mapping)]

        print("Choose Move To Clearing:")
        to_clearings = set([move[1]
                            for move in msg.available_moves if move[0] == from_clearing])
        to_response_mapping = self.setup_mapping(to_clearings)
        to_clearing = to_response_mapping[self._get_response(
            to_response_mapping)]

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break

        if len(all_units) == 1:
            units = all_units
        else:
            response = int(
                input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            while response < 0 or response > len(all_units):
                response = int(
                    input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            units = all_units[:response]
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        print("Choose Card to Craft:")
        response_mapping = self.setup_mapping(msg.crafting_options)
        return CraftResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        print("Choose Action to Take:")
        response_mapping = self.setup_mapping(msg.available_actions)
        return ActionChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        print("Choose Faction to Target:")
        response_mapping = self.setup_mapping(msg.available_players)
        return StandAndDeliverResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        print("Choose Unit to Remove:")
        response_mapping = self.setup_mapping(msg.available_units)
        return TaxCollectorResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        print("Choose Faction to Target:")
        response_mapping = self.setup_mapping(msg.available_players)
        return CodebreakersResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        print("Choose Card to Discard In exchange for Dominance:")
        response_mapping = self.setup_mapping(msg.available_discard_cards)
        return ClaimDominanceCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        print("Choose Dominance card to claim:")
        response_mapping = self.setup_mapping(msg.available_dominance_cards)
        return ClaimDominanceSuitResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        print("Choose Clearing to Battle On:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return BattleClearingChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        print("Choose whether to use a card in battle:")
        response_mapping = self.setup_mapping([True, False])
        return BattleUseCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        print("Choose other player to also draw card:")
        response_mapping = self.setup_mapping(msg.available_players)
        return BetterBurrowBankResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        print("Choose dominance to play:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return ChooseDominanceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        print("Choose target to battle:")
        response_mapping = self.setup_mapping(msg.battle_target_list)
        return BattleTargetResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        print("Choose card to discard:")
        response_mapping = self.setup_mapping(msg.discard_options)
        return DiscardChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        print("Choose card to give the Woodland Alliance:")
        response_mapping = self.setup_mapping(msg.valid_cards)
        return TriggererOutrageResponse(response_mapping[self._get_response(response_mapping)])

    # Marquise controller
    def _handle_keep_clearing_choice(self, msg: KeepClearingMessage) -> KeepClearingResponse:
        print("Choose Clearing to put Keep in:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return KeepClearingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_march_1_choice(self, msg: March1Message) -> March1Response:
        print("Choose Move From Clearing:")
        from_clearings = set([move[0] for move in msg.available_moves])
        from_response_mapping = self.setup_mapping(from_clearings)
        from_clearing = from_response_mapping[self._get_response(
            from_response_mapping)]

        print("Choose Move To Clearing:")
        to_clearings = set([move[1]
                            for move in msg.available_moves if move[0] == from_clearing])
        to_response_mapping = self.setup_mapping(to_clearings)
        to_clearing = to_response_mapping[self._get_response(
            to_response_mapping)]

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break

        if len(all_units) == 1:
            units = all_units
        else:
            response = int(
                input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            while response < 0 or response > len(all_units):
                response = int(
                    input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            units = all_units[:response]
        return March1Response(from_clearing, to_clearing, units)

    def _handle_march_2_choice(self, msg: March2Message) -> March2Response:
        print("Perform second march?")
        march_choice_mapping = self.setup_mapping([True, False])
        march_choice = march_choice_mapping[self._get_response(
            march_choice_mapping)]
        if not march_choice:
            print(" - Not performing second march movement")
            return March2Response(None, None, None)
        print("Choose Move From Clearing:")
        from_clearings = set([move[0] for move in msg.available_moves])
        from_response_mapping = self.setup_mapping(from_clearings)
        from_clearing = from_response_mapping[self._get_response(
            from_response_mapping)]
        print("Choose Move To Clearing:")
        to_clearings = set([move[1]
                            for move in msg.available_moves if move[0] == from_clearing])
        to_response_mapping = self.setup_mapping(to_clearings)
        to_clearing = to_response_mapping[self._get_response(
            to_response_mapping)]

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break

        if len(all_units) == 1:
            units = all_units
        else:
            response = int(
                input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            while response < 0 or response > len(all_units):
                response = int(
                    input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            units = all_units[:response]

        return March2Response(from_clearing, to_clearing, units)

    def _handle_overwork_choice(self, msg: OverworkMessage) -> OverworkResponse:
        print("Choose Clearing to Overwork Sawmill in:")
        clearing_response_mapping = self.setup_mapping(msg.available_clearings)
        chosen_clearing = clearing_response_mapping[self._get_response(
            clearing_response_mapping)]
        print("Choose Card to Discard:")
        discard_response_mapping = self.setup_mapping(
            [card for card in msg.hand if card.suit == Suits.BIRD or card.suit == chosen_clearing.get_suit()])
        chosen_discard = discard_response_mapping[self._get_response(
            discard_response_mapping)]
        return OverworkResponse(chosen_discard, chosen_clearing)

    def _handle_marquise_building_choice(self, msg: MarquiseBuildingMessage) -> MarquiseBuildingResponse:
        print("Choose clearing to build in:")
        clearing_response_mapping = self.setup_mapping(
            msg.clearing_building_options)
        clearing = clearing_response_mapping[self._get_response(
            clearing_response_mapping)]
        print("Choose Building Type to Build:")
        building_type_response_mapping = self.setup_mapping(
            msg.clearing_building_options[clearing])
        building_type = building_type_response_mapping[self._get_response(
            building_type_response_mapping)]
        return MarquiseBuildingResponse(clearing, building_type)

    def _handle_wood_removal_choice(self, msg: WoodRemovalMessage) -> WoodRemovalResponse:
        print("Choose Wood Token to remove:")
        response_mapping = self.setup_mapping(msg.wood_list)
        return WoodRemovalResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_marquise_building_setup_choice(self, msg: MarquiseBuildingSetupMessage) -> MarquiseBuildingSetupResponse:
        available_clearings: List[Clearing] = msg.available_clearings
        clearings_to_slots = {
            clearing: sum(1 for slot in clearing.slots if slot is None) for clearing in available_clearings}
        building_clearings = []  # Sawmill, Recruiter, Workshop
        building_names = ["Sawmill", "Recruiter", "Workshop"]
        for i in range(3):
            print(f"Choose Clearing to place {building_names[i]} in:")
            available_clearing_mappings = self.setup_mapping(
                available_clearings)
            building_clearing: Clearing = available_clearing_mappings[self._get_response(
                available_clearing_mappings)]
            clearings_to_slots[building_clearing] -= 1
            if clearings_to_slots[building_clearing] <= 0:
                available_clearings.remove(building_clearing)
            building_clearings.append(building_clearing)
        return MarquiseBuildingSetupResponse(sawmill_clearing=building_clearings[0], recruiter_clearing=building_clearings[1], workshop_clearing=building_clearings[2])

    def _handle_marquise_spend_bird_card_choice(self, msg: MarquiseSpendBirdCardMessage):
        print("Choose Bird Card to Discard:")
        response_mapping = self.setup_mapping(msg.bird_cards)
        return MarquiseSpendBirdCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_field_hospital_choice(self, msg: FieldHospitalMessage) -> FieldHospitalResponse:
        print("Choose Field Hospital Card to use:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return FieldHospitalResponse(response_mapping[self._get_response(response_mapping)])
