#Процесс сдачи жилья 


import asyncio
from typing import List, Union


from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
# from handler.rentier_profile import rentier_profile_check

import handler
from database.bd import sql_check, sql_insert_new_rent , sql_check_number_rents, sql_insert_photos
from sys_files.bot_creation import bot,dp
from keybord.rentier_keybord import back_button_reply, confirmation_keybord,type_of_house_keybord, rooms_keybord, district_keybord, rentier_yes_no_keybord




class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]



class New_rent (StatesGroup):
    type_of_house = State()
    rooms = State()
    price = State() 
    komission = State()
    district = State()
    type_repair = State()
    apartment_area = State()
    floor = State()
    floors_in_house = State()
    description = State()
    animals = State()
    kids = State()
    photo = State()
    confirmation = State()
    change = State()
    change_floor_st = State()
    change_floor_all_st = State()
    change_kids_st = State()
    change_animals_st = State()

list_of_bd = ['type_of_house', 'rooms','price', 'komission', 'district', 'type_repair', 'apartment_area', 'floor', 'floors_in_house', 'description', 'animals', 'kids', 'photo']

about_house_dict = {
    'type_of_house':{
        1:'Квартира', 2:'Комната', 3:'Дом'
    },
    'district':
    {     
    1:"Алмазарский район"  ,
    2:"Бектемирский район" ,
    3:"Мирабадский район"  , 
    4:'Мирзо-Улугбекский район' , 
    5:"Сергелийский район" , 
    6:"Чиланзарский район" ,
    7:"Шайхантаурский район" ,
    8:"Юнусабадский район" ,
    9:"Яккасарайский район" ,
    10:"Чиланзарский район",
    11:"Яшнабадский район" ,
    12:"Учтепинский район",
    13:'Загниатинский район'
    },

    'type_repair' : {
    1:'Бабушкин', 2:'Обычный', 3:'Евроремонт', 4:'Дизайнерский'
    },
    'true_false':{
        'True':'Можно', 'False':'Нельзя' , 'None' : 'Не важно'
    },
    'change_point':{
        "price": "Цена", 'komission' : 'Комиссия' , 'description' : 'Описание' , 'photo': 'Фото', 
        'rooms': "Количество комнат", "type_of_house": 'Тип жилья', "type_repair" : 'Тип ремонта',
        'district' : 'Район', 'apartment_area' : 'Площадь жилья', "floor" : 'Этаж', "floors_in_house" : "Этажей в доме",
        "kids" : "Можно с детьми", 'animals' : "Можно с животными"
    }, 
    'change_order':{
        "price": "Цена",'rooms': "Количество комнат","type_of_house": 'Тип жилья', "type_repair" : 'Тип ремонта',
        'district' : 'Район', 'apartment_area' : 'Площадь жилья', "floor" : 'Этаж' , 'animals_kids' : "Можно с детьми? Можно с животными?"
    }
}


async def new_rent_h(message:types.Message):   
    number_of_rents = (await sql_check_number_rents(id_member= message.chat.id))[0]
    its_rentie_check = (await sql_check (field="id_member", field_2= ', rieltor' ,value= message.chat.id, table= 'rentie' ))[0][1]
    if number_of_rents == 0:
        dot_msg = await bot.send_message (chat_id=message.chat.id, text = '.', reply_markup=ReplyKeyboardRemove())
        await bot.delete_message (chat_id=message.chat.id , message_id= dot_msg.message_id)
        await bot.send_message (chat_id=message.chat.id, text= 'Создаем новое предложение', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='Начнем', callback_data='start_new_rent')))
    elif number_of_rents >= 1:
        if its_rentie_check == True:
            dot_msg = await bot.send_message (chat_id=message.chat.id, text = '.', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message (chat_id=message.chat.id , message_id= dot_msg.message_id)            
            await bot.send_message (chat_id=message.chat.id, text= 'Создаем новое предложение', reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='Начнем', callback_data='start_new_rent')))
        else: 
            await bot.send_message (chat_id=message.chat.id, text = 'Размещать более одного объявления может только риелтор, Ваш статус Вы можете изменить нажав кнопку "Изменить профиль"')
            await handler.rentier_profile.rentier_profile_check (message)


