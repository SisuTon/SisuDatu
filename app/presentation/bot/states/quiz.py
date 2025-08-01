"""
FSM-состояния для квиза.
"""
from aiogram.fsm.state import State, StatesGroup

class QuizStates(StatesGroup):
    waiting_for_answer = State()
