# Изменение предложений сдачи жилья 

import asyncio
from typing import List, Union


import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from database.bd import drop_photos, drop_rent, sql_check, sql_insert_photos, sql_show_photo, sql_update
import handler


from sys_files.bot_creation import bot,dp
from keybord.rentier_keybord import district_keybord, number_rents_keybord , confirmation_keybord, rentier_yes_no_keybord, rooms_keybord, type_of_house_keybord
from handler.pass_house import list_of_bd, about_house_dict, AlbumMiddleware



class change_rents(StatesGroup):
    change = State()
    change_acc = State()
    change_price = State()
    change_komission = State()
    change_description = State()
    change_photo = State ()
    change_rooms_state = State()
    change_type_of_house_state = State()
    change_type_of_repair_state = State()
    change_district_state = State()
    change_apartment_area_state = State()
    change_floor_state = State()
    change_floors_in_house_state = State()
    change_kids_state = State()
    change_animals_state = State()





async def my_rents(message:types.Message):
    list_of_rents = await sql_check (field_2=',*' , field= 'fk_id_member', table= 'rent' , value = message.chat.id)
    number = 1
    for rents in list_of_rents:
        media_group =  types.MediaGroup()
        n=2
        message_rent ={}
        while n<15:
            for i in list_of_bd:
                message_rent[i] =  rents [n]
                n += 1
        list_of_photos = await sql_show_photo (id=rents[1])
        for photo in list_of_photos:
            media_group.attach_photo (photo=photo[0])

        await message.answer_media_group (media_group)
        await bot.send_message (chat_id=message.chat.id, text= f'Номер объявления: {number}\n\nТип дома: {about_house_dict["type_of_house"][message_rent["type_of_house"]]}\n'
        f'Количество комнат: {message_rent["rooms"]}\n'
        f'Цена: {message_rent["price"]} $\n'
        f'Комиссия: { message_rent["komission"]} $\n'
        f'Район: {about_house_dict["district"][message_rent["district"]]}\n'
        f'Тип ремонта: {about_house_dict["type_repair"][message_rent["type_repair"]]}\n'
        f'Площадь квартиры: {message_rent["apartment_area"]} м2\n'
        f'Этаж: { message_rent["floor"]}\n'
        f'Этажность дома: {message_rent ["floors_in_house"]}\n'
        f'Описание: {message_rent ["description"]}\n'
        f'Можно с животными: {about_house_dict["true_false"][str(message_rent ["animals"])]}\n'
        f'Можно с детьми: {about_house_dict["true_false"][str(message_rent ["kids"])]}\n')
        del media_group
        number += 1
        await asyncio.sleep(1)
    await bot. send_message (chat_id=message.chat.id, text= 'Для изменения объявления отправьте номер объявления', reply_markup= await number_rents_keybord (number = len(list_of_rents)))
    await change_rents.change.set()


# @dp.message_handler (state=change_rents.change)
async def change_rent(message:types.Message, state:FSMContext):
    if message.text == 'Назад':
        await state.finish()
        await handler.rentier_profile.rentier_profile_check (message)    
        return
    async with state.proxy() as data:
        if 'flag' not in data:
            data['flag'] = 0
        if data['flag'] == 0:
            value_text = message.chat.id
            data ['chs_id_of_order'] = message.text
        elif data['flag'] == 1:
            value_text = message.chat.id

        list_of_rents = await sql_check (field_2=',*',field= 'fk_id_member', table= 'rent' , value = value_text)
        number_of_list = int(data['chs_id_of_order'])-1
        list_to_change = list_of_rents[number_of_list]
        data['type_of_house'] = list_to_change[2]
        data['rooms'] = list_to_change[3]
        data['price'] = list_to_change[4]
        data['komission'] = list_to_change[5]
        data['district'] = list_to_change[6]
        data['type_repair'] = list_to_change[7]
        data['apartment_area'] = list_to_change[8]
        data['floor'] = list_to_change[9]
        data['floors_in_house'] = list_to_change[10]
        data['description'] = list_to_change[11]
        data['animals'] = list_to_change[12]
        data['kids'] = list_to_change[13]
        # data['photo'] = list_to_change[14]

        media_group =  types.MediaGroup()
        list_of_photos = await sql_show_photo (id=list_to_change[1])
        for photo in list_of_photos:
            media_group.attach_photo (photo=photo[0])

        data['id_of_order'] = list_to_change[1]
        data['flag'] = 1

    await message.answer_media_group(media_group)
    await bot.send_message (chat_id=value_text, text= f'Тип дома: {about_house_dict["type_of_house"][data["type_of_house"]]}\n'
    f'Количество комнат: {data["rooms"]}\n'
    f'Цена: {data["price"]} $\n'
    f'Комиссия: { data["komission"]} $\n'
    f'Район: {about_house_dict["district"][data["district"]]}\n'
    f'Тип ремонта: {about_house_dict["type_repair"][data["type_repair"]]}\n'
    f'Площадь квартиры: {data["apartment_area"]} м2\n'
    f'Этаж: { data["floor"]}\n'
    f'Этажность дома: {data ["floors_in_house"]}\n'
    f'Описание: {data ["description"]}\n'
    f'Можно с животными: {about_house_dict["true_false"][str(data ["animals"])]}\n'
    f'Можно с детьми: {about_house_dict["true_false"][str(data ["kids"])]}\n\nЧто изменить?', reply_markup=await confirmation_keybord(dictionary=about_house_dict['change_point'], additional_b_name = 'Назад', additional_b_data='отмена',add_2='Удалить', add_2_data='delete'))
    await change_rents.change_acc.set()


