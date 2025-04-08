from aiogram.fsm.state import State, StatesGroup

class FSMAddGoal(StatesGroup):
    goal = State()

class FSMAddTask(StatesGroup):
    task = State()