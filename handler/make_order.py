# арендовать квартиру 

import asyncio
from aiogram import types, Dispatcher 
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, filters
from config import ADMIN


from database.bd import drop_row, search_houses, sql_check, sql_check_rentie_name_tn, sql_insert_take_order, sql_insert_user_take_house, sql_show_photo, update_row
from handler.change_order import change_order_start 
from keybord.rentier_keybord import * 
from sys_files.bot_creation import dp, bot
from handler.pass_house import about_house_dict ,list_of_bd



list_bd = ['type_of_house', 'rooms', 'price min-max', 
'district', 'type_repair', 'area mi-max', 'floors', 'animals' , 'kids', 'notify']

class make_order(StatesGroup):
    start_creation = State()
    user_name = State()
    delete_status = State()
    type_of_house = State()
    rooms = State()
    price = State()
    rieltor_show = State()
    district = State()
    type_repair = State()
    area = State()
    floors = State()
    animals_kids = State()
    show_res = State()
    notify = State()




async def start_cr_order (message: types.Message):

    check_user = (await sql_check(field = 'tg_id', field_2 =',name', table='users', value = message.chat.id))
    flag = True 
    for check in check_user:
        if check[0]==message.chat.id:
            await message.answer(f'{check[1]}, чем могу помочь?', reply_markup = await take_house_keybord_menu())
            flag = False
    if flag:
        await message.answer('Мы еще не знакомы\nКак к вам обращаться?', reply_markup= ReplyKeyboardRemove())
        await make_order.user_name.set()


# @dp.message_handler (lambda message: message.text in ['Создать запрос','Посмотреть мой запрос'])
async def new_take (message: types.Message):
    if message.text == 'Посмотреть мой запрос':
        await change_order_start( message)
    else:
        check_orders_fr_id = await sql_check('fk_tg_id','','orders', message.chat.id)
        if  len(check_orders_fr_id) > 0:
            await message.answer(' У вас уже есть активный запрос. Для создания нового удалите предыдущий', reply_markup =await delete_order_kbd())
            await make_order.delete_status.set()
            return
        await message.answer ('Начнем')
        dot_msg = await bot.send_message (chat_id=message.chat.id,text='.', reply_markup=ReplyKeyboardRemove())  
        await bot.delete_message (chat_id=message.chat.id, message_id=dot_msg.message_id)
        await message.answer ('Выберите тип жилья', reply_markup = await confirmation_keybord(dictionary=about_house_dict['type_of_house'], additional_b_data='Отмена', additional_b_name='◀️Назад'))
        await make_order.type_of_house.set()

# @dp.message_handler (state = make_order.delete_status)
async def delete_order (message: types.Message, state: FSMContext):
    if message.text == 'Удалить':
        await drop_row(message.chat.id)
        await message.answer('Объявление удалено')
        await state.finish()
        await start_cr_order(message)
    elif message.text == 'Посмотреть мой запрос':
        await change_order_start (message)
    else:
        await state.finish()
        await start_cr_order(message)

