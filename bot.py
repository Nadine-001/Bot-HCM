from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date
import time, asyncio, gspread, random

bot = AsyncTeleBot('5538226702:AAGdbNQmMSCiQS_861iti98NBh69J1UwBzI', state_storage=StateMemoryStorage())
# bot = AsyncTeleBot('5088370919:AAHa6lHh_S8jR--KGU2Y3u-D3jNV3KktfNU', state_storage=StateMemoryStorage())

# custom states
class States(StatesGroup):
    inputData = State()
    customMsg = State()

# link ke GSS
gs = gspread.service_account(filename='presensi-reminder.json')
sh = gs.open_by_key('1kNYfAQGDcZD-EcJQOfkFKErJ_QfilyQH4NwNxLAe5OM')
ws = sh.sheet1

# waktu untuk trigger pesan reminder
fiveTo = ('07:55:00', '16:55:00', '19:55:00')
exactTime = ('08:00:00', '17:00:00', '20:00:00')

# pesan reminder
fiveMins = ["Baru saja kulihat si tampan\nSelain tinggi, dia pun pandai\nPenuhi hari dengan senyuman\n📌 Yuk absensi 5 menit lagi\n\nSemangat Pagi! 🙌🏻",
            "Semangat Pagi! 🙌🏻\nSama seperti ayang yang rutin mengingatkan makan, bot ini juga akan mengingatkan kamu untuk absensi 5 menit lagi",
            "Semangat Pagi! 🙌🏻\nKamu mau aku kasih tahu sesuatu ga?\nSebenernya, 5 menit lagi waktunya absensi\nJangan lupa, ya",
            "Hai, Kak\nAku sudah lama memendam rasa ini\nTolong izinkan aku untuk mengingatkan bahwa 5 menit lagi waktunya absensi\n\nSemangat Pagi! 🙌🏻",
            "Rencang-rencang, absensi 5 menit malih, nggih\nSemangat Pagi! 🙌🏻"]
morning = ["Selamat Pagi, Semangat Pagi! 🙌🏻\nSudah jam 8 pagi, yuk buka aplikasi SUPER HANA untuk absensi",
           "Sugeng enjang\nYok rencang-rencang absensi riyen wonten aplikasi SUPER HANA\n\nSemangat Pagi! 🙌🏻",
           "Makan sate hangat-hangat\nTiba-tiba turun hujan lebat\nPagi-pagi penuh semangat 🙌🏻\nYuk absensi, sudah jam 8 tepat",
           "Semangat Pagi! 🙌🏻\nCuma mau ngingetin, jangan lupa absensi di aplikasi SUPER HANA, ya\nPastikan absensi sudah tercatat di sistem",
           "Pagi, Kak! 🙌🏻\nKakak tahu ga persamaan sarapan sama absensi di aplikasi SUPER HANA?\nIya, sama-sama penting!\nNah, jangan sampai lupa dua-duanya, ya"]
afternoon = ["Sugeng sonten\nYok rencang-rencang absensi riyen wonten aplikasi SUPER HANA\n\nSemangat Pagi! 🙌🏻",
             "Selamat Sore, Semangat Pagi! 🙌🏻\nIzin untuk mengingatkan, Kak, jangan lupa absensi di aplikasi SUPER HANA ya",
             "Sudah lama tak bertemu\nAku masih menunggumu di sini\nSemangat pagi selalu 🙌🏻\nJangan lupa absensi sore ini 📢",
             "Sore, Kak\nJangan lupa makan, ya\nJaga kesehatan dan jangan lupa juga absensi sore hari ini di aplikasi SUPER HANA, oke?",
             "Kak, ada yang mau aku omongin\nIni udah jam 5 sore, yuk buka aplikasi SUPER HANA buat absensi dulu\n\nSemangat Pagi! 🙌🏻\n"]
night = ["Banyak uang jangan dihambur\nMengasah otak bermain catur\nBuat kamu yang lagi lembur\nAbsensi dulu sebelum tidur\n\nSemangat Pagi! 🙌🏻",
         "Sugeng ndalu\nRencang-rencang ingkang lembur, absensi riyen wonten aplikasi SUPER HANA, nggih\n\nSemangat Pagi! 🙌🏻",
         "Selamat Malam, Semangat Pagi! 🙌🏻\nBuat kakak yang lagi lembur, jangan lupa absensi dulu di aplikasi SUPER HANA, ya",
         "Malam, Kak\nUdah absensi, belum?\nKalau belum, absensi dulu yaa\nJangan sampai lupa\n\nSemangat Pagi! 🙌🏻",
         "Semangat Pagi, Kakaak! 🙌🏻\nUdah jam 8 malem nih ternyata, waktunya absensi\nJangan lupa, ya!"]

@bot.message_handler(commands=['start'])
async def start(message) :
    chatID = message.chat.id
    messageID = message.from_user.id

    await bot.send_message(chatID, f'Halo, {message.from_user.first_name}! 👋🏻\
                           \n\nBot ini akan mengingatkanmu untuk absensi pada jam 8 pagi, 5 sore, dan 8 malam.\
                           \nTekan /help untuk mengetahui apa saja yang dapat dilakukan oleh bot ini.\
                           \n\nSalam Akhlak,\nFA & HCM Semarang 😉')
    
    ## print(chatID)
    
    # kolom id di GSS
    id = ws.col_values(1)

    # jika user adalah user baru
    if str(chatID) not in id :
        # menambahkan chat ID dan username ke GSS
        row = len(id) + 1
        ws.update_cell(row, 1, chatID)
        
        # memulai state inputData
        await bot.set_state(messageID, States.inputData, chatID)

        # request data ke user
        await bot.send_message(chatID, 'Server kami mendeteksi bahwa kamu adalah pengguna baru.\
                               \n\nMohon kesediaannya untuk mengisi data-data berikut:\
                               \nNama Lengkap:\nNomor Induk Karyawan:\nNomor Hp (Telegram):\
                               \n\nData dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                               \n\nContoh:\nFaizhal Rifky Alfaris\n00011122\n085566677788')

@bot.message_handler(state="*", commands='cancel')
async def cancel(message):
    id = ws.col_values(1)
    chatID = message.chat.id
    messageID = message.from_user.id

    cell = id.index(str(chatID)) + 1
    cell = ws.row_values(cell)

    if len(cell) < 3 :
        await bot.send_message(chatID, '🚫 Kamu harus melengkapi data terlebih dahulu.')
    else :
        await bot.delete_state(messageID, chatID)

@bot.message_handler(state=States.inputData)
async def inputData(message) :
    chatID = message.chat.id
    user = message.from_user.username
    messageID = message.from_user.id
    
    # kolom id di GSS
    id = ws.col_values(1)

    # data input dari user
    async with bot.retrieve_data(messageID, chatID) as data:
        data['dataUser'] = message.text.split('\n')

    # input user harus sebanyak 3 data
    if len(data['dataUser']) == 3 :
        nama = data['dataUser'][0]
        nik = data['dataUser'][1]
        nomorHp = data['dataUser'][2]
        
        # nik harus sebanyak ... digit angka dan nomor Hp harus lebih dari 10 digit angka
        if (nik.isdigit() and len(nik) == 8) and (nomorHp.isdigit() and len(nomorHp) >= 10) :
            # menambahkan atau meng-update data user di GSS
            cell = id.index(str(chatID)) + 1
            ws.update_cell(cell, 1, chatID)
            ws.update_cell(cell, 2, user)
            ws.update_cell(cell, 3, nama)
            ws.update_cell(cell, 4, "'" + nik)
            ws.update_cell(cell, 5, "'" + nomorHp)

            await bot.reply_to(message, f'Terima kasih, data telah berhasil ditambahkan ✅')

            # mengakhiri state inputData
            await bot.delete_state(messageID, chatID)

        # jika input user tidak sesuai format
        else : 
            await bot.reply_to(message, '❌ Teliti kembali data ini. Pastikan sudah sesuai format.\
                               \n\nContoh:\nFaizhal Rifky Alfaris\n00011122\n085566677788')

    # jika input user kurang atau lebih dari 3 data
    else :
        await bot.reply_to(message, '❌ Pastikan pesan ini terdiri dari 3 baris data.')

