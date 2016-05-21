from collections import namedtuple
from typing import Iterable, Callable, Dict, Set


class State:
    def __init__(self, name,
                 entry_action: Callable = None,
                 exit_action: Callable = None,
                 end_state: bool = False,
                 ):
        super().__init__()
        self.name = name
        self._entry_action = entry_action
        self._exit_action = exit_action
        self.is_end_state = end_state

    def do_entry(self):
        if self._entry_action:
            # noinspection PyCallingNonCallable,PyCallingNonCallable,PyCallingNonCallable
            self._entry_action()

    def do_exit(self):
        if self._exit_action:
            # noinspection PyCallingNonCallable,PyCallingNonCallable
            self._exit_action()

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return 'State object named {0}.'.format(self.name)


Event = str

Response = namedtuple('Response', 'next_state, action, guard_condition')


class StateMachine(State):
    def __init__(self,
                 event_source: Iterable[Event],
                 start_state: State = State('start'),
                 end_action: Callable = None
                 ):
        super().__init__()
        self._event_source = event_source
        self._current_state = start_state
        self._end_action = end_action
        self._states = {start_state}    # type: Set[State]
        self._state_table = {}  # type: Dict[Event, Dict[State, Response]]
        self._machine_data = {}  # data used by actions and event ignore functions

    def add_state(self, state: State):
        self._states.add(state)

    def add_event(self, event: Event):
        if event not in self._state_table:
            self._state_table[event] = {}   # Dict[State, Response]

    def add_table_entry(self, event: Event, state: State, response: Response):
        self.add_event(event)
        self.add_state(state)
        self._state_table[event][state] = response

    def run(self):
        for event, parameters in self._event_source:
            next_state, action, guard_condition = self._state_table.get(event).get(self._current_state)
            if action:
                if guard_condition and guard_condition():  # guard_condition function supplied which returns True
                    continue
                self._current_state.do_exit()
                self._current_state = next_state
                action(parameters)
                self._current_state.do_entry()
            if self._current_state.is_end_state:
                break
        if self._end_action:
            self._end_action()