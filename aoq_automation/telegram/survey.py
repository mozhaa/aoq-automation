from dataclasses import dataclass
from functools import partial
from typing import *
from uuid import uuid1

from aiogram import F, Router
from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from aoq_automation.database.models import *

from .filterset import Filterset


class StateValue(Filter):
    def __init__(self, key: str, value: Any, default_value: Any = None) -> None:
        self.key = key
        self.value = value
        self.default_value = default_value

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        return await state.get_value(self.key, self.default_value) == self.value


class RouterBuilder:
    def as_routers(self) -> Tuple[Router, Router]: ...


@dataclass
class SurveyQuestion:
    """
    Question class for Survey.

    key - string, that will be used as a key for storing value in FSMContext
    after correct input

    filter - filter for correct input

    welcome_message - string with optional placeholder {key}

    invalidation_message - string with optional placeholders {key} and {response}

    keyboard_markup - optional ReplyKeyboardMarkup

    save - save answer into state or not
    """

    key: str
    filter: Filter
    welcome_message: str = "Enter value for {key}"
    invalidation_message: str = '"{response}" is invalid value for {key}, try again'
    keyboard_markup: Optional[ReplyKeyboardMarkup] = None
    save: bool = True


class Survey(RouterBuilder):
    def __init__(
        self,
        questions: List[SurveyQuestion],
        on_exit: CallbackType,
        on_cancel: Optional[CallbackType] = None,
        state: Optional[State] = None,
        enter_filter: Filter = Filterset([[]]),
        cancel_filter: Filter = Filterset([[F.text == "/cancel"]]),
    ) -> None:
        self.questions = questions

        # CallableObject, that will be called when last question will be answered
        self.on_exit = CallableObject(on_exit)

        # CallableObject, that will be called on triggering cancel_filters
        self.on_cancel = CallableObject(on_cancel)

        # State, that will be used during whole Survey
        self.state = state

        # Filter, that triggers this survey to start
        self.enter_filter = enter_filter

        # Filter, that triggers this survey to cancel in the middle
        self.cancel_filter = cancel_filter

        self.step_key = f"_survey_step_{uuid1()}"

    async def _send_welcome_message(self, message: Message, step: int) -> None:
        await message.answer(
            text=self.questions[step].welcome_message.format(
                key=self.questions[step].key
            ),
            reply_markup=self.questions[step].keyboard_markup or ReplyKeyboardRemove(),
        )

    async def _send_invalidation_message(self, message: Message, step: int) -> None:
        await message.reply(
            text=self.questions[step].invalidation_message.format(
                response=message.text, key=self.questions[step].key
            ),
            reply_markup=self.questions[step].keyboard_markup or ReplyKeyboardRemove(),
        )

    def as_routers(self) -> Tuple[Router, Router]:
        """
        Returns two routers: router that handles successful updates, and router for
        invalid updates. Second router (fr) should be chained to fallback_router
        in main module
        """

        r = Router()
        fr = Router()

        @r.message(StateValue(self.step_key, None), self.enter_filter)
        async def on_enter(message: Message, state: FSMContext) -> None:
            await self._send_welcome_message(message, 0)
            if self.state is not None:
                await state.set_state(self.state)
            await state.update_data({self.step_key: 0})

        @r.message(~StateValue(self.step_key, None), self.cancel_filter)
        async def on_cancel(message: Message, state: FSMContext) -> None:
            await self.on_cancel.call(message, state)

        async def on_correct_input(
            step: int, message: Message, state: FSMContext
        ) -> None:
            question = self.questions[step]
            if question.save:
                await state.update_data({question.key: message.text})
            if step == len(self.questions) - 1:
                await state.update_data({self.step_key: None})
                await self.on_exit.call(message, state)
            else:
                await state.update_data({self.step_key: step + 1})
                await self._send_welcome_message(message, step + 1)

        async def on_invalid_input(
            step: int, message: Message, state: FSMContext
        ) -> None:
            await self._send_invalidation_message(message, step)

        for step, question in enumerate(self.questions):
            # Step-dependant handlers
            r.message.register(
                partial(on_correct_input, step),
                StateValue(self.step_key, step),
                question.filter,
            )
            fr.message.register(
                partial(on_invalid_input, step), StateValue(self.step_key, step)
            )

        return r, fr

    def include_into(self, r: Router, fr: Router) -> None:
        nr, nfr = self.as_routers()
        r.include_router(nr)
        fr.include_router(nfr)
