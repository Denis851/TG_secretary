from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    waiting_for_task_text = State()

class GoalStates(StatesGroup):
    waiting_for_goal_text = State()