@bot.message_handler(commands=['cekData'])
async def cek(message) :
    chatID = message.chat.id

    # kolom id di GSS
    id = ws.col_values(1)
    
    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # mengambil data user berdasarkan chat ID
        cell = id.index(str(chatID)) + 1
        dataUser = ws.row_values(cell)

        # jika data user di GSS belum lengkap
        if len(dataUser) < 5 :
            for i in range(len(dataUser), 5) :
                dataUser.append('-')

        # mengirim data user
        await bot.send_message(chatID, f'Username: @{dataUser[1]}\
                                        \n\nNama: {dataUser[2]}\
                                        \n\nNomor Induk Karyawan: {dataUser[3]}\
                                        \n\nNomor Hp: {dataUser[4]}')
        await bot.send_message(chatID, '⚠️ Tekan /updateData untuk melengkapi data atau jika data tidak sesuai.')
    
    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')

# tombol "Sudah" dan "Belum"
async def answer() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Sudah', callback_data='sdh'),
               InlineKeyboardButton('Belum', callback_data='blm'))
    return markup

@bot.message_handler(commands=['updateData'])
async def update(message) :
    global chatID, messageID

    chatID = message.chat.id
    messageID = message.from_user.id
    
    # kolom id di GSS
    id = ws.col_values(1)

    # jika chat ID ada di data GSS
    if str(chatID) in id :
        await bot.send_message(chatID, 'Apakah kamu sudah melakukan pengecekkan data?', reply_markup=await answer())

    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')

# mengambil input dari tombol yang diklik user
@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call) :
    global column

    # jika user menjawab "Sudah"
    if call.data == 'sdh' :
        await bot.send_message(chatID, 'Silakan isi data-data berikut:\
                                \nNama Lengkap:\nNomor Induk Karyawan:\nNomor Hp (Telegram):\
                                \n\nData dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                                \n\nContoh:\nFaizhal Rifky Alfaris\n00011122\n085566677788')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        ## await bot.edit_message_reply_markup(inline_message_id=messageID, reply_markup=None)
        await bot.set_state(messageID, States.inputData, chatID)
    
    # jika user menjawab "Belum"
    elif call.data == 'blm' :
        await bot.send_message(chatID, '⚠️ Lakukan /cekData terlebih dahulu.')

    # -- bagian bawah ini buat custom reminder messages --
    elif call.data in ['morning', 'afternoon', 'night'] :
        await bot.send_message(chatID, '💬 Silakan kirim custom reminder absensimu.')

        # jika user ingin custom reminder absensi pagi
        if call.data == 'morning' :
            column = 6

        # jika user ingin custom reminder absensi sore
        elif call.data == 'afternoon' :
            column = 7

        # jika user ingin custom reminder absensi malam
        elif call.data == 'night' :
            column = 8
        
        # memulai state customMsg
        await bot.set_state(messageID, States.customMsg, chatID)

    # jika user tidak memilih jawaban dari inline keyboard
    else :
        await bot.send_message(chatID, '❌ Input tidak valid.')

# Pilihan "8 Pagi", "5 Sore", dan "8 Malam"
async def options() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('8 Pagi', callback_data='morning'),
               InlineKeyboardButton('5 Sore', callback_data='afternoon'),
               InlineKeyboardButton('8 Malam', callback_data='night'))
    return markup

@bot.message_handler(commands=['customMessage'])
async def customMsg(message) :
    global chatID, messageID

    chatID = message.chat.id
    messageID = message.from_user.id

    await bot.send_message(chatID, 'Pilih salah satu dari jadwal jam absensi di bawah ini.', reply_markup = await options())

@bot.message_handler(state=States.customMsg)
async def customMsg(message) :
    id = ws.col_values(1)
    chatID = message.chat.id
    messageID = message.from_user.id

    # mengambil input dari user
    async with bot.retrieve_data(messageID, chatID) as data:
        data['customMsg'] = message.text

    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # menambahkan custom reminder ke GSS
        cell = id.index(str(chatID)) + 1
        ws.update_cell(cell, column, data['customMsg'])

        await bot.send_message(chatID, 'Custom reminder berhasil diterapkan ✅')

        # mengakhiri state customMsg
        await bot.delete_state(messageID, chatID)
    
    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 User tidak ditemukan. Tekan /start.')

        # mengakhiri state customMsg
        await bot.delete_state(messageID, chatID)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

@bot.message_handler(commands=['help'])
async def help(message) :
    chatID = message.chat.id

    await bot.send_message(chatID, 'Berikut daftar command dari bot ini:\
                                    \n/start -- Memulai bot\
                                    \n/cekData -- Memeriksa data pengguna\
                                    \n/updateData -- Memperbarui data pengguna\
                                    \n/customMessage -- Custom pesan pengingat\
                                    \n/cancel -- Membatalkan proses input data')

# untuk meng-handle pesan user
@bot.message_handler()
async def anything(message) :
    chatID = message.chat.id
    await bot.send_message(chatID, 'Tekan /help untuk mengetahui apa saja yang dapat dilakukan oleh bot ini.')

async def reminder(day, time) :
    global fiveMins, morning, afternoon, night, id

    # mengambil pesan secara random dari template pesan
    randFiveMins = random.choice(fiveMins)
    randMorning = random.choice(morning)
    randAfternoon = random.choice(afternoon)
    randNight = random.choice(night)

    # hari libur
    weekend = [5, 6]

    # jika hari ini adalah hari kerja
    if day not in weekend :
        id = ws.col_values(1)
        # jika waktu absensi kurang 5 menit
        if time in fiveTo :
            for i in id[1:] :
                await bot.send_message(i, randFiveMins)

        # jika waktu absensi adalah jam 8 pagi
        elif time == exactTime[0] :
            for i in id[1:] :
                # memanggil fungsi custom
                randMorning = await custom(i, 5, randMorning)

                await bot.send_message(i, randMorning)
        
        # jika waktu absensi adalah jam 5 sore
        elif time == exactTime[1] :
            for i in id[1:] :
                # memanggil fungsi custom
                randAfternoon = await custom(i, 6, randAfternoon)

                await bot.send_message(i, randAfternoon)
        
        # jika waktu absensi adalah jam 8 malam
        elif time == exactTime[2] :
            for i in id[1:] :
                # memanggil fungsi custom
                randNight = await custom(i, 7, randNight)

                await bot.send_message(i, randNight)

async def custom(chatID, column, schedule) :
    cell = id.index(str(chatID)) + 1
    cell = ws.row_values(cell)
    if cell[column] != '-' :
        schedule = cell[column]

    return schedule

async def main() :
    while True :
        # memeriksa hari
        today = date.today()
        today = today.weekday()

        # memeriksa waktu saat ini
        currentTime = time.strftime('%H:%M:%S')

        # memanggil fungsi reminder
        await reminder(today, currentTime)

        ## print('*', currentTime, '*')
        ## print('-', today, '-')

        # waktu tunggu loop
        await asyncio.sleep(1)

# run using asynchronous mode
try :
    loop = asyncio.new_event_loop()
    loop.create_task(main(), name="Check Time")
    loop.create_task(bot.polling(), name="Bot Commands")
    loop.run_forever()
except :
    pass