# @dp.callback_query_handler(state=change_rents.change_acc)
async def change_acception (callback_query:types.CallbackQuery, state:FSMContext):
    if callback_query.data == 'delete':
        async with state.proxy() as data:
            id_ = data['id_of_order']
            data ['flag'] = 0
        await drop_rent (id_= id_, id_member=callback_query.message.chat.id)
        await callback_query.answer ('Объявление удалено')
        await my_rents (callback_query.message)
    elif callback_query.data == 'price':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новую цену')
        await change_rents.change_price.set()
    elif callback_query.data == 'komission':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новую комиссию')
        await change_rents.change_komission.set()
    elif callback_query.data == 'description':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новое описание')
        await change_rents.change_description.set()
    elif callback_query.data == 'photo':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Отправьте новое фото')
        await change_rents.change_photo.set()
    elif callback_query.data == 'rooms':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новое количество комнат' , reply_markup=await rooms_keybord (10))
        await change_rents.change_rooms_state.set()
    elif callback_query.data == 'type_of_house':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Выберите новый тип дома', reply_markup=await type_of_house_keybord())
        await change_rents.change_type_of_house_state.set()
    elif callback_query.data == 'type_repair':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Выберите новый тип ремонта', reply_markup=await district_keybord(about_house_dict['type_repair']))
        await change_rents.change_type_of_repair_state.set()
    elif callback_query.data == 'district':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Выберите новый район', reply_markup=await district_keybord(about_house_dict['district']))
        await change_rents.change_district_state.set()
    elif callback_query.data == 'apartment_area':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новую площадь квартиры')
        await change_rents.change_apartment_area_state.set()
    elif callback_query.data == 'floor':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новый этаж')
        await change_rents.change_floor_state.set()
        
    elif callback_query.data == 'floors_in_house':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Введите новую этажность дома')
        await change_rents.change_floors_in_house_state.set()
        
    elif callback_query.data == 'kids':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Можно с детьми?', reply_markup=await rentier_yes_no_keybord())
        await change_rents.change_kids_state.set()
        pass
    elif callback_query.data == 'animals':
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Можно с животными?', reply_markup=await rentier_yes_no_keybord())
        await change_rents.change_animals_state.set()
        pass
    else: 
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Возвращаемся в меню')
        await state.finish()
        await handler.rentier_profile.rentier_profile_check (callback_query.message)


