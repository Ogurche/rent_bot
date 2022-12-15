# Запросы к бд

import psycopg2
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import *


def db_connection ():
    try:
        global conn,  cursor 
        conn = psycopg2.connect(host= host , user= user, password= password, database = db_name)
        cursor = conn.cursor()
        if conn:
            print ('[INFO] База данных подключена')
    except Exception as e:
        print ("[INFO] Проблемы с подключением", e)


# Таблицы 
# orders(забросы на съем квартиры) | users(арендаторы) | rentie(арендодатели) | rent(предложения аренды)

# Тип жилья:
# Квартира - 1
# Комната - 2
# Дом - 3

# Тип ремонта:
# Бабушкин - 1
# Обычный - 2
# Евро - 3
# Дизайнерский - 4

# Название районов:
# Алмазарский район - 1
# Бектемирский район - 2
# Мирабадский район - 3
# Мирзо-Улугбекский район - 4
# Сергелийский район - 5
# Чиланзарский район - 6
# Шайхантаурский район - 7
# Юнусабадский район - 8
# Яккасарайский район - 9
# Чиланзарский район - 10
# Яшнабадский район - 11
# Учтепинский район - 12
# Загниатинский район - 13

async def sql_check(field ='', field_2 = '', table='', value ='', aditional_order = ''):
    try:
        cursor.execute(f"SELECT {field} {field_2} FROM {table} WHERE {field} = {value} {aditional_order}")
        data = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        db_connection()
        return
    return data

async def sql_show_photo (id):
    cursor.execute (f'SELECT * FROM photos WHERE fk_rent_id = {id}')
    photos = cursor.fetchall()
    return photos 


async def sql_check_number_rents (id_member):
    cursor.execute (f'SELECT number_of_rents FROM rentie WHERE id_member = {id_member}')
    data = cursor.fetchone()
    return data  


async def sql_insert_rentie_profile (state):
    async with state.proxy() as data:
        cursor.execute(f"INSERT INTO rentie (name ,id_member , telephone_number , telegram_profile, rieltor ) VALUES {tuple(data.values())}")
        conn.commit()
        # cursor.close()


async def sql_insert_new_rent ( state, id_member):
    async with state.proxy() as rent_data:
        cursor.execute (f'''INSERT INTO rent (type_of_house, rooms,price, komission, district, type_repair, apartment_area, floor, floors_in_house, description, animals, kids, fk_id_member) 
        VALUES ({rent_data ['type_of_house']}, {rent_data['rooms']} , {rent_data['price']} , {rent_data['komission']}, {rent_data['district']} , {rent_data['type_repair']}, {rent_data['apartment_area']}, {rent_data['floor']}, {rent_data['floors_in_house']} ,'{rent_data['description']}', {rent_data['animals']} , {rent_data['kids']} , {rent_data['fk_id_member']})''')
        conn.commit()
        cursor.execute (f'SELECT MAX(id) FROM rent WHERE fk_id_member = {rent_data["fk_id_member"]}')
        id_rent = cursor.fetchone()
        cursor.execute (f'UPDATE rentie SET number_of_rents=number_of_rents +1 WHERE id_member = {id_member}')
        conn.commit()
        return id_rent 


async def sql_insert_photos (id_photo, photo):
    cursor.execute (f"INSERT INTO photos VALUES ('{photo}', {id_photo})")
    conn.commit()


async def sql_update (name_of_column, value_to_change, id_of_order, id_user):
    if value_to_change.isnumeric():
        cursor.execute (f'UPDATE rent SET {name_of_column} = {value_to_change} WHERE id = {id_of_order} AND fk_id_member = {id_user}')
    else:
        cursor.execute (f"UPDATE rent SET {name_of_column} = '{value_to_change}' WHERE id = {id_of_order} AND fk_id_member = {id_user}")
    conn.commit()


async def sql_insert_user_take_house (name, tg_id):
    cursor.execute (f"INSERT INTO users (tg_id, name) VALUES ({tg_id},'{name}')")
    conn.commit()


async def sql_insert_take_order(data_take):
    cursor.execute (f'''INSERT INTO orders (type_of_house, rooms , price_min , price_max ,rieltor_show, district, type_repairs,apartment_area_min, apartment_area_max, floor, kids, animals, fk_tg_id) 
    VALUES ('{data_take['type_of_house']}','{data_take['rooms']}', {data_take['price_min']}, {data_take['price_max']}, {data_take['rieltor_show']}, '{data_take['district']}', '{data_take['type_repair']}', {data_take['area_min']}, {data_take['area_max']},'{data_take['floor']}', '{data_take['kids']}', '{data_take['animals']}', {data_take['fk_tg_id']})''')
    conn.commit()

# TODO: Запрос на поиск домов, создать запрос на выгрузку фотографий 
async def search_houses (id_member):
    cursor.execute (f'''WITH price_id AS(SELECT price_min,price_max,apartment_area_min,apartment_area_max FROM orders WHERE fk_tg_id={id_member})
                    SELECT fk_id_member, rent.* FROM rent, price_id WHERE (price BETWEEN price_id.price_min AND price_id.price_max) 
                    AND
                    (apartment_area BETWEEN price_id.apartment_area_min AND price_id.apartment_area_max)''')
    search_data =cursor.fetchall()
    return search_data


async def drop_row (id_member):
    cursor.execute (f'DELETE FROM orders WHERE fk_tg_id = {id_member}')
    conn.commit()


async def drop_photos (id_):
    cursor.execute (f'DELETE FROM photos WHERE fk_rent_id = {id_}')
    conn.commit()


async def drop_rent(id_, id_member):
    await drop_photos(id_=id_)
    cursor.execute (f'DELETE FROM rent WHERE id= {id_}')
    conn.commit()
    cursor.execute (f'UPDATE rentie SET number_of_rents=number_of_rents -1 WHERE id_member = {id_member}')
    conn.commit()


async def update_row (id_member):
    cursor.execute (f'UPDATE orders SET notify = True WHERE fk_tg_id = {id_member}')
    conn.commit()

async def update_row_nt_fls (id_member):
    cursor.execute (f'UPDATE orders SET notify = False WHERE fk_tg_id = {id_member}')
    conn.commit()



async def sql_check_rentie_name_tn (id_member):
    cursor.execute (f'SELECT name,telephone_number,telegram_profile FROM rentie WHERE id_member = {id_member}')
    data = cursor.fetchone()
    return data


async def update_order_bd (id_member, table , value):
    if type(value) == str:
        cursor.execute (f"UPDATE orders SET {table} = '{value}' WHERE fk_tg_id = {id_member}")
    else:
        cursor.execute (f'UPDATE orders SET {table} = {value} WHERE fk_tg_id = {id_member}')
    conn.commit()


def db_connection_close ():
    conn.close()
    print ('[INFO] Соединение разорвано')





async def checker_sheduler ():
    cursor.execute ('SELECT fk_tg_id, last_seen_rent FROM orders WHERE notify = true') 
    data = cursor.fetchall()
    return data

async def update_lastseen(value,id_member):
    cursor.execute(f'UPDATE orders SET last_seen_rent = {value} WHERE fk_tg_id = {id_member}') 
    conn.commit()