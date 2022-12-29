# Создание профиля арендодателя

import re
from aiogram import types, Dispatcher 
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, filters
from handler.make_order import start_cr_order 


from keybord.rentier_keybord import * 
from sys_files.bot_creation import dp, bot
from database.bd import sql_check , sql_insert_rentie_profile
from handler.pass_house import new_rent_h , change_profile 
from handler.change_pass_house import my_rents
import database.bd as bd


# Проверка профиля и создание профиля

class Rentier (StatesGroup):
    name = State()
    telephone_number = State()
    its_rentier = State() #True & False


#@dp.message_handler (commands=['start'])
async def start_cmd (message: types.Message):
    keybord = await menu_keybord()
    await message.answer('Добро пожаловать в бот поиску квартир в Узбекистане🤖🇺🇿. По всем вопросам и пожеланиям пишите @flat_rent_admin', reply_markup= keybord)


#@dp.message_handler(filters.Text (equals='Сдать'))
async def rentier_profile_check (message: types.Message):
    try:
        check_id = (await sql_check(field = 'id_member', field_2 =',name', table='rentie', value = message.chat.id))
        flag = True 
        for check in check_id:
            if check[0]==message.chat.id:
                await message.answer(f'{check[1]}, чем могу помочь?', reply_markup = await create_change_show_keybord())
                flag = False
        if flag:
            await message.answer('Мы еще не знакомы. Давайте создадим ваш профиль')
            await message.answer('Введите ваше имя', reply_markup= ReplyKeyboardRemove())
            await Rentier.name.set()
    except:
        await message.answer('Мы еще не знакомы. Давайте создадим ваш профиль')
        await message.answer('Введите ваше имя', reply_markup= ReplyKeyboardRemove())
        await Rentier.name.set()


# @dp.message_handler (commands=['order'],state ="*")
# @dp.message_handler(filters.Text (equals='Снять'))
async def take_house (message: types.Message, state: FSMContext):
    await state.finish()
    await start_cr_order (message)


# ОТМЕНА - выход в самое начало 
# start/ menu - выход в самое начало 
# Назад  


#@dp.message_handler(filters.Text(equals="Отмена", ignore_case= True), state='*')
async def cancel_buttom(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('В главное меню', reply_markup= await menu_keybord())
    await start_cmd(message)


#@dp.message_handler(commands=[rent], state='*')
async def rent_buttom (message: types.Message, state:FSMContext):
    await state.finish()
    answer = await message.reply('Возвращаемся в меню сдачи жилья!')
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(answer.chat.id, answer.message_id)
    await rentier_profile_check (message)


# @dp.message_handler (filters.Text (equals='В главное меню'))
# @dp.message_handler (commands=['menu'], state='*')
async def back_to_menu (message: types.Message, state: FSMContext):
    await state.finish()
    answer = await message.reply('Возвращаемся в главное меню', reply_markup= await menu_keybord())
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.delete_message(answer.chat.id, answer.message_id)
    await start_cmd(message)
    

# @dp.message_handler(lambda messsage : messsage.text in ['Создать новое предложение', 'Изменить профиль', 'Показать мои предложения'])
async def new_rent(message:types.Message):
    # создать кнопку назад 
    if message.text == 'Создать новое предложение':
        await new_rent_h(message)
    elif message.text == 'Изменить профиль':
        await change_profile(message)
    elif message.text == 'Показать мои предложения':
        await my_rents(message)


# @dp.message_handler(state=Rentier.name)
async def rentier_name (message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data ['rentier_name'] = message.text
        data ['rentier_id'] = message.chat.id
    await message.answer('Отлично, введите ваш номер телефона')
    await Rentier.telephone_number.set()


# @dp.message_handler(state=Rentier.telephone_number)
async def rentier_telephone_number (message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data ['rentier_telephone_number'] = message.text
        data ['telegram_profile'] = '@' + str(message.from_user.username)
    inline_rentier_keybord = await rentier_yes_no_keybord()
    await message.answer('Последний вопрос, Вы риэлтор?\n(Внимание, не риэлтор может создавать не более 1 объявления)',reply_markup = inline_rentier_keybord)
    await Rentier.its_rentier.set()


# @dp.callback_query_handler(state=Rentier.its_rentier)
async def rentier_yes_no (callback_query: types.CallbackQuery, state: FSMContext):
    try:
        async with state.proxy() as data:
            data ['its_rentier'] = callback_query.data
        await bot.send_message(callback_query.from_user.id, 'Спасибо, ваш профиль создан')
        await sql_insert_rentie_profile (state=state)
        await state.finish()
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await rentier_profile_check (callback_query.message)
    except Exception as e:
        print(e)
        await bot.send_message(callback_query.from_user.id, 'Ошибка, попробуйте еще раз')
        await state.finish()
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await rentier_profile_check (callback_query.message)


def registr_handlers(dp:Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(rentier_profile_check, filters.Text (equals='Сдать'))
    dp.register_message_handler(take_house, commands=['order'], state='*')
    dp.register_message_handler (take_house, filters.Text (equals='Снять'), state='*')
    dp.register_message_handler(cancel_buttom, filters.Text(equals="Отмена", ignore_case= True), state='*')
    dp.register_message_handler(rent_buttom, commands=['rent'], state='*')
    dp.register_message_handler(back_to_menu, filters.Text (equals='В главное меню'))
    dp.register_message_handler(back_to_menu, commands=['menu'], state='*')
    dp.register_message_handler(new_rent, lambda messsage : messsage.text in ['Создать новое предложение', 'Изменить профиль', 'Показать мои предложения'])
    dp.register_message_handler(rentier_name, state=Rentier.name)
    dp.register_message_handler(rentier_telephone_number, state=Rentier.telephone_number)
    dp.register_callback_query_handler(rentier_yes_no, state=Rentier.its_rentier)
