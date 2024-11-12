from aiogram.filters import Filter
from aiogram.types import Message, ReplyKeyboardMarkup
from typing import Dict, Any, List
from aiogram.fsm.context import FSMContext
from typing import Optional, Tuple
from aiogram.fsm.state import State
from aiogram import Router, F
from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from aiogram.dispatcher.event.telegram import TelegramEventObserver
from dataclasses import dataclass
from functools import partial
from uuid import uuid1


class StateValue(Filter):
    def __init__(self, key: str, value: Any, default_value: Any = None) -> None:
        self.key = key
        self.value = value
        self.default_value = default_value

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        return await state.get_value(self.key, self.default_value) == self.value


class RouterBuilder:
    def as_routers(self) -> Tuple[Router, Router]: ...


class Filterset:
    """
    Set of filters in disjunctive normal form
    """

    def __init__(self, filters: List[List[Filter]]) -> None:
        self._table = filters

    def register(
        self,
        observer: TelegramEventObserver,
        callback: CallbackType,
        appendix: List[Filter] = [],
    ) -> None:
        for filter_set in self._table:
            observer.register(callback, *(appendix + filter_set))

    @property
    def empty(self) -> bool:
        return len(self._table) == 0


@dataclass
class SurveyQuestion:
    """
    Question class for Survey.

    key - string, that will be used as a key for storing value in FSMContext after correct input
    filters - filters in disjunctive normal form
    welcome_message - string with optional placeholder {key}
    invalidation_message - string with optional placeholders {key} and {response}
    keyboard_markup - optional ReplyKeyboardMarkup
    """

    key: str
    filterset: Filterset | List[List[Filter]]
    welcome_message: str = "Enter value for {key}"
    invalidation_message: str = '"{response}" is invalid value for {key}, try again'
    keyboard_markup: Optional[ReplyKeyboardMarkup] = None

    def __post_init__(self) -> None:
        if not isinstance(self.filterset, Filterset):
            self.filterset = Filterset(self.filterset)


class Survey(RouterBuilder):
    def __init__(
        self,
        questions: List[SurveyQuestion],
        on_exit: CallbackType,
        on_cancel: Optional[CallbackType] = None,
        state: Optional[State] = None,
        enter_filterset: Filterset | List[List[Filter]] = [[]],
        cancel_filterset: Filterset | List[List[Filter]] = [[F.text == "/cancel"]],
    ) -> None:
        self.questions = questions

        # CallableObject, that will be called when last question will be answered
        self.on_exit = CallableObject(on_exit)

        # CallableObject, that will be called on triggering cancel_filters
        self.on_cancel = CallableObject(on_cancel)

        # State, that will be used during whole Survey
        self.state = state

        # Filter set, that triggers this survey to start
        self.enter_filterset = (
            enter_filterset
            if isinstance(enter_filterset, Filterset)
            else Filterset(enter_filterset)
        )

        # Filter set, that triggers this survey to cancel in the middle
        self.cancel_filterset = (
            cancel_filterset
            if isinstance(cancel_filterset, Filterset)
            else Filterset(cancel_filterset)
        )

        if self.on_cancel is None and not self.cancel_filterset.empty():
            raise ValueError()
    
        self.step_key = f"_survey_step_{uuid1()}"

    async def _send_welcome_message(self, message: Message, step: int) -> None:
        await message.answer(
            text=self.questions[step].welcome_message.format(
                key=self.questions[step].key
            ),
            reply_markup=self.questions[step].keyboard_markup,
        )

    async def _send_invalidation_message(self, message: Message, step: int) -> None:
        await message.reply(
            text=self.questions[step].invalidation_message.format(
                response=message.text, key=self.questions[step].key
            ),
            reply_markup=self.questions[step].keyboard_markup,
        )

    def as_routers(self) -> Tuple[Router, Router]:
        """
        Returns two routers: router that handling successful updates, and router for invalid update
        Second router (fr) must be chained to fallback_router in main module
        """

        r = Router()
        fr = Router()

        async def on_enter(message: Message, state: FSMContext) -> None:
            await self._send_welcome_message(message, 0)
            if self.state is not None:
                await state.set_state(self.state)
            await state.update_data({self.step_key: 0})

        async def on_cancel(message: Message, state: FSMContext, **kwargs) -> None:
            await self.on_cancel.call(message, state, **kwargs)

        async def on_correct_input(
            step: int, message: Message, state: FSMContext, **kwargs
        ) -> None:
            await state.update_data({question.key: message.text})
            if step == len(self.questions) - 1:
                await state.update_data({self.step_key: None})
                await self.on_exit.call(message, state, **kwargs)
            else:
                await state.update_data({self.step_key: step + 1})
                await self._send_welcome_message(message, step + 1)

        async def on_invalid_input(
            step: int, message: Message, state: FSMContext
        ) -> None:
            await self._send_invalidation_message(message, step)

        self.enter_filterset.register(
            r.message, on_enter, [StateValue(self.step_key, None)]
        )

        self.cancel_filterset.register(
            r.message, on_cancel, [~StateValue(self.step_key, None)]
        )

        for step, question in enumerate(self.questions):
            # Step-dependant handlers

            question.filterset.register(
                r.message,
                partial(on_correct_input, step),
                [StateValue(self.step_key, step)],
            )

            fr.message.register(
                partial(on_invalid_input, step), StateValue(self.step_key, step)
            )

        return r, fr
