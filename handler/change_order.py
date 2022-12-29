# Изменение готового запроса 

import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from database.bd import search_houses, sql_check, sql_check_rentie_name_tn, sql_show_photo, sql_update, update_order_bd, update_row, update_row_nt_fls
import handler
from keybord.rentier_keybord import ban_button, change_order_kbd, confirmation_keybord, district_keybord, kids_animals_take_keybord, notify_, order_show_change, rentier_yes_no_keybord, save_order_kbd, take_floor_keybord, take_rooms_keybord
from sys_files.bot_creation import bot,dp
from handler.pass_house import list_of_bd, about_house_dict
# import scheduler_tg
from config import ADMIN


class change_order(StatesGroup):
    change_first_step = State()
    change_second_step = State()
    notify_state = State()
    change_rooms = State()
    change_price = State()
    change_price_max = State()
    change_area = State()
    change_area_max = State()
    change_district = State()
    change_type_of_house = State()
    change_type_repair = State()
    change_floor = State()
    change_kids_animals = State()



async def change_order_start (message:types.Message):
    list_of_houses = (await sql_check (field='fk_tg_id',field_2=',*', table= 'orders', value = message.chat.id))
    if len(list_of_houses) == 0:
        await bot.send_message (chat_id=message.chat.id, text= 'Вы не создали запрос на поиск')
        await handler.make_order.start_cr_order(message)
        return
    list_of_houses = list_of_houses[0]
    rooms = list_of_houses[3]
    price = str(list_of_houses[4]) + ' - ' + str(list_of_houses[5])
    district = list_of_houses[6].split(', ')
    d_msg = ''
    for i in district:
            if i == '0':
                d_msg = 'Без разницы. ' + d_msg
            else:
                d_msg = str(about_house_dict['district'][int(i)]) + '. ' + d_msg
    type_repair = list_of_houses[7].split(', ')
    t_r_msg = ''
    for i in type_repair:
        if i == '0':
            t_r_msg = 'Без разницы. ' + t_r_msg
        else:
            t_r_msg = str(about_house_dict['type_repair'][int(i)]) + '. ' + t_r_msg
    area = str(list_of_houses[8]) + ' - ' + str(list_of_houses[9])
    floor = list_of_houses[10].split(', ')
    f_msg = ''
    for i in floor:
        if i == '1':
            f_msg = 'Не первый этаж. ' + f_msg
        elif i == '2':
            f_msg = 'Не последний этаж. ' + f_msg
        else:
            f_msg = 'Любой этаж. ' + f_msg
    animals = about_house_dict['true_false'][list_of_houses[11]]
    kids = about_house_dict['true_false'][list_of_houses[12]]
    type_of_house = list_of_houses[14].split(', ')
    t_h_msg = ''
    for i in type_of_house:
        t_h_msg =str(about_house_dict['type_of_house'][int(i)]) + '. ' + t_h_msg
    
    await bot.send_message (message.chat.id, f'Ваши объявления:\n\nТип жилья: {t_h_msg}\nКоличество комнат: {rooms}\nЦена: {price} $\nРайон: {d_msg}\nТип ремонта: {t_r_msg}\nПлощадь: {area} м2\nЭтаж: {f_msg}\nМожно с животными: {animals}\nМожно с детьми: {kids}')
    await bot.send_message (chat_id=message.chat.id, text= 'Изменить запрос', reply_markup =await order_show_change())
    await change_order.change_first_step.set()


