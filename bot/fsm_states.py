from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    description = State()
    deadline = State()

class GoalStates(StatesGroup):
    waiting_for_goal_text = State()