async def change_profile(message:types.Message):
    profile = (await sql_check (field="id_member", field_2= ', name, telephone_number, rieltor, telegram_profile ' ,value= message.chat.id, table= 'rentie' ))[0]
    its_rieltor = profile[3]
    rieltor_w = 'Риелтор' if its_rieltor == True else 'Не риелтор '
    await bot.send_message (chat_id=message.chat.id, text= f'Ваш профиль \n\n{profile[1]} \n{profile[4]}\nID: {profile[0]} \nНомер телефона:{profile[2]}\n{rieltor_w}')
    await bot.send_message (chat_id=message.chat.id, text= 'Для изменения профиля отправьте сообщение в @flat_rent_admin и напишите, чтобы Вы хотели изменить и причину')
    #TODO: Выводится профиль пользователя


# @dp.callback_query_handler(filters.Text (equals='start_new_rent'))
async def type_of_house (callback_query: types.CallbackQuery , state:FSMContext):
    keybord = await type_of_house_keybord()
    await callback_query.message.edit_text (text='Выберите тип жилья', reply_markup= keybord)
    async with state.proxy() as rent_data:
        if 'changes' not in rent_data:
            rent_data['changes'] = 0
    await New_rent.type_of_house.set()


# @dp.callback_query_handler(state=New_rent.type_of_house)
async def rooms (callback_query: types.CallbackQuery, state:FSMContext):
    try:
        if callback_query.data ==  'back':
            async with state.proxy() as rent_data:

                if rent_data['changes'] == 1:
                    await show_rent (callback_query.message, state) 
                    return
            await new_rent_h(callback_query.message)
            await state.finish()
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            return
        async with state.proxy() as rent_data:
            if rent_data['changes'] == 1:
                del rent_data ['type_of_house']
            if 'type_of_house' not in rent_data:
                rent_data['type_of_house'] = int(callback_query.data)
        if len(rent_data) == 14: 
            if rent_data['changes'] != 2:
                await bot.send_message (chat_id=callback_query.message.chat.id, text='Запомнил!')
                await show_rent (callback_query.message, state)
                return
        async with state.proxy() as rent_data:
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            keybord = await rooms_keybord(10)
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id) 
            await bot.send_message (chat_id=callback_query.message.chat.id, text=f'{type_house}\n\nВыберите количество комнат', reply_markup= keybord)
            await New_rent.rooms.set()
    except AttributeError:
        callback_query.message = callback_query
        async with state.proxy() as rent_data:
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            keybord = await rooms_keybord(10)
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id) 
            await bot.send_message (chat_id=callback_query.message.chat.id, text=f'{type_house}\n\nВыберите количество комнат', reply_markup= keybord)
            await New_rent.rooms.set()


# @dp.callback_query_handler(state=New_rent.rooms)
async def price ( callback_query:types.CallbackQuery ,state:FSMContext):
    try:
        if callback_query.data == 'back':
            async with state.proxy() as rent_data:
                if rent_data['changes'] == 2:
                    await show_rent(callback_query.message, state) 
                    return
                else:
                    await type_of_house (callback_query, state)
                    return
        async with state.proxy() as rent_data:
            if rent_data['changes'] == 2:
                del rent_data ['rooms']
            if 'rooms'not in rent_data:
                rent_data['rooms'] = int(callback_query.data)
        if len(rent_data) == 14:
            if rent_data['changes'] ==2:
                await bot.send_message (chat_id=callback_query.message.chat.id, text='Запомнил!')
                await show_rent (callback_query.message, state)
                return
            else:
                type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
                await bot.send_message (chat_id=callback_query.message.chat.id, text=f'{type_house}\n\nВведите новую цену')
                await New_rent.price.set()
            return
        async with state.proxy() as rent_data:
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id) 
            await callback_query.message.answer (text=f'{type_house}\nКомнат: {rent_data["rooms"]}\n\nВведите цену в $', reply_markup= await  back_button_reply())
            await New_rent.price.set()            
    except AttributeError:
        callback_query.message = callback_query
        async with state.proxy() as rent_data:
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id) 
            await callback_query.message.answer (text=f'{type_house}\nКомнат: {rent_data["rooms"]}\n\nВведите цену в $', reply_markup= await  back_button_reply())
            await New_rent.price.set()  