# @dp.callback_query_handler ( state=make_order.type_of_house)
async def pass_type_house (callback_query:types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'next':
        await callback_query.message.edit_text('Выберите количество комнат', reply_markup = await take_rooms_keybord(4, '4+', '4+', '◀️Назад', 'back'))
        await make_order.rooms.set()
    elif callback_query.data == 'Отмена':
        await callback_query.message.answer('Отмена')
        await state.finish()
        await start_cr_order(callback_query.message)
    else:
        async with state.proxy() as data_take:
            if callback_query.data.isnumeric():
                if 'type_of_house' in data_take:
                    data_take['type_of_house'] = data_take ['type_of_house']+ ', ' +str(callback_query.data)
                    data_take ['type_of_house']=  data_take['type_of_house'].split(', ')
                    data_take['type_of_house'] = list(set(data_take['type_of_house']))
                    data_take['type_of_house'] = ', '.join(data_take ['type_of_house'])
                else:
                    data_take['type_of_house'] = str(callback_query.data)
            
        await callback_query.message.edit_text(f'Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await confirmation_keybord(dictionary=about_house_dict['type_of_house'], additional_b_data='next', additional_b_name='Далее'))
        await make_order.type_of_house.set()


# @dp.callback_query_handler ( state=make_order.rooms)
async def pass_rooms (callback_query:types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'back':
        await callback_query.message.edit_text('Выберите тип жилья', reply_markup = await confirmation_keybord(dictionary=about_house_dict['type_of_house'], additional_b_data='Отмена', additional_b_name='◀️Назад'))
        await state.finish()
        await pass_type_house(callback_query, state)
    elif callback_query.data == 'next':
        await bot.delete_message (callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message (callback_query.message.chat.id, 'Ваш бюджет От ($)', reply_markup= await back_button_reply())
        # await callback_query.message.edit_text('Ваш бюджет От ($)',reply_markup= await back_button_reply() )
        await make_order.price.set() 
    else:
        async with state.proxy() as data_take:
            if 'rooms' in data_take:
                data_take['rooms'] = data_take ['rooms']+ ', ' +str(callback_query.data)
                data_take ['rooms']=  data_take['rooms'].split(', ')
                data_take['rooms'] = list(set(data_take['rooms']))
                data_take['rooms'] = ', '.join(data_take ['rooms'])
            else:
                data_take['rooms'] = str(callback_query.data)
            
        await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await take_rooms_keybord(4, '4+', '4+', "Дальше",'next'))
        await make_order.rooms.set()


# @dp.message_handler (state=make_order.price)
async def pass_price (message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        await bot.delete_message (message.chat.id, message.message_id)
        async with state.proxy() as data_take:
            if 'price_min' in data_take:
                del data_take['price_min']
            elif 'rooms' in data_take:
                del data_take['rooms']
        await message.answer('Выберите количество комнат', reply_markup = await take_rooms_keybord(4, '4+', '4+', '◀️Назад', 'back'))
        dot_msg = await bot.send_message (chat_id=message.chat.id,text='.', reply_markup=ReplyKeyboardRemove())  
        await bot.delete_message (chat_id=message.chat.id, message_id=dot_msg.message_id)
        await make_order.rooms.set()
    elif message.text.isnumeric():
        async with state.proxy() as data_take:
            if 'price_min' in data_take:
                if 'price_max'not in data_take:
                    data_take['price_max'] = int(message.text)
                    dot_msg = await bot.send_message (chat_id=message.chat.id,text='.', reply_markup=ReplyKeyboardRemove())  
                    await bot.delete_message (chat_id=message.chat.id, message_id=dot_msg.message_id)
                    await message.answer ("Показать варианты риелторов?", reply_markup = await rentier_yes_no_keybord())
                    await make_order.rieltor_show.set()
            else:
                data_take['price_min'] = int (message.text)
                await message.answer('До ($)')
                await make_order.price.set()
    else:
        await message.answer('Введите число')


# @dp.callback_query_handler (state=make_order.rieltor_show)
async def pass_rieltor_show (callback_query:types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data_take:
        data_take['rieltor_show'] = callback_query.data
        with open ('map.png', 'rb') as media:
            await bot.send_photo (chat_id=callback_query.message.chat.id , photo= media)
        await callback_query.message.answer('Выберите район', reply_markup = await district_keybord(about_house_dict['district'],'◀️Назад', 'back'))
        await make_order.district.set()


# @dp.callback_query_handler (state=make_order.district)
async def pass_district (callback_query:types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'back':
        await bot.delete_message (callback_query.message.chat.id, callback_query.message.message_id)
        async with state.proxy() as data_take:
            if 'district' in data_take:
                del data_take['district']
        await callback_query.message.answer('Показать варианты риелторов?', reply_markup = await rentier_yes_no_keybord())
        await make_order.rieltor_show.set()
    elif callback_query.data == 'next':
        async with state.proxy() as data_take:
            if 'district' not in data_take:
                data_take['district'] = '0'
        await callback_query.message.edit_text('Выберите тип ремонта', reply_markup = await district_keybord(about_house_dict['type_repair'],'◀️Назад', 'back'))
        await make_order.type_repair.set()
    else:
        async with state.proxy() as data_take:
            if 'district' in data_take:
                data_take['district'] = data_take ['district']+ ', ' +str(callback_query.data)
                data_take ['district']=  data_take['district'].split(', ')
                data_take['district'] = list(set(data_take['district']))
                data_take['district'] = ', '.join(data_take ['district'])
            else:
                data_take['district'] = str(callback_query.data)
        await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await district_keybord(about_house_dict['district'], 'Далее', 'next'))
        await make_order.district.set()


# @dp.callback_query_handler (state=make_order.type_repair)
async def pass_type_repair (callback_query:types.CallbackQuery, state: FSMContext): 
    if callback_query.data == 'back':
        async with state.proxy() as data_take:
            if 'type_repair' in data_take:
                del data_take['type_repair']
            if 'district' in data_take:
                del data_take['district']
        await bot.delete_message (callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message (callback_query.message.chat.id, 'Выберите район', reply_markup = await district_keybord(about_house_dict['district'], '◀️Назад', 'back'))
        await make_order.district.set()
    elif callback_query.data == 'next':
        async with state.proxy() as data_take:
            if 'type_repair' not in data_take:
                data_take['type_repair'] = '0'
        await bot.delete_message (chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)       
        await bot.send_message (chat_id=callback_query.message.chat.id,text='Площадь квартиры: ОТ (м2)', reply_markup= await back_button_reply ())

        await make_order.area.set()
    else:
        async with state.proxy() as data_take:
            if 'type_repair' in data_take:
                data_take['type_repair'] = data_take ['type_repair']+ ', ' +str(callback_query.data)
                data_take ['type_repair']=  data_take['type_repair'].split(', ')
                data_take['type_repair'] = list(set(data_take['type_repair']))
                data_take['type_repair'] = ', '.join(data_take ['type_repair'])
            else:
                data_take['type_repair'] = str(callback_query.data)
            
        await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await district_keybord(about_house_dict['type_repair'], 'Далее', 'next'))
        await make_order.type_repair.set()


# @dp.message_handler (state=make_order.area)
async def pass_area (message: types.Message, state: FSMContext):
    # площадь назад поменять 
    if message.text == 'Назад':
        async with state.proxy() as data_take:
            if 'area_min' in data_take:
                del data_take['area_min']
                await message.answer ('Площадь квартиры: ОТ (м2)')
                await make_order.area.set ()
                return
            if 'type_repair' in data_take:
                del data_take['type_repair']
        await message.answer('Выберите тип ремонта', reply_markup = await district_keybord(about_house_dict['type_repair'], 'Далее', 'next', '◀️Назад', 'back'))
        await make_order.type_repair.set()
    else:
        async with state.proxy() as data_take:
            if 'area_min' in data_take:
                if 'area_max'not in data_take:
                    data_take['area_max'] = int(message.text)
                    dot_msg = await bot.send_message (chat_id=message.chat.id,text='.', reply_markup=ReplyKeyboardRemove())  
                    await bot.delete_message (chat_id=message.chat.id, message_id=dot_msg.message_id)
                    await message.answer ("Какой должен быть этаж?", reply_markup = await take_floor_keybord(back='◀️Назад', back_data='back', skip='Пропустить', skip_data='next'))
                    await make_order.floors.set()
            else:
                data_take['area_min'] = int(message.text)
                await bot.delete_message (message.chat.id, message.message_id)
                await bot.delete_message (message.chat.id, message.message_id-1)
                await message.answer('Площадь квартиры: ДО (м2)', reply_markup= await back_button_reply ())
                await make_order.area.set()


# @dp.callback_query_handler (state=make_order.floors)
async def pass_floor (callback_query:types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'back':
        async with state.proxy() as data_take:
            if 'floor' in data_take:
                del data_take['floor']
            if 'area_max' in data_take:
                del data_take['area_max']
        await bot.delete_message (callback_query.message.chat.id, callback_query.message.message_id)
        await bot.send_message (callback_query.message.chat.id, 'Площадь квартиры: ДО (м2)',reply_markup= await back_button_reply ())
        await make_order.area.set()
    elif callback_query.data == 'next':
        async with state.proxy() as data_take:
            if 'floor'not in data_take:
                data_take['floor'] = '0'
        await callback_query.message.edit_text('Вы ищите квартиру в которую можно с', reply_markup = await kids_animals_take_keybord(back='◀️Назад', back_data='back', skip='Пропустить', skip_data='next'))
        await make_order.animals_kids.set()
    else:
        async with state.proxy() as data_take:
            if 'floor' in data_take:
                data_take['floor'] = data_take ['floor']+ ', ' +str(callback_query.data)
                data_take ['floor']=  data_take['floor'].split(', ')
                data_take['floor'] = list(set(data_take['floor']))
                data_take['floor'] = ', '.join(data_take ['floor'])
            else:
                data_take['floor'] = str(callback_query.data)
            
        await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await take_floor_keybord(skip='Далее', skip_data='next'))
        await make_order.floors.set()


# @dp.callback_query_handler (state=make_order.animals_kids)
async def pass_animals_kids (callback_query:types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'back':
        async with state.proxy() as data_take:
            if 'kids' in data_take:
                del data_take['kids']
            if 'animals' in data_take:
                del data_take['animals']
            if 'floor' in data_take:
                del data_take['floor']

        await callback_query.message.edit_text('Какой должен быть этаж?', reply_markup = await take_floor_keybord(back='◀️Назад', back_data='back', skip='Пропустить', skip_data='next'))
        await make_order.floors.set()
    elif callback_query.data == 'next':
        async with state.proxy() as data_take:
            if 'animals' not in data_take:
                data_take['animals'] = 'None'
                anima_msg = 'Без разницы'
            else:
                anima_msg = about_house_dict["true_false"][data_take["animals"]]
            if 'kids' not in data_take:
                data_take['kids'] = 'None'
                kids_msg = 'Без разницы'
            else:
                kids_msg = about_house_dict["true_false"][data_take["kids"]]
            t_h_msg = ''
            type_of_house = data_take['type_of_house'].split(', ')
            for i in type_of_house:
                t_h_msg =str(about_house_dict['type_of_house'][int(i)]) + ', ' + t_h_msg
            district_take = data_take['district'].split(', ')
            d_msg = ''

            for i in district_take:
                if i == '0':
                    d_msg = 'Без разницы. ' + d_msg
                else:
                    d_msg = str(about_house_dict['district'][int(i)]) + ', ' + d_msg
            type_repair_take = data_take['type_repair'].split(', ')
            t_r_msg = ''

            for i in type_repair_take:
                if i == '0':
                    t_r_msg = 'Без разницы. ' + t_r_msg
                else:
                    t_r_msg = str(about_house_dict['type_repair'][int(i)]) + ', ' + t_r_msg
            floor_take = data_take['floor'].split(', ')
         
            f_msg = ''
            for i in floor_take:
                if i == '1':
                    f_msg = 'Не первый этаж. ' + f_msg
                elif i == '2':
                    f_msg = 'Не последний этаж. ' + f_msg
                else:
                    f_msg = 'Любой этаж. ' + f_msg
            # rooms_msg = data_take['rooms'].split(', ')
            # # rooms_msg = list(set(rooms_msg))
            await callback_query.message.edit_text(f'Ваш запрос\n\nТипы жилья: {t_h_msg}\n'
                                                f'Комнат: {data_take["rooms"]}\n'
                                                f'Цена: {data_take["price_min"]} - {data_take["price_max"]} $\n'
                                                f'Показывать объявления риелторов: {about_house_dict["true_false"][data_take["rieltor_show"]]}\n'
                                                f'Район: {d_msg}\n'
                                                f'Тип ремонта: {t_r_msg}\n'
                                                f'Площадь: {data_take["area_min"]} - {data_take["area_max"]} м2\n'
                                                f'Этаж: {f_msg}\n'
                                                f'Дети: {kids_msg}\n'
                                                f'Животные: {anima_msg}\n', reply_markup= await start_search_kbd())
            data_take['fk_tg_id'] = callback_query.from_user.id
            await sql_insert_take_order(data_take=data_take)
            await make_order.show_res.set()
    else:
        if callback_query.data == 'kids':
            async with state.proxy() as data_take:
                if 'kids' in data_take:
                    await bot.send_message(callback_query.message.chat.id, 'Уже записано')
                else:
                    data_take['kids'] = 'True'
        elif callback_query.data == 'animals':
            async with state.proxy() as data_take:
                if 'animals' in data_take:
                    await bot.send_message(callback_query.message.chat.id, 'Уже записано')
                else:
                    data_take['animals'] = 'True'
        await callback_query.message.edit_text('Ваш вариант выбран. Выберите еще один или нажмите кнопку далее?', reply_markup = await kids_animals_take_keybord(skip='Далее', skip_data= 'next'))
        await make_order.animals_kids.set()

# TODO
# @dp.callback_query_handler (state=make_order.show_res)
async def start_search (callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'start_search':
        await callback_query.answer('Ищем наиболее подходящие варианты')
        list_of_houses = await search_houses (id_member=callback_query.message.chat.id) 
        number = 1
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

            await bot.send_media_group (chat_id= callback_query.message.chat.id ,  media=media_group)          
            await bot.send_message (chat_id= callback_query.message.chat.id , text = f'Номер объявления: {number}\n\nТип дома: {about_house_dict["type_of_house"][message_rent["type_of_house"]]}\n'
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
            f'{data[2]}',reply_markup= await ban_button(admin_url=ADMIN))
            del media_group
            number += 1
        if len(list_of_houses) == 0:
            await bot.send_message(callback_query.message.chat.id, 'По вашему запросу ничего не найдено')
        await bot.send_message (callback_query.message.chat.id, 'Поиск завершен. Вы можете сохранить его и получать новые предложения автоматически ежедневно.',reply_markup=await save_order_kbd())
        await make_order.notify.set()
    elif callback_query.data == 'change':
        await state.finish()
        await change_order_start (message=callback_query.message)
    else:
        await state.finish()
        await drop_row (id_member=callback_query.message.chat.id)
        await start_cr_order(callback_query.message)



# @dp.callback_query_handler ( state=make_order.notify)
async def notify (callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'save':
        await callback_query.message.edit_text('Сохранено, Вам будет приходить ежедневная подборка с новыми объявлениями по Вашему фильтру с 11 до 20 по Московскому времени.\nОтписаться, от рассылки вы можете в меню "Посмотреть мой запрос"')
        await update_row(id_member=callback_query.message.chat.id)
        # await state.reset_data()
        # asyncio.create_task(scheduler_tg.scheduler(callback_query.message.chat.id,state=state))
    elif callback_query.data == 'drop':
        await drop_row (id_member=callback_query.message.chat.id)
        await callback_query.message.edit_text('Запрос удален')
    await state.finish()
    await start_cr_order (callback_query.message)


# @dp.message_handler (state=make_order.user_name)
async def user_name (message: types.Message, state: FSMContext):
    await message.answer('Приятно познакомится')
    await sql_insert_user_take_house(name = message.text , tg_id = message.chat.id)
    await state.finish()
    await new_take (message)

    


def registr_handlers(dp:Dispatcher):
    dp.register_message_handler (user_name, state=make_order.user_name, )
    dp.register_message_handler (new_take ,lambda message: message.text in ['Создать запрос','Посмотреть мой запрос'])
    dp.register_message_handler (delete_order, state=make_order.delete_status)
    dp.register_callback_query_handler (pass_type_house, state=make_order.type_of_house)
    dp.register_callback_query_handler (pass_rooms, state=make_order.rooms)
    dp.register_message_handler (pass_price, state=make_order.price)
    dp.register_callback_query_handler (pass_rieltor_show, state=make_order.rieltor_show)
    dp.register_callback_query_handler (pass_district, state=make_order.district)
    dp.register_callback_query_handler (pass_type_repair, state=make_order.type_repair)
    dp.register_message_handler (pass_area, state=make_order.area)
    dp.register_callback_query_handler (pass_floor, state=make_order.floors)
    dp.register_callback_query_handler (pass_animals_kids, state=make_order.animals_kids)
    dp.register_callback_query_handler (start_search, state=make_order.show_res)
    dp.register_callback_query_handler (notify, state=make_order.notify)

