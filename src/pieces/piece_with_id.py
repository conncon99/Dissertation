class PieceWithID:
    _next_ids = {}
    _free_ids = {}
    _instances = {}

    def __init__(self, piece_type: str):
        self.piece_type = piece_type
        # Initialize ID tracking for this piece type if not already done
        if piece_type not in PieceWithID._next_ids:
            PieceWithID._next_ids[piece_type] = 0
            PieceWithID._free_ids[piece_type] = []
            PieceWithID._instances[piece_type] = {}

        # Assign ID from the free list if available, otherwise use the next available ID
        if PieceWithID._free_ids[piece_type]:
            self.id = PieceWithID._free_ids[piece_type].pop(0)
        else:
            self.id = PieceWithID._next_ids[piece_type]
            PieceWithID._next_ids[piece_type] += 1

        # Store the instance in the dictionary
        PieceWithID._instances[piece_type][self.id] = self
        print(f" - Spawned '{piece_type}' with ID {self.id}")

    def destroy(self):
        print(f" - Destroying '{self.piece_type}' with ID {self.id}")
        # Remove the instance from the tracking dictionary
        if self.id in PieceWithID._instances[self.piece_type]:
            del PieceWithID._instances[self.piece_type][self.id]
        # Free the ID for reuse
        PieceWithID._free_ids[self.piece_type].append(self.id)
        PieceWithID._free_ids[self.piece_type].sort()

    @classmethod
    def get_by_id(cls, piece_type: str, piece_id: int):
        """Retrieve a piece instance by its type and ID."""
        return cls._instances.get(piece_type, {}).get(piece_id, None)

    @classmethod
    def reset_ids(cls):
        cls._next_ids.clear()
        cls._free_ids.clear()
        cls._instances.clear()
        print(" - Reset all piece IDs")
