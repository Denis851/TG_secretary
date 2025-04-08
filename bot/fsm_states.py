from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    description = State()
    deadline = State()

class GoalStates(StatesGroup):
    name = State()
