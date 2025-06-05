from aiogram import Router, F
from aiogram import types
from keyboards import keyboard_approved_deal
from aiogram.utils.markdown import hide_link
router = Router()
from datetime import datetime
import re
from DataBase import DataBase

def is_valid_phone_start(phone: str) -> bool:
    phone = phone.lstrip()  # Удаляем пробелы слева
    return phone.startswith(('+7', '8'))

def validate_phone_number(phone):
    # Паттерн для российских номеров (может начинаться с +7, 7, 8, код оператора и 7 цифр)
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'

    if re.match(pattern, phone):
        return True
    return False



###Доделать отправку номера
@router.callback_query(F.data.startswith("approved_"))
async def deal_approved_start(callback: types.CallbackQuery):
    message_to_user = "☎️ Для подтверждения, пожалуйста, напишите Ваш номер телефона. Наш специалист свяжется с Вами в течение 30 минут."
    ##сохранение и запись в БД???? - временная для сохранения типа услуги - + в основной таблице статус сделки!
    now = datetime.now()
    deal_type = callback.data.split('_')[1]
    print(deal_type)
    user_id = callback.from_user.id
    create_dtm = now.strftime("%Y-%m-%d %H:%M:%S")
    status = False
    tg_username = callback.from_user.username

    #функция
    await DataBase.DataBase_add_1data(user_id, deal_type, status, create_dtm, tg_username)

    #ИТОГ:
    # Сохранение в таблицу deals - сохраняем тип сделки, время, user_id
    await callback.message.answer(message_to_user)

@router.message(F.text.startswith(('+7', '8')))
async def deal_approved_number(message: types.Message):

    #Запрос из БД c данными сделки (Тип услуги по ID пользователя и самой последней записьюв БД (самая недавняя кнопка по типу сделки)

    #По вторичному ключу из таблицы deals_types
    user_id = message.from_user.id
    phone_number = message.text

    if validate_phone_number(phone_number):
        await DataBase.DataBase_add_2data(user_id, phone_number)

        #Функция получения deal_type DataBase
        deal_type_description = DataBase.DataBase_find_dealtype(user_id)
        print(deal_type_description)
        await message.answer(f"Отлично! Тип услуги: {deal_type_description}\nНомер телефона: {message.text}\nМы перезвоним вам в течение 30 минут 📞\n\nНажмите на кнопку ниже, если данные верны 👇", reply_markup=keyboard_approved_deal.approved_deal_final())
    else:
        await message.answer(f"Номер неверный, он должен начинаться с +7 или 8 и состоять из 11 цифр. Введите его еще раз")
    #Сохраняем телефон и тг по возможности с помощью UPDATE WHERE user_id = message.user.id +-


@router.callback_query(F.data == "final_deal_approved")
async def deal_approved_number(callback: types.CallbackQuery):
    #Логика сохранения в БД - Поменяем статус в основной таблице на True - подтверждена и все
    # UPDATE WHERE USER_ID = user.id AND create_date.time DESC LIMIT 1
    # SET status = true
    user_id = callback.from_user.id
    await DataBase.DataBase_approve_status(user_id)
    await callback.message.answer("Отлично, Вы записаны!\n\n"
        'Рекомендуем ознакомиться и с другими услугами на нашем <a href="https://www.forabank.ru/">официальном сайте</a>.')