# @dp.message_handler(state=New_rent.price)
async def komission (message:types.Message, state:FSMContext):
    if message.text == 'Назад':
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        async with state.proxy() as rent_data:
            if rent_data['changes'] == 6:
                await show_rent(message, state) 
                return
            del rent_data['rooms']
            await rooms(message, state=state)

    elif message.text.isnumeric():
        async with state.proxy() as rent_data:
            rent_data['price'] = int(message.text)
        if len(rent_data) == 14: 
            await bot.send_message (chat_id=message.chat.id, text='Запомнил!')
            await show_rent(message, state)
            return
        type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        its_rentie_check = (await sql_check (field="id_member", field_2= ', rieltor' ,value= message.chat.id, table= 'rentie' ))[0][1]
        if its_rentie_check == True:
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {message.text} $\n\nВведите комиссию в $', reply_markup= await  back_button_reply())
            await New_rent.komission.set()
        else:
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            with open ('map.png', 'rb') as media:
                await bot.send_photo (chat_id=message.chat.id , photo= media)
            await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {message.text} $\n\nВведите район', reply_markup= await district_keybord(about_house_dict['district'],back_data= 'back_to_price',back='◀️Назад'))
            async with state.proxy() as rent_data:
                rent_data ['komission'] = 0
            await New_rent.district.set()
    else:
        await message.reply('Напишите цифрами цену')