# @dp.message_handler (state=change_order.change_first_step)
async def first_step_to_change (message:types.Message, state:FSMContext):
    async with state.proxy() as data:
        if 'flag' not in data:
            data['flag'] = 0 
        if message.text == 'Да':
            data['flag'] = 1
            dot_msg = await bot.send_message (chat_id=message.chat.id , text='.',reply_markup=ReplyKeyboardRemove())
            await bot.delete_message (chat_id= message.chat.id , message_id= dot_msg.message_id)
            await bot.send_message (chat_id=message.chat.id, text= 'Что Вы хотите изменить?',reply_markup= await confirmation_keybord(dictionary=about_house_dict['change_order'], additional_b_name = '◀️Назад', additional_b_data='отмена'))
            await change_order.change_second_step.set()
        elif data['flag'] == 1:
            await bot.send_message (chat_id=message.chat.id, text= 'Что Вы хотите изменить?',reply_markup= await confirmation_keybord(dictionary=about_house_dict['change_order'], additional_b_name = '◀️Назад', additional_b_data='отмена'))
            await change_order.change_second_step.set()
        elif message.text == 'Нет':
            await bot.send_message (chat_id=message.chat.id, text= 'Хорошо')
            await state.finish()
            await handler.make_order.start_cr_order(message)
        elif message.text == 'Уведомления':
            data['flag'] = 1
            await bot.send_message (chat_id=message.chat.id , text= 'Вам будет приходить ежедневная подборка с новыми объявлениями по Вашему фильтру с 11 до 20 по Московскому времени.', reply_markup= await notify_())
            await change_order.notify_state.set()
        elif message.text == 'Показать объявления по запросу':
            await bot.send_message (chat_id=message.chat.id, text = 'Ищу объявления')
            list_of_houses = await search_houses (id_member = message.chat.id) 
            number = 1
            if len(list_of_houses) == 0:
                await bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено') 
                await state.finish()
                await handler.make_order.start_cr_order(message)    
                return
            for rents in list_of_houses:
                media_group = types.MediaGroup()
                data = await sql_check_rentie_name_tn(rents[0])
                n=2
                message_rent ={}
                while n<15:
                    for i in list_of_bd:
                        message_rent[i] = rents [n]
                        n += 1
                list_of_photos = await sql_show_photo (id=rents[1])
                for photo in list_of_photos:
                    media_group.attach_photo (photo=photo[0])  

                await bot.send_media_group (chat_id= message.chat.id ,  media=media_group)          
                await bot.send_message (chat_id= message.chat.id , text = f'Номер объявления: {rents[1]}\n\nТип дома: {about_house_dict["type_of_house"][message_rent["type_of_house"]]}\n'
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
                f'Можно с детьми: {about_house_dict["true_false"][str(message_rent ["kids"])]}\n\n'
                f'Имя арендатора: {data[0]}\n'
                f'Номер телефона: {data[1]}\n'
                f'{data[2]}', reply_markup=await ban_button(admin_url=ADMIN))
                del media_group
                number += 1
            await bot.send_message (message.chat.id , 'Это пока все объявления по вашему запросу', reply_markup= ReplyKeyboardRemove())  
            await state.finish()  
            await handler.make_order.start_cr_order(message)   


# @dp.message_handler (state=change_order.notify_state)
async def change_notifier (message:types.Message, state:FSMContext):
    if message.text == 'Сохранить поиск':
        await message.answer('Сохранено, Вам будет приходить ежедневная подборка с новыми объявлениями по Вашему фильтру с 11 до 20 по Московскому времени.\nОтписаться, от рассылки вы можете в меню "Посмотреть мой запрос"', reply_markup= ReplyKeyboardRemove())
        await update_row(id_member=message.chat.id)
        # asyncio.create_task(scheduler_tg.scheduler(message.chat.id,state=state))
        await first_step_to_change(message, state)
    if message.text == 'Не сохранять поиск':
        await message.answer ('Уведомления отключены')
        await update_row_nt_fls(id_member=message.chat.id)
        await first_step_to_change(message, state)


# @dp.callback_query_handler (state=change_order.change_second_step)
async def second_step_to_change (callback_query:types.CallbackQuery, state:FSMContext):
    if callback_query.data == 'rooms':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите количество комнат', reply_markup = await take_rooms_keybord(4, '4+', '4+'))
        await change_order.change_rooms.set()
    elif callback_query.data == 'price':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите минимальный бюджет', reply_markup= ReplyKeyboardRemove())
        await change_order.change_price.set()
    elif callback_query.data == 'apartment_area':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите минимальную площадь', reply_markup= ReplyKeyboardRemove())
        await change_order.change_area.set()
    elif callback_query.data == 'district':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите район', reply_markup= await district_keybord(about_house_dict['district']))
        await change_order.change_district.set()
    elif callback_query.data == 'type_of_house':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите тип дома', reply_markup= await confirmation_keybord(dictionary=about_house_dict['type_of_house']))
        await change_order.change_type_of_house.set()
    elif callback_query.data == 'type_repair':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите тип ремонта', reply_markup= await confirmation_keybord(dictionary=about_house_dict['type_repair']))
        await change_order.change_type_repair.set()
    elif callback_query.data == 'floor':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Какой этаж', reply_markup= await take_floor_keybord(skip='Далее', skip_data='next'))
        await change_order.change_floor.set()
    elif callback_query.data == 'type_repair':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Введите тип ремонта', reply_markup=  await district_keybord(about_house_dict['type_repair'], 'Далее', 'next'))
        await change_order.change_type_repair.set()
    elif callback_query.data == 'animals_kids':
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Вы ищите квартиру в которую можно с', reply_markup= await kids_animals_take_keybord(skip= 'Пропустить', skip_data='next'))
        await change_order.change_kids_animals.set()
    else:
        await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Сохранил')
        await state.finish()
        await handler.make_order.start_cr_order(callback_query.message)
    

