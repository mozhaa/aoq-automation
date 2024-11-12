from aiogram.filters import Filter
from aiogram.types import Message, ReplyKeyboardMarkup
from typing import Dict, Any, List
from aiogram.fsm.context import FSMContext
from typing import Optional, Tuple
from aiogram.fsm.state import State
from aiogram import Router, F
from aiogram.dispatcher.event.handler import CallableObject, CallbackType


class StateValue(Filter):
    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        return await state.get_value(self.key, None) == self.value


class ValueInput:
    def __init__(
        self,
        key: str,
        on_exit: CallbackType,
        state: Optional[State] = None,
        enter_filters: List[List[Filter]] = [[]],
        validation_filters: List[List[Filter]] = [[]],
        enter_message: str = "Enter value for {key}",
        invalid_message: str = '"{response}" is invalid value for {key}, try again',
        keyboard_markup: Optional[ReplyKeyboardMarkup] = None,
    ) -> None:
        self.key = key
        self.on_exit = CallableObject(on_exit)
        self.state = state
        self.enter_filters = enter_filters
        self.validation_filters = validation_filters
        self.state_key = f"{self.key}_input_state"
        self.enter_message = enter_message
        self.invalid_message = invalid_message
        self.keyboard_markup = keyboard_markup

    def as_routers(self) -> Tuple[Router, Router]:
        """
        Returns two routers: router that handling successful updates, and router for invalid update
        Second router (fr) must be chained to fallback_router in main module
        """

        r = Router()
        fr = Router()

        async def on_enter(message: Message, state: FSMContext) -> None:
            await message.answer(
                text=self.enter_message.format(response=message.text, key=self.key),
                reply_markup=self.keyboard_markup,
            )
            if self.state is not None:
                await state.set_state(self.state)
            await state.update_data({self.state_key: True})

        for enter_filters_set in self.enter_filters:
            r.message.register(
                on_enter, StateValue(self.state_key, None), *enter_filters_set
            )

        async def on_correct_input(
            message: Message, state: FSMContext, **kwargs
        ) -> None:
            await state.update_data({self.state_key: None})
            await self.on_exit.call(message, state, **kwargs)

        for validation_filters_set in self.validation_filters:
            r.message.register(
                on_correct_input,
                StateValue(self.state_key, True),
                *validation_filters_set,
            )

        async def on_invalid_input(message: Message, state: FSMContext) -> None:
            await message.reply(
                text=self.invalid_message.format(response=message.text, key=self.key),
                reply_markup=self.keyboard_markup,
            )

        fr.message.register(on_invalid_input, StateValue(self.state_key, True))

        return r, fr
