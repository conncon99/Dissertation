from __future__ import annotations
from src.controllers.base_controllers.controller import Controller
from src.controllers.base_controllers.action_decoder import Decoder
from src.controllers.nn_controllers.observation_space_encoder import ObservationSpace
from gymnasium import spaces
from src.controllers.nn_controllers.mask import Mask
import numpy as np
from tianshou.data import Batch

import torch
import os
from typing import TYPE_CHECKING
from tianshou.utils.net.common import Net

if TYPE_CHECKING:
    from src.controllers.messages.game_messages import GameMessage


class NN_Controller(Controller):

    def __init__(self, faction_name):
        super().__init__()

        self.state_dim = 896
        self.action_dim = 340
        self.mask = Mask(self.action_dim)
        V_MIN, V_MAX, N_ATOMS = -10.0, 25.0, 340
        self.SUPPORT = torch.linspace(V_MIN, V_MAX, N_ATOMS)

        device = "cuda" if torch.cuda.is_available() else "cpu"

        model_path = f"log/root/rainbow/{faction_name}.pth"

        self.model = Net(
            state_shape=(self.state_dim,),
            action_shape=self.action_dim,
            hidden_sizes=[1024, 1024, 512],
            softmax=True,
            num_atoms=340,
            device=device,
        ).to(device)

        try:
            state_dict = torch.load(model_path, map_location=device)
            missing, unused = self.model.load_state_dict(
                state_dict, strict=False)
            if missing:
                print(f"[{faction_name}] checkpoint loaded "
                      f"(missing: {missing}, unused: {unused})")
            else:
                print(f"[{faction_name}] checkpoint loaded successfully")
        except Exception as err:
            print(f"[{faction_name}] could not load checkpoint - "
                  f"using random weights ({err})")
        else:
            print(f"[{faction_name}] no checkpoint found - network initialised")

        self.model.eval()
        self.mask = Mask()

    @torch.no_grad()
    def send_game_message(self, msg: GameMessage):
        # 1) flat observation tensor (1, 896)
        obs_vec = ObservationSpace.encode_game_state(
            msg.game_state, msg.type, msg.action_group
        ).clip(0, 1).astype(np.float32)

        obs_t = torch.from_numpy(obs_vec).unsqueeze(0).to(self.model.device)

        # 2) forward pass  -> logits shape (1, A, 60)
        logits, _ = self.model(obs_t)

        # if Net(softmax=True) already gave probabilities
        #   (depends on Tianshou version) check with a quick sum.
        probs = (
            logits if torch.allclose(logits.sum(-1), torch.ones_like(logits[..., 0]))
            else torch.softmax(logits, dim=-1)
        )

        # 3) expected Q for each action:  Σ p(z_i) * z_i
        support = self.SUPPORT.to(probs.device)
        q_values = torch.sum(probs * support, dim=-1).squeeze(0)   # (A,)

        # 4) mask out illegal actions
        mask = np.asarray(self.mask.create_mask(msg), dtype=bool)
        q_values[~torch.as_tensor(mask, device=q_values.device)] = -torch.inf

        action_id = int(torch.argmax(q_values).item())

        # 5) translate discrete id into a concrete game action
        return Decoder.decode(action_id, msg)

    # region Unimplemented Handlers

    def _handle_faction_messages(self, msg):
        raise NotImplementedError

    def _handle_battle_card_message(self, msg):
        raise NotImplementedError

    def _handle_ambushes(self, msg):
        raise NotImplementedError

    def _handle_tax_collector(self, msg):
        raise NotImplementedError

    def _handle_stand_and_deliver(self, msg):
        raise NotImplementedError

    def _handle_claim_dominance_suit(self, msg):
        raise NotImplementedError

    def _handle_claim_dominance_card(self, msg):
        raise NotImplementedError

    def _handle_codebreakers(self, msg):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg):
        raise NotImplementedError

    def _handle_better_burrow_bank(self, msg):
        raise NotImplementedError

    def _handle_move_from(self, msg):
        raise NotImplementedError

    def _handle_move_to(self, msg):
        raise NotImplementedError

    def _handle_move_units(self, msg):
        raise NotImplementedError

    def _handle_crafting(self, msg):
        raise NotImplementedError

    def _handle_dominance_choice(self, msg):
        raise NotImplementedError

    def _handle_action_choice(self, msg):
        raise NotImplementedError

    def _handle_battle_clearing_choice(self, msg):
        raise NotImplementedError

    def _handle_battle_target_choice(self, msg):
        raise NotImplementedError

    def _handle_discard_choice(self, msg):
        raise NotImplementedError

    def _handle_triggerer_outrage_message(self, msg):
        raise NotImplementedError

    # endregion


Marquise_NN_Controller = NN_Controller("marquise")
Eyrie_NN_Controller = NN_Controller("eyrie")
Alliance_NN_Controller = NN_Controller("woodland_alliance")
Vagabond_NN_Controller = NN_Controller("vagabond")
