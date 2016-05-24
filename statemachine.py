"""
    A full-featured framework for a Finite State Machine written in python.
    Inspired by "A Crash Course in UML State Machines" by Miro Samek, Quantum Leaps, LLC.
    https://classes.soe.ucsc.edu/cmpe013/Spring11/LectureNotes/A_Crash_Course_in_UML_State_Machines.pdf
"""
from typing import Iterable, Callable, Dict, Set, NamedTuple


Event = str
""" type alias:  Event is represented by a string """

Response = NamedTuple('Response',
                      [('next_state', 'State'), ('action', Callable[..., None]),
                       ('guard_condition', Callable[..., bool])])
"""
    action may optionally take parameters supplied with the event
    guard_condition should return False if the transition is to be disabled
"""


# noinspection PyCallingNonCallable
class State:
    """
    A State (an extended state) captures an aspect of the system's history
    and provides a context for the response of the system to events.
    """

    def __init__(self,
                 name: str,
                 entry_action: Callable = None,
                 exit_action: Callable = None,
                 end_state: bool = False,
                 ):
        super().__init__()
        self.name = name
        self._entry_action = entry_action
        self._exit_action = exit_action
        self.is_end_state = end_state
        self._responses = {}    # type: Dict[Event, Response]

    def add_response(self, event: Event, response: Response):
        self._responses[event] = response

    def handle_event(self, event: Event, *parameters) -> 'State':
        required_response = self._responses.get(event)
        if not required_response:
            return None
        next_state, action, guard_condition = required_response
        if guard_condition and not guard_condition():  # guard_condition function supplied which returns False
            return None
        if self._exit_action:
            self._exit_action()
        if action:
            action(event, parameters)
        next_state.do_entry()
        return next_state

    def do_entry(self):
        if self._entry_action:
            self._entry_action()

    def do_exit(self):
        if self._exit_action:
            self._exit_action()

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return 'State object named {0}.'.format(self.name)


# noinspection PyCallingNonCallable
class StateMachine(State):
    """
    An implementation of a FSM (Finite State Machine).
    """

    def __init__(self,
                 name: str,
                 event_source: Iterable[Event],
                 initial_state: State = State('initial'),
                 initial_action: Callable = None,
                 end_action: Callable = None
                 ):
        super().__init__(name)
        self._event_source = event_source
        self._current_state = initial_state
        self._initial_action = initial_action
        self._end_action = end_action
        self._states = {initial_state}  # type: Set[State]
        self._extended_state = {}  # data used by actions and event ignore functions
        self._started = False

    def register_state(self, state: State):
        self._states.add(state)

    def handle_event(self, event: Event, *parameters) -> 'State':
        if not self._started:
            if self._initial_action:
                self._initial_action()
            self._started = True
        self._current_state = self._current_state.handle_event(event, *parameters)
        if self._current_state.is_end_state and self._end_action:
            self._end_action()
        return self._current_state

    def __repr__(self):
        return 'Finite State Machine object named {0}.'.format(self.name)

