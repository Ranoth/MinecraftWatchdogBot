import asyncio


class TurnManager:
    _managers = {}
    _update_interval = 1.5
    _total_turns = 0  # Total number of monitors sending updates
    _current_turn = 0
    _can_send_updates = True

    def __init__(self):
        self.start_time = asyncio.get_event_loop().time()
        self.can_send_updates = True
        self.my_turn = True
        self.turn_number = self._total_turns
        TurnManager._managers[self.turn_number] = self
        TurnManager._total_turns = len(TurnManager._managers)

    @classmethod
    async def _update_current_turn(cls):
        """Update total turns and offset for turn management"""
        cls._can_send_updates = False
        cls._current_turn += 1
        if cls._current_turn >= cls._total_turns:
            cls._current_turn = 0
        cls._set_is_manager_turn()

        await asyncio.sleep(cls._update_interval)
        cls._can_send_updates = True

    @classmethod
    def _set_is_manager_turn(cls):
        """Set turn status for each manager"""
        for manager in cls._managers.values():
            if manager.turn_number == cls._current_turn:
                manager.my_turn = True
            else:
                manager.my_turn = False

    @classmethod
    def remove_manager(cls, manager):
        """Remove a manager from the turn management system"""
        if manager.turn_number in cls._managers:
            old_turn_number = manager.turn_number
            del cls._managers[manager.turn_number]

            # Reassign turn numbers sequentially
            new_managers = {}
            for idx, (_, m) in enumerate(sorted(cls._managers.items())):
                m.turn_number = idx
                new_managers[idx] = m

            cls._managers = new_managers
            cls._total_turns = len(cls._managers)

            # Adjust current turn if necessary
            if cls._total_turns == 0:
                cls._current_turn = 0
                cls._can_send_updates = True
            elif cls._current_turn >= cls._total_turns:
                cls._current_turn = 0
            # If we removed the manager that was before current turn, adjust
            elif old_turn_number < cls._current_turn:
                cls._current_turn -= 1

            # Update turn status for remaining managers
            cls._set_is_manager_turn()