# @dp.message_handler(state=change_rents.change_price)
async def change_price(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='price', value_to_change=message.text, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Цена изменена')
        await change_rents.change.set()
        await change_rent (message, state=state)


# @dp.message_handler(state=change_rents.change_komission)
async def change_komission(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='komission', value_to_change=message.text, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Комиссия изменена')
        await change_rents.change.set()
        await change_rent (message, state=state)



# @dp.message_handler(state=change_rents.change_description)
async def  change_description(message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='description', value_to_change=message.text, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Описание изменено')
        await change_rents.change.set()
        await change_rent (message, state=state)


# @dp.message_handler(state=change_rents.change_photo , content_types=types.ContentType.PHOTO)
async def  change_photo(message:types.Message, state:FSMContext,  album: List[types.Message]):
    async with state.proxy() as data:
        id_ = data['id_of_order']
        # DELETE FROM photos WHERE fk_rent_id = id_of_rent
        await drop_photos(id_)
        for obj in album:
            if obj.photo:
                file_id = obj.photo[-1].file_id
                await sql_insert_photos(id_photo=id_ ,photo=file_id)

        # await sql_update (name_of_column='photo', value_to_change=message.photo[-1].file_id, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Фото изменено')
        await change_rents.change.set()
        await change_rent (message, state=state)


async def change_rooms (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='rooms', value_to_change=callback_query.data, id_of_order=data['id_of_order'], id_user=callback_query.message.chat.id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Количество комнат изменено')
        await change_rents.change.set()
        await change_rent (callback_query.message, state=state)


async def change_type_of_house (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='type_of_house', value_to_change=callback_query.data, id_of_order=data['id_of_order'], id_user=callback_query.message.chat.id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Тип дома изменен')
        await change_rents.change.set()
        await change_rent (callback_query.message, state=state)


async def change_type_of_repair (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='type_repair', value_to_change=callback_query.data, id_of_order=data['id_of_order'], id_user=callback_query.message.chat.id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Тип ремонта изменен')
        await change_rents.change.set()
        await change_rent (callback_query.message, state=state)


async def change_district (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='district', value_to_change=callback_query.data, id_of_order=data['id_of_order'], id_user=callback_query.message.chat.id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Район изменен')
        await change_rents.change.set()
        await change_rent (callback_query.message, state=state)


async def change_apartment_area (message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='apartment_area', value_to_change=message.text, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Площадь квартиры изменена')
        await change_rents.change.set()
        await change_rent (message, state=state)


async def change_floor (message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='floor', value_to_change=message.text, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Этаж изменен')
        await change_rents.change.set()
        await change_rent (message, state=state)


async def change_floors_in_house (message: types.Message , state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='floors_in_house', value_to_change=message.text, id_of_order=data['id_of_order'], id_user=message.chat.id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
        await bot.send_message(chat_id=message.chat.id, text = 'Этажность дома изменена')
        await change_rents.change.set()
        await change_rent (message, state=state)


async def change_kids (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='kids', value_to_change=callback_query.data, id_of_order=data['id_of_order'], id_user=callback_query.message.chat.id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Изменения приняты')
        await change_rents.change.set()
        await change_rent (callback_query.message, state=state)


async def change_animals (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        await sql_update (name_of_column='animals', value_to_change=callback_query.data, id_of_order=data['id_of_order'], id_user=callback_query.message.chat.id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await bot.send_message(chat_id=callback_query.message.chat.id, text = 'Изменения приняты')
        await change_rents.change.set()
        await change_rent (callback_query.message, state=state)


def registr_handlers(dp:Dispatcher):
    dp.register_message_handler(change_rent, state= change_rents.change)
    dp.register_callback_query_handler(change_acception, state=change_rents.change_acc)
    dp.register_message_handler(change_price, state=change_rents.change_price)
    dp.register_message_handler(change_komission, state=change_rents.change_komission)
    dp.register_message_handler(change_description, state=change_rents.change_description)
    dp.register_message_handler(change_photo, state=change_rents.change_photo , content_types=types.ContentType.PHOTO)
    dp.register_callback_query_handler(change_rooms, state=change_rents.change_rooms_state)
    dp.register_callback_query_handler(change_type_of_house, state=change_rents.change_type_of_house_state)
    dp.register_callback_query_handler(change_type_of_repair, state=change_rents.change_type_of_repair_state)
    dp.register_callback_query_handler(change_district, state=change_rents.change_district_state)
    dp.register_message_handler(change_apartment_area, state=change_rents.change_apartment_area_state)
    dp.register_message_handler(change_floor, state=change_rents.change_floor_state)
    dp.register_message_handler(change_floors_in_house, state=change_rents.change_floors_in_house_state)
    dp.register_callback_query_handler(change_kids, state=change_rents.change_kids_state)
    dp.register_callback_query_handler(change_animals, state=change_rents.change_animals_state)
    