# @dp.callback_query_handler (state=change_order.change_rooms)
async def change_rooms (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data_take:
        if callback_query.data == 'next':
            await update_order_bd(callback_query.message.chat.id, 'rooms', data_take['rooms'])
            # await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=message.message_id)
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
            await bot.send_message (chat_id=callback_query.message.chat.id, text= 'Количество комнат изменено')
            await first_step_to_change(callback_query.message, state)
        else:
            if 'rooms' in data_take:
                data_take['rooms'] = data_take ['rooms']+ ', ' +str(callback_query.data)
                data_take ['rooms']=  data_take['rooms'].split(', ')
                data_take['rooms'] = list(set(data_take['rooms']))
                data_take['rooms'] = ', '.join(data_take ['rooms'])
            else:
                data_take['rooms'] = str(callback_query.data)
            await callback_query.message.edit_text(f'Количество комнат {data_take["rooms"]}\nВыбрать еще один вариант?', reply_markup = await take_rooms_keybord(4, '4+', '4+', "Закончить изменения",'next'))
            await change_order.change_rooms.set()  


# @dp.message_handler (state=change_order.change_price)
async def change_price (message:types.Message, state:FSMContext):
    await update_order_bd(message.chat.id, 'price_min', int(message.text))
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
    await bot.send_message (chat_id=message.chat.id, text= 'Введите максимальный бюджет')
    await change_order.change_price_max.set()


# @dp.message_handler (state=change_order.change_price_max)
async def change_price_max (message:types.Message, state:FSMContext):
    await update_order_bd(message.chat.id, 'price_max', int(message.text))
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
    await bot.send_message (chat_id=message.chat.id, text= 'Бюджет изменен')
    await first_step_to_change(message, state=state)


# @dp.message_handler (state=change_order.change_area)
async def change_area (message:types.Message, state:FSMContext):
    await update_order_bd(message.chat.id, 'apartment_area_min', int(message.text))
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
    await bot.send_message (chat_id=message.chat.id, text= 'Введите максимальную площадь')
    await change_order.change_area_max.set()


# @dp.message_handler (state=change_order.change_area_max)
async def change_area_max (message:types.Message, state:FSMContext):
    await update_order_bd(message.chat.id, 'apartment_area_max', int(message.text))
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message (chat_id=message.chat.id, message_id=message.message_id-1)
    await bot.send_message (chat_id=message.chat.id, text= 'Площадь изменена')
    await first_step_to_change(message, state=state)


# @dp.callback_query_handler (state=change_order.change_district)
async def change_district (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data_take:
        if callback_query.data == 'next':
            await update_order_bd(callback_query.message.chat.id, 'district', data_take['district'])
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
            await callback_query.message.edit_text (text= 'Район изменен')
            await first_step_to_change(callback_query.message, state=state)
        else:
            async with state.proxy() as data_take:
                if 'district' in data_take:
                    data_take['district'] = data_take ['district']+ ', ' +str(callback_query.data)
                    data_take ['district']=  data_take['district'].split(', ')
                    data_take['district'] = list(set(data_take['district']))
                    data_take['district'] = ', '.join(data_take ['district'])
                else:
                    data_take['district'] = str(callback_query.data)

            district_take = data_take['district'].split(', ')
            d_msg = ''
            for i in district_take:
                d_msg = str(about_house_dict['district'][int(i)]) + ', ' + d_msg
            await callback_query.message.edit_text(f'Район: {d_msg}\nВыбрать еще один вариант?', reply_markup = await district_keybord(about_house_dict['district'], 'Сохранить изменения', 'next'))
            await change_order.change_district.set()


# @dp.callback_query_handler (state=change_order.change_type_of_house)
async def change_type_of_house (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data_take:
        if callback_query.data.isnumeric():
            if 'type_of_house' in data_take:
                data_take['type_of_house'] = data_take ['type_of_house']+ ', ' +str(callback_query.data)
                data_take ['type_of_house']=  data_take['type_of_house'].split(', ')
                data_take['type_of_house'] = list(set(data_take['type_of_house']))
                data_take['type_of_house'] = ', '.join(data_take ['type_of_house'])
            else:
                data_take['type_of_house'] = str(callback_query.data)
            t_h_msg = ''
            type_of_house = data_take['type_of_house'].split(', ')
            for i in type_of_house:
                t_h_msg =str(about_house_dict['type_of_house'][int(i)]) + ', ' + t_h_msg
            await callback_query.message.edit_text(f'Типы жилья {t_h_msg}\nВыбрать еще один вариант?', reply_markup = await confirmation_keybord(dictionary=about_house_dict['type_of_house'], additional_b_data='next', additional_b_name='Закончить изменения'))
            await change_order.change_type_of_house.set()
        else:
            await update_order_bd(callback_query.message.chat.id, 'type_of_house', data_take['type_of_house'])
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
            await callback_query.message.edit_text (text= 'Тип дома изменен')
            await first_step_to_change(callback_query.message, state=state)


async def change_floor (callback_query:types.CallbackQuery, state:FSMContext):
    if callback_query.data == 'next':
        async with state.proxy() as data_take:
            if 'floor'not in data_take:
                data_take['floor'] = '0'
            await update_order_bd(callback_query.message.chat.id, 'floor', data_take['floor'])
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
        await callback_query.message.edit_text (text= 'Изменения приняты')
        await first_step_to_change(callback_query.message, state=state)
    async with state.proxy() as data_take:
        if 'floor' in data_take:
            data_take['floor'] = data_take ['floor']+ ', ' +str(callback_query.data)
            data_take ['floor']=  data_take['floor'].split(', ')
            data_take['floor'] = list(set(data_take['floor']))
            data_take['floor'] = ', '.join(data_take ['floor'])            
        else:
            data_take['floor'] = str(callback_query.data)
        await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее', reply_markup = await take_floor_keybord(skip='Далее', skip_data='next'))


async def change_type_repair (callback_query:types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data_take:
        if callback_query.data.isnumeric():
            if 'type_repairs' in data_take:
                data_take['type_repairs'] = data_take ['type_repairs']+ ', ' +str(callback_query.data)
                data_take ['type_repairs']=  data_take['type_repairs'].split(', ')
                data_take['type_repairs'] = list(set(data_take['type_repairs']))
                data_take['type_repairs'] = ', '.join(data_take ['type_repairs'])
            else:
                data_take['type_repairs'] = str(callback_query.data)
            t_r_msg = ''
            type_repair = data_take['type_repairs'].split(', ')
            for i in type_repair:
                t_r_msg =str(about_house_dict['type_repair'][int(i)]) + ', ' + t_r_msg
            await callback_query.message.edit_text(f'Типы ремонта {t_r_msg}\nВыбрать еще один вариант?', reply_markup = await confirmation_keybord(dictionary=about_house_dict['type_repair'], additional_b_data='next', additional_b_name='Закончить изменения'))
            await change_order.change_type_repair.set()
        else:
            await update_order_bd(callback_query.message.chat.id, 'type_repairs', data_take['type_repairs'])
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
            await callback_query.message.edit_text (text= 'Тип ремонта изменен')
            await first_step_to_change(callback_query.message, state=state)


async def change_kids_animals (callback_query:types.CallbackQuery, state:FSMContext):
    if callback_query.data == 'next':
        async with state.proxy() as data_take:
            if 'animals' not in data_take:
                data_take['animals'] = 'None'
            if 'kids' not in data_take:
                data_take['kids'] = 'None' 
            await update_order_bd(callback_query.message.chat.id, 'kids', data_take['kids'])
            await update_order_bd(callback_query.message.chat.id, 'animals', data_take['animals'])
            await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
            await callback_query.message.edit_text (text= 'Изменения приняты')
            await first_step_to_change(callback_query.message, state=state)   
            return
    if callback_query.data == 'kids':
        async with state.proxy() as data_take:
            if 'kids' in data_take:
                bot.send_message(callback_query.message.chat.id, 'Уже записано')
            else:
                data_take['kids'] = 'True'
    elif callback_query.data == 'animals':
        async with state.proxy() as data_take:
            if 'animals' in data_take:
                await bot.send_message(callback_query.message.chat.id, 'Уже записано')
            else:
                data_take['animals'] = 'True'
    await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await kids_animals_take_keybord(skip='Далее', skip_data='next'))
    await change_order.change_kids_animals.set()

     

#@dp.message_handler (state='*')
async def garbage_handler (message: types.Message):
    await message.answer('Не знаю, что ответить даже')


def registr_handlers(dp:Dispatcher):
    dp.register_message_handler (first_step_to_change,state=change_order.change_first_step)
    dp.register_message_handler (change_notifier , state=change_order.notify_state)
    dp.register_callback_query_handler (second_step_to_change, state=change_order.change_second_step)
    dp.register_callback_query_handler (change_rooms, state=change_order.change_rooms)
    dp.register_message_handler (change_price, state=change_order.change_price)
    dp.register_message_handler (change_price_max, state=change_order.change_price_max)
    dp.register_message_handler (change_area, state=change_order.change_area)
    dp.register_message_handler (change_area_max, state=change_order.change_area_max)
    dp.register_callback_query_handler (change_district, state=change_order.change_district)
    dp.register_callback_query_handler (change_type_of_house, state=change_order.change_type_of_house)
    dp.register_callback_query_handler (change_floor, state=change_order.change_floor)
    dp.register_callback_query_handler (change_type_repair, state=change_order.change_type_repair)
    dp.register_callback_query_handler (change_kids_animals, state=change_order.change_kids_animals)

    dp.register_message_handler (garbage_handler, state='*')