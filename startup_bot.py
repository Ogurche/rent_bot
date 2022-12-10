# Запуск бота 

import logging 
from aiogram import executor
from aiogram import types
import asyncio
import datetime
import aioschedule

from sys_files.bot_creation import dp
from database.bd import *
from handler import pass_house , rentier_profile , change_pass_house , make_order, change_order
from handler.pass_house import about_house_dict ,list_of_bd
from sys_files.bot_creation import dp, bot
# from handler.pass_house import AlbumMiddleware



async def notifi ():
    data = await checker_sheduler()
    for i in data:
        houses = await search_houses (id_member=i[0])
        for res in houses:
            media_group = types.MediaGroup()
            if int(i[1]) < res[1]:
                data_names = await sql_check_rentie_name_tn(res[0])
                n=2
                message_rent ={}
                while n<15:
                    for z in list_of_bd:
                        message_rent[z] =  res [n]
                        n += 1

                list_of_photos = await sql_show_photo (id=res[1])
                for photo in list_of_photos:
                    media_group.attach_photo (photo=photo[0])  
                
                await bot.send_message ( chat_id= i[0], text='Новое предложение для вас')
                await bot.send_media_group (chat_id=i[0], media=media_group )
                await bot.send_message (chat_id= i[0] ,text= f'Тип дома: {about_house_dict["type_of_house"][message_rent["type_of_house"]]}\n'
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
                f'Имя арендатора: {data_names[0]}\n'
                f'Номер телефона: {data_names[1]}\n'
                f'{data_names[2]}')
                await update_lastseen(value=res[1], id_member=i[0])
                del media_group
                await asyncio.sleep(2)
        else:
            continue

async def schedul_():
    aioschedule.every().day.at('9:00').do(notifi)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)


async def startup(_):
    print ('Бот запущен!')
    db_connection()
    asyncio.create_task(schedul_())


# logging to file with time 
def logging_bot():
    logging.basicConfig(level= logging.WARNING ,filename='bot.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logging.warning ('Bot started')


if __name__== '__main__':
    logging_bot()
    rentier_profile.registr_handlers(dp)
    pass_house.registr_handlers(dp)
    change_pass_house.registr_handlers(dp)
    make_order.registr_handlers(dp)
    change_order.registr_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=startup)