# @dp.message_handler(state=New_rent.komission)
async def house_district (message:types.Message, state:FSMContext, chat_id=None):
    async with state.proxy() as rent_data:

        if message == 'back_to_district':
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            with open ('map.png', 'rb') as media:
                await bot.send_photo (chat_id=chat_id , photo= media)
            await bot.send_message (chat_id=chat_id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\n\nВыберите район', reply_markup= await district_keybord(about_house_dict['district'],back_data= 'back_to_price',back='◀️Назад'))
            await New_rent.district.set()
        elif message.text == 'Назад':
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            await price (message, state)
            del rent_data['price']

        elif rent_data['changes'] == 3:
            with open ('map.png', 'rb') as media:
                type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
                await bot.send_photo (chat_id=chat_id , photo= media)
            await bot.send_message (chat_id=chat_id, text = f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\n\nВыберите район', reply_markup= await district_keybord(about_house_dict['district'],back_data= 'back_to_price',back='◀️Назад'))
            await New_rent.district.set()
        elif message.text.isnumeric():
            async with state.proxy() as rent_data:
                if 'komission' not in rent_data or rent_data['komission'] > 0 :
                    rent_data['komission'] = int(message.text)
            if len(rent_data) == 14:
                await bot.send_message (chat_id=message.chat.id, text="Записал")
                await show_rent(message, state)
                return
            chat_id = message.chat.id
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            with open ('map.png', 'rb') as media:
                await bot.send_photo (chat_id=chat_id , photo= media)
            await bot.send_message (chat_id=chat_id, text = f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\n\nВыберите район', reply_markup= await district_keybord(about_house_dict['district'],back_data= 'back_to_price',back='◀️Назад'))
            await New_rent.district.set()
        else:
            await message.reply('Напишите цифрами комиссию')


# @dp.callback_query_handler(state=New_rent.district)
async def type_repair (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as rent_data:
        try:
            if callback_query.data == 'back_to_price':
                if rent_data['changes'] == 3:
                    await show_rent(callback_query.message, state) 
                    return
                await price (callback_query, state)
                return
            elif rent_data['changes'] == 4:
                type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
                district = about_house_dict['district'][rent_data['district']]  
                await callback_query.message.edit_text (text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\n\nВыберите тип ремонта', reply_markup= await district_keybord(about_house_dict['type_repair'],back_data= 'back_to_district',back='◀️Назад'))
                await New_rent.type_repair.set()
                return

            elif rent_data['changes'] == 3:
                del rent_data['district']

            rent_data['district'] = int (callback_query.data)
            if len(rent_data) == 14:
                await bot.send_message (chat_id=callback_query.message.chat.id, text='Запомнил!')
                await show_rent(callback_query.message, state)
                return
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            district = about_house_dict['district'][rent_data['district']]
            await callback_query.message.delete()
            await callback_query.message.answer (text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\n\nВыберите тип ремонта', reply_markup= await district_keybord(about_house_dict['type_repair'],back_data= 'back_to_district',back='◀️Назад'))
            await New_rent.type_repair.set()
        except AttributeError:
            callback_query.message = callback_query
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            district = about_house_dict['district'][rent_data['district']]
            await callback_query.message.delete()
            await callback_query.message.answer (text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\n\nВыберите тип ремонта', reply_markup= await district_keybord(about_house_dict['type_repair'],back_data= 'back_to_district',back='◀️Назад'))
            await New_rent.type_repair.set()



# @dp.callback_query_handler(state=New_rent.type_repair)
async def house_area (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as rent_data:
        try:
            if callback_query.data == 'back_to_district':
                if rent_data['changes'] == 4:
                    await show_rent(callback_query.message, state) 
                    return 
                await house_district (message= callback_query.data , state = state, chat_id=callback_query.message.chat.id)
                return
            elif rent_data ['changes'] == 5:
                type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
                district = about_house_dict['district'][rent_data['district']]
                type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
                await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
                await bot.send_message (chat_id=callback_query.message.chat.id ,text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\n\nВведите площадь в м2')
                await New_rent.apartment_area.set()
                return

            elif rent_data['changes'] == 4:
                del rent_data['type_repair']

            rent_data['type_repair'] = int (callback_query.data)
            if len(rent_data) == 14:
                await bot.send_message (chat_id=callback_query.message.chat.id, text='Запомнил!')
                await show_rent(callback_query.message, state)
                return
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            district = about_house_dict['district'][rent_data['district']]
            type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
            keybord = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard= True)
            keybord.add('Пропустить', 'Назад')
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            await bot.send_message (chat_id=callback_query.message.chat.id ,text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\n\nВведите площадь в м2', reply_markup= keybord)
            await New_rent.apartment_area.set()

        except AttributeError:
            callback_query.message = callback_query
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            district = about_house_dict['district'][rent_data['district']]
            type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
            keybord = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard= True)
            keybord.add('Пропустить', 'Назад')
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            await bot.send_message (chat_id=callback_query.message.chat.id ,text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\n\nВведите площадь в м2', reply_markup= keybord)
            await New_rent.apartment_area.set()



# @dp.message_handler(state=New_rent.apartment_area)
async def floor (message:types.Message, state:FSMContext, callback_query:types.CallbackQuery = None, arg=None):
    if message.text == 'Назад':
        if arg != None:
            async with state.proxy() as rent_data:
                type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
                district = about_house_dict['district'][rent_data['district']]
                type_repair_ = about_house_dict['type_repair'][rent_data['type_repair']]
            await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair_}\nПлощадь: {rent_data["apartment_area"]} м2\n\nВведите этаж', reply_markup=await back_button_reply())
            await New_rent.floor.set()
        else:
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            async with state.proxy() as rent_data:
                if rent_data['changes'] == 5:
                    await show_rent(callback_query.message, state) 
                    return 
                await type_repair(message, state)
                del rent_data['type_repair'] 
    elif message.text == 'Пропустить':
        async with state.proxy() as rent_data:
            rent_data['apartment_area'] = 0 
        type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
        district = about_house_dict['district'][rent_data['district']]
        type_repair_ = about_house_dict['type_repair'][rent_data['type_repair']]
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        # await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair_}\n\nВведите этаж', reply_markup=await back_button_reply())   
        await New_rent.floor.set()
    elif message.text.isnumeric():
        async with state.proxy() as rent_data:
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            district = about_house_dict['district'][rent_data['district']]
            type_repair_ = about_house_dict['type_repair'][rent_data['type_repair']]
            if rent_data['changes'] == 5:
                del rent_data['apartment_area']
            if 'apartment_area' not in rent_data:
                rent_data['apartment_area'] = int (message.text)
        if len(rent_data) == 14: 
            await bot.send_message (chat_id=message.chat.id, text='Запомнил!')
            await show_rent(message, state)
            return
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair_}\nПлощадь: {message.text} м2\n\nВведите этаж', reply_markup=await back_button_reply())
        await New_rent.floor.set()
    else:
        await message.reply('Напишите цифрами площадь')

# @dp.message_handler(state=New_rent.floor)
async def floor_all (message:types.Message, state:FSMContext, args=None ):
    if message.text == 'Назад':
        if args != None:
            async with state.proxy() as rent_data:
                type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
                district = about_house_dict['district'][rent_data['district']]
                type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
            await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {rent_data["floor"]}\n\nCколько этажей в доме?', reply_markup= await back_button_reply())
            await New_rent.floors_in_house.set()            
        async with state.proxy() as rent_data:
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            del rent_data['apartment_area']
            await house_area (message,state=state)
    elif message.text.isnumeric():
        async with state.proxy() as rent_data:
            rent_data['floor'] = int (message.text)
        type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
        district = about_house_dict['district'][rent_data['district']]
        type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {message.text}\n\nCколько этажей в доме?', reply_markup= await back_button_reply())
        await New_rent.floors_in_house.set()
    else:
        await message.reply('Напишите цифрами этаж')


# @dp.message_handler(state=New_rent.floors_in_house)
async def description (message:types.Message, state:FSMContext, chat_id = None):
    if message.text == 'Назад':
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        async with state.proxy() as rent_data:
            del rent_data['floor']
            await floor (message, state, arg=True)
            return 
    async with state.proxy() as rent_data:
        if len(rent_data) == 14:
            await bot.send_message (chat_id= chat_id, text="Введите новое описание")
            await New_rent.description.set()
            return
        if message.text.isnumeric():
            if 'floors_in_house' not in rent_data:
                rent_data['floors_in_house'] = int(message.text)
            type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
            district = about_house_dict['district'][rent_data['district']]
            type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
            if len(rent_data) == 14:
                await bot.send_message (chat_id= chat_id, text="Введите новое описание")
                await New_rent.description.set()
                return
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
            await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
            await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {rent_data["floor"]}\nЭтажей в доме: {message.text}\n\nВведите описание квартиры', reply_markup=await back_button_reply())
            await New_rent.description.set()
        else:
            await message.reply('Напишите цифрами сколько этажей в доме всего')


# @dp.message_handler(state=New_rent.description)
async def animals (message:types.Message, state:FSMContext):
    if message.text == 'Назад':
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        async with state.proxy() as rent_data:
            del rent_data['floor']
            await floor_all (message, state, args=True)
            return
    async with state.proxy() as rent_data:
        rent_data['description'] = message.text
    if len(rent_data) == 14: 
        await bot.send_message (chat_id=message.chat.id, text='Запомнил!')
        await show_rent(message, state)
        return 
    type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
    district = about_house_dict['district'][rent_data['district']]
    type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
    await bot.send_message (chat_id=message.chat.id, text=f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {rent_data["floor"]}\nЭтажей в доме: {rent_data["floors_in_house"]}\nОписание: {message.text}\n\nМожно ли с животными?', reply_markup= await rentier_yes_no_keybord())
    await New_rent.animals.set()


# @dp.callback_query_handler(state=New_rent.animals)
async def kids (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as rent_data:
        rent_data['animals'] = callback_query.data
    animals_in_house = about_house_dict['true_false'][rent_data['animals']]
    type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
    district = about_house_dict['district'][rent_data['district']]
    type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
    await callback_query.message.edit_text(f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {rent_data["floor"]}\nЭтажей в доме: {rent_data["floors_in_house"]}\nОписание: {rent_data["description"]}\nС животными: {animals_in_house}\n\nМожно ли с детьми?', reply_markup= await rentier_yes_no_keybord())
    await New_rent.kids.set()


# @dp.callback_query_handler(state=New_rent.kids)
async def photo_set (callback_query:types.CallbackQuery, state:FSMContext, ):
    async with state.proxy() as rent_data:
        if 'kids' not in rent_data:
            rent_data['kids'] = callback_query.data
    kids_in_house = about_house_dict['true_false'][rent_data['kids']]
    animals_in_house = about_house_dict['true_false'][rent_data['animals']]
    type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
    district = about_house_dict['district'][rent_data['district']]
    type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
    if len(rent_data) == 14:
        await bot.send_message (chat_id= callback_query.message.chat.id , text="Установите новые фото")
        async with state.proxy() as rent_data:
            del rent_data['photos']
        await New_rent.photo.set()
        return
    await callback_query.message.edit_text(f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {rent_data["floor"]}\nЭтажей в доме: {rent_data["floors_in_house"]}\nОписание: {rent_data["description"]}\nС животными: {animals_in_house}\nС детьми: {kids_in_house}\n\nПрикрепите несколько фотографий квартиры')
    await New_rent.photo.set()





#dp.message_handler(state=New_rent.photo, content_types=types.ContentTypes.PHOTO)
async def show_rent (message:types.Message, state:FSMContext, album: List[types.Message]= None):
    media_group = types.MediaGroup()
    async with state.proxy() as rent_data:
        if 'photos' in rent_data:
            for photo in rent_data['photos']:
                media_group.attach_photo (photo=photo)
        else:
            try:
                for obj in album:
                    if obj.photo:
                        file_id = obj.photo[-1].file_id
                        if 'photos' not in rent_data:
                            rent_data['photos'] = []  
                            rent_data['photos'].append(file_id)
                        else:
                            rent_data['photos'].append(file_id)
                    else:
                        file_id = obj[obj.content_type].file_id

                    # We can also add a caption to each file by specifying `"caption": "text"`
                    media_group.attach({"media": file_id, "type": obj.content_type})
            except TypeError:
                await bot.delete_message (chat_id= message.chat.id, message_id=message.message_id)
                return await bot.send_message (chat_id= message.chat.id, text = 'Прикрепите больше фотографий')
                

    
    animals_in_house = about_house_dict['true_false'][rent_data['animals']]
    kids_in_house = about_house_dict['true_false'][rent_data['kids']]
    type_house = about_house_dict['type_of_house'][rent_data['type_of_house']]
    district = about_house_dict['district'][rent_data['district']]
    type_repair = about_house_dict['type_repair'][rent_data['type_repair']]
    await message.answer_media_group(media_group)
    await bot.send_message(chat_id=message.chat.id,text =f'{type_house}\nКомнат: {rent_data["rooms"]}\nЦена: {rent_data["price"]} $\nКомиссия: {rent_data["komission"]} $\nРайон: {district}\nТип ремонта: {type_repair}\nПлощадь: {rent_data["apartment_area"]} м2\nЭтаж: {rent_data["floor"]}\nЭтажей в доме: {rent_data["floors_in_house"]}\nОписание: {rent_data["description"]}\nС животными: {animals_in_house}\nС детьми: {kids_in_house}\n\nПодтвердите публикацию объявления или измените один из параметров', reply_markup=await confirmation_keybord(about_house_dict['change_point'], additional_b_name = 'Все верно, разместить', additional_b_data='confirmed', add_2= 'Отмена (в Главное меню)', add_2_data='отмена'))

    await New_rent.confirmation.set()



# @dp.callback_query_handler (state = New_rent.confirmation)
async def change_point (callback_query:types.CallbackQuery, state:FSMContext):
    if callback_query.data == 'отмена':
        await callback_query.answer ('Объявление удалено')
        await state.finish()
        await handler.rentier_profile.rentier_profile_check (callback_query.message)
    elif callback_query.data == 'type_of_house':
        async with state.proxy() as rent_data:
            rent_data['changes'] = 1
        await type_of_house(callback_query, state)

    elif callback_query.data == 'rooms':
        async with state.proxy() as rent_data:
            rent_data['changes'] = 2 
        await rooms (callback_query=callback_query, state=state)

    elif callback_query.data == 'district':
        async with state.proxy() as rent_data:
            rent_data['changes'] = 3
        await house_district (message=callback_query.message, state=state , chat_id=callback_query.message.chat.id)

    elif callback_query.data == 'type_repair':
        async with state.proxy() as rent_data:
            rent_data['changes'] = 4
        await type_repair (callback_query=callback_query,state=state)

    elif callback_query.data == 'apartment_area':
        async with state.proxy() as rent_data:
            rent_data['changes'] = 5
        await house_area(callback_query, state)

    elif callback_query.data == 'floor':
        await bot.send_message (callback_query.message.chat.id, 'Введите этаж')
        await New_rent.change_floor_st.set()

    elif callback_query.data == 'floors_in_house':
        await bot.send_message (callback_query.message.chat.id, 'Сколько этажей в доме?')
        await New_rent.change_floor_all_st.set()
    
    elif callback_query.data == 'kids':
        await bot.send_message (callback_query.message.chat.id, 'Можно с детьми?', reply_markup= await rentier_yes_no_keybord())
        await New_rent.change_kids_st.set()  

    elif callback_query.data == 'animals':
        await bot.send_message (callback_query.message.chat.id, 'Можно с животными?', reply_markup= await rentier_yes_no_keybord())
        await New_rent.change_animals_st.set()

    elif callback_query.data == 'price':
        async with state.proxy() as rent_data:
            rent_data['changes'] = 6        
        await price (callback_query, state)

    elif callback_query.data == 'komission':
        its_rentie_check = (await sql_check (field="id_member", field_2= ', rieltor' ,value= callback_query.from_user.id, table= 'rentie' ))[0][1]
        if its_rentie_check == True:
            await bot.send_message (chat_id= callback_query.message.chat.id ,text='Введите коммиссию')
            await New_rent.komission.set()     
        else: 
            await callback_query.answer (text="Для установки коммисии нужно быть риелтором") 
    elif callback_query.data == 'description':
        await description (callback_query.message , state=state , chat_id= callback_query.message.chat.id)
    elif callback_query.data == 'photo':
        await photo_set (callback_query=callback_query , state=state)
    else: 
        id_member = callback_query.message.chat.id
        async with state.proxy() as rent_data:
            rent_data['fk_id_member'] = id_member
        id_rent = (await sql_insert_new_rent (state, rent_data['fk_id_member']))[0]
        for photo in rent_data['photos']:
            await sql_insert_photos(id_rent , photo)
        await callback_query.answer ('Объявление размещено!', show_alert=True)
        await state.finish()
        await handler.rentier_profile.rentier_profile_check (callback_query.message)

async def change_floor (message:types.Message, state:FSMContext):
    async with state.proxy() as rent_data: 
        rent_data['floor'] = message.text
    await message.answer ('Этаж изменен')
    await show_rent (message=message, state=state)

async def change_floor_all (message:types.Message, state:FSMContext):
    async with state.proxy() as rent_data: 
        rent_data['floors_in_house'] = message.text
    await message.answer ('Изменения внесены')
    await show_rent (message=message, state=state)
    
async def change_kids (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as rent_data: 
        rent_data['kids'] = callback_query.data
    await callback_query.answer ('Изменения внесены')
    await show_rent (message=callback_query.message, state=state) 

async def change_animals (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as rent_data: 
        rent_data['animals'] = callback_query.data
    await callback_query.answer ('Изменения внесены')
    await show_rent (message=callback_query.message, state=state)    
       
    

def registr_handlers(dp:Dispatcher):
    dp.register_callback_query_handler(type_of_house,filters.Text (equals='start_new_rent'))
    dp.register_callback_query_handler(rooms, state=New_rent.type_of_house)
    dp.register_callback_query_handler(price, state=New_rent.rooms)
    dp.register_message_handler(komission, state=New_rent.price)
    dp.register_message_handler(house_district, state=New_rent.komission)
    dp.register_callback_query_handler(type_repair, state=New_rent.district)
    dp.register_callback_query_handler(house_area, state=New_rent.type_repair)
    dp.register_message_handler(floor, state=New_rent.apartment_area)
    dp.register_message_handler(floor_all, state=New_rent.floor)
    dp.register_message_handler(description, state=New_rent.floors_in_house)
    dp.register_message_handler(animals, state=New_rent.description)
    dp.register_callback_query_handler(kids, state=New_rent.animals)
    dp.register_callback_query_handler(photo_set, state=New_rent.kids)
    dp.middleware.setup(AlbumMiddleware())
    dp.register_message_handler(show_rent, state=New_rent.photo, content_types=types.ContentTypes.PHOTO)
    dp.register_callback_query_handler (change_point, state=New_rent.confirmation)
    dp.register_message_handler (change_floor, state=New_rent.change_floor_st)
    dp.register_message_handler (change_floor_all, state=New_rent.change_floor_all_st)
    dp.register_callback_query_handler(change_kids, state=New_rent.change_kids_st)
    dp.register_callback_query_handler(change_animals, state=New_rent.change_animals_st)



    