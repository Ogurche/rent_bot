
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove



async def menu_keybord():
    keybord = ReplyKeyboardMarkup( resize_keyboard=True) 
    keybord.add ('Сдать', 'Снять')
    return keybord 


async def rentier_yes_no_keybord():
    keybord = InlineKeyboardMarkup()
    keybord.add (InlineKeyboardButton('Да', callback_data='True'), InlineKeyboardButton('Нет', callback_data='False'))
    return keybord


async def create_change_show_keybord ():
    ketbord = ReplyKeyboardMarkup( resize_keyboard=True, one_time_keyboard=True )
    ketbord.add ('Создать новое предложение', 'Изменить профиль', 'Показать мои предложения','В главное меню')
    return ketbord


async def type_of_house_keybord ():
    keybord = InlineKeyboardMarkup()
    keybord.add (InlineKeyboardButton('Квартира',callback_data='1'))
    keybord.add (InlineKeyboardButton('Комната',callback_data='2'))
    keybord.add (InlineKeyboardButton('Дом',callback_data='3'))
    keybord.add (InlineKeyboardButton('◀️Назад',callback_data='back'))
    return keybord


async def rooms_keybord ( number , additional= None, adittional_data = None, additional2 = None, adittional_data2 = None):
    keybord = InlineKeyboardMarkup(row_width=2)
    for i in range (1,number +1):
        keybord.insert (InlineKeyboardButton(str(i),callback_data=str(i)))
    if additional != None:
        keybord.add (InlineKeyboardButton(f'{additional}',callback_data=adittional_data))
    if additional2 != None:
        keybord.add (InlineKeyboardButton(f'{additional2}',callback_data=adittional_data2))
    keybord.add (InlineKeyboardButton('◀️Назад',callback_data='back'))
    return keybord


async def take_rooms_keybord ( number , additional= None, adittional_data = None, additional2 = None, adittional_data2 = None):
    keybord = InlineKeyboardMarkup(row_width=2)
    for i in range (1,number +1):
        keybord.insert (InlineKeyboardButton(str(i),callback_data=str(i)))
    if additional != None:
        keybord.add (InlineKeyboardButton(f'{additional}',callback_data=adittional_data))
    if additional2 != None:
        keybord.add (InlineKeyboardButton(f'{additional2}',callback_data=adittional_data2))
    return keybord


async def district_keybord (dictionary , back = None, back_data = None, ad_b =None, ad_b_data = None):
    keybord = InlineKeyboardMarkup(row_width=2)
    for i in dictionary:
        keybord.insert (InlineKeyboardButton(dictionary[i] ,callback_data=str(i)))
    if back != None:
        keybord.add (InlineKeyboardButton(back,callback_data=back_data))
    if ad_b != None:
        keybord.add (InlineKeyboardButton(ad_b,callback_data=ad_b_data))
    return keybord


async def confirmation_keybord (dictionary ,additional_b_name = None , additional_b_data=None, add_2= None , add_2_data = None):
    keybord = InlineKeyboardMarkup(row_width=2)
    for i in dictionary:
        keybord.insert (InlineKeyboardButton(dictionary[i] ,callback_data=str(i)))
    if additional_b_name != None:
        keybord.add (InlineKeyboardButton(f'{additional_b_name}',callback_data=additional_b_data))
    if add_2 != None:
        keybord.add (InlineKeyboardButton(f'{add_2}', callback_data=add_2_data))
    return keybord


async def number_rents_keybord (number):
    keybord = ReplyKeyboardMarkup( resize_keyboard=True, one_time_keyboard=True)
    for i in range (1,number+1):
        keybord.insert (str(i))
    keybord.add ('Назад')
    return keybord


# не первый 1
# не последний 2

async def take_floor_keybord(back = None, back_data = None, skip = None, skip_data = None):
    keybord = InlineKeyboardMarkup()
    keybord.insert (InlineKeyboardButton('Не первый',callback_data='1'))
    keybord.insert (InlineKeyboardButton('Не последний',callback_data='2'))
    if skip != None:
        keybord.add (InlineKeyboardButton(skip,callback_data=skip_data))
    if back != None:
        keybord.add (InlineKeyboardButton(back,callback_data=back_data))
    return keybord


async def kids_animals_take_keybord(back = None, back_data = None, skip= None, skip_data= None):
    keybord = InlineKeyboardMarkup()
    keybord.insert (InlineKeyboardButton('C маленькими детьми',callback_data='kids'))
    keybord.insert (InlineKeyboardButton('C животными',callback_data='animals'))
    if skip != None:
        keybord.add (InlineKeyboardButton(skip,callback_data=skip_data))
    if back != None:
        keybord.add (InlineKeyboardButton(back,callback_data=back_data))
    return keybord


async def take_house_keybord_menu ():
    keybord = ReplyKeyboardMarkup( resize_keyboard=True, one_time_keyboard=True)
    keybord.add ('Создать запрос','Посмотреть мой запрос', 'В главное меню')
    return keybord


async def start_search_kbd():
    keybord = InlineKeyboardMarkup()
    keybord.insert (InlineKeyboardButton('Начать поиск',callback_data='start_search'))
    keybord.insert (InlineKeyboardButton('Изменить',callback_data='change'))
    keybord.add (InlineKeyboardButton('Отмена (в Главное меню)',callback_data='отмена'))
    return keybord


async def save_order_kbd ():
    keybord = InlineKeyboardMarkup()
    keybord.insert (InlineKeyboardButton('Сохранить поиск',callback_data='save'))
    keybord.insert (InlineKeyboardButton('Не сохранять поиск',callback_data='drop'))
    return keybord


async def delete_order_kbd ():
    keybord = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keybord.insert ('Удалить')
    keybord.insert ('Посмотреть мой запрос')
    keybord.insert ('Назад')
    return keybord

async def change_order_kbd ():
    keybord = InlineKeyboardMarkup ()
    keybord.insert (InlineKeyboardButton('Кол-во комнат',callback_data='rooms'))
    keybord.insert (InlineKeyboardButton('Бюджет',callback_data='price'))
    keybord.insert (InlineKeyboardButton('Район',callback_data='district'))
    keybord.insert (InlineKeyboardButton('Площадь жилья',callback_data='area'))
    return keybord


async def back_button_inline ():
    keybord = InlineKeyboardMarkup ()
    keybord.insert (InlineKeyboardButton('◀️Назад',callback_data='back'))
    return keybord

async def back_button_reply ():
    keybord = ReplyKeyboardMarkup (resize_keyboard=True, one_time_keyboard=True)
    keybord.insert ('Назад')
    return keybord


async def order_show_change ():
    keybord = ReplyKeyboardMarkup(resize_keyboard=True)
    keybord.add ("Да", "Нет")
    keybord.add ("Показать объявления по запросу",'Уведомления')
    return keybord


async def notify_():
    keybord = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keybord.add ('Сохранить поиск', 'Не сохранять поиск')
    return keybord



async def ban_button (admin_url):
    keybord = InlineKeyboardMarkup()
    keybord.add (InlineKeyboardButton('Пожаловаться', url= f'{admin_url}'))
    return keybord