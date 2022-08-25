from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date
import time, asyncio, gspread, random

bot = AsyncTeleBot('5088370919:AAHa6lHh_S8jR--KGU2Y3u-D3jNV3KktfNU', state_storage=StateMemoryStorage())

# custom states
class States(StatesGroup):
    inputData = State()
    customMsg = State()
    addMsg = State()
    bcMsg = State()
    someUser = State()

# link ke GSS
gs = gspread.service_account(filename='presensi-reminder.json')
sh = gs.open_by_key('1kNYfAQGDcZD-EcJQOfkFKErJ_QfilyQH4NwNxLAe5OM')

# sheets excel
sheet1 = sh.worksheet("user_data")
sheet2 = sh.worksheet("template_messages")
sheet3 = sh.worksheet("custom_messages")

# chat ID admin
admin = (1372954700, 5033311508, 5142972565, 117145654, 73937262)

idDone = []

@bot.message_handler(commands=['start'])
async def start(message) :
    chatID = message.chat.id
    user = '@' + message.from_user.username

    await bot.send_message(chatID, f'Halo, {message.from_user.first_name}! 👋🏻\
                           \n\nBot ini akan mengingatkanmu untuk absensi pada jam 8 pagi, 5 sore, dan 8 malam.\
                           \nTekan /help untuk mengetahui apa saja yang dapat dilakukan oleh bot ini.\
                           \n\nSalam Akhlak,\nFA & HCM Semarang 😉')
    
    # kolom id di GSS
    id = sheet1.col_values(1)

    # jika user adalah user baru
    if str(chatID) not in id :
        # menambahkan chat ID ke GSS
        row = len(id) + 1
        sheet1.update_cell(row, 1, chatID)
        sheet3.update_cell(row, 1, chatID)
        
        # memulai state inputData
        await bot.set_state(chatID, States.inputData)

        # request data ke user
        await bot.send_message(chatID, 'Server kami mendeteksi bahwa kamu adalah pengguna baru.\
                               \n\nMohon kesediaannya untuk mengisi data-data berikut:\
                               \nNama Lengkap:\nNomor Induk Karyawan:\nNomor Hp (Telegram):\
                               \n\nData dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                               \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788')
    
    # jika user bukan user baru
    else :
        # meng-update username di GSS
        cell = id.index(str(chatID)) + 1
        sheet1.update_cell(cell, 2, user)

@bot.message_handler(state='*', commands='cancel')
async def cancel(message):
    chatID = message.chat.id

    await bot.delete_state(chatID)

# state inputData
@bot.message_handler(state=States.inputData)
async def inputData(message) :
    chatID = message.chat.id
    user = '@' + message.from_user.username
    
    # kolom id di GSS
    id = sheet1.col_values(1)

    # mengambil input dari user
    async with bot.retrieve_data(chatID) as data :
        data['dataUser'] = message.text.split('\n')

    # input user harus sebanyak 3 data
    if len(data['dataUser']) == 3 :
        nama = data['dataUser'][0]
        nik = data['dataUser'][1]
        nomorHp = data['dataUser'][2]
        
        # nik harus sebanyak 6 sampai 8 digit angka dan nomor Hp harus lebih dari 10 digit angka
        if (nik.isdigit() and len(nik) in range (6, 9)) and (nomorHp.isdigit() and len(nomorHp) >= 10) :
            # menambahkan atau meng-update data user di GSS
            cell = id.index(str(chatID)) + 1
            sheet1.update_cell(cell, 1, chatID)
            sheet1.update_cell(cell, 2, user)
            sheet1.update_cell(cell, 3, nama)
            sheet1.update_cell(cell, 4, "'" + nik)
            sheet1.update_cell(cell, 5, "'" + nomorHp)

            await bot.reply_to(message, f'Data berhasil ditambahkan ✅')

            # mengakhiri state inputData
            await bot.delete_state(chatID)

        # jika input user tidak sesuai format
        else : 
            await bot.reply_to(message, '❌ Teliti kembali data ini. Pastikan sudah sesuai format.\
                               \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788')

    # jika input user kurang atau lebih dari 3 data
    else :
        await bot.reply_to(message, '❌ Pastikan pesan ini terdiri dari 3 baris data.')

@bot.message_handler(commands=['cekData'])
async def cekData(message) :
    chatID = message.chat.id
    user = '@' + message.from_user.username

    # kolom id di GSS
    id = sheet1.col_values(1)
    
    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # mengambil data user berdasarkan chat ID
        cell = id.index(str(chatID)) + 1
        sheet1.update_cell(cell, 2, user)
        dataUser = sheet1.row_values(cell)

        # jika data user di GSS belum lengkap
        if dataUser[2] == '' :
            for i in range(2, 5) :
                dataUser[i] = '-'

        # mengirim data user
        await bot.send_message(chatID, f'— Data Pengguna —\
                                        \n\nUsername: {dataUser[1]}\
                                        \n\nNama: {dataUser[2]}\
                                        \n\nNomor Induk Karyawan: {dataUser[3]}\
                                        \n\nNomor Hp: {dataUser[4]}')
        await bot.send_message(chatID, '⚠️ Tekan /updateData untuk melengkapi data atau jika data tidak sesuai.')
    
    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')

# tombol 'Sudah' dan 'Belum'
async def answers() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Sudah', callback_data='sdh'),
               InlineKeyboardButton('Belum', callback_data='blm'))
    return markup

@bot.message_handler(commands=['updateData'])
async def updateData(message) :
    global chatID

    chatID = message.chat.id
    user = '@' + message.from_user.username
    
    # kolom id di GSS
    id = sheet1.col_values(1)

    # jika chat ID ada di data GSS
    if str(chatID) in id :
        cell = id.index(str(chatID)) + 1
        sheet1.update_cell(cell, 2, user)

        await bot.send_message(chatID, 'Apakah kamu sudah melakukan pengecekan data?', reply_markup=await answers())

    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')

# Pilihan '8 Pagi', '5 Sore', dan '8 Malam'
async def options() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('8 Pagi', callback_data='morning'),
               InlineKeyboardButton('5 Sore', callback_data='afternoon'),
               InlineKeyboardButton('8 Malam', callback_data='night'))
    return markup

@bot.message_handler(commands=['customReminder'])
async def customReminder(message) :
    global chatID

    chatID = message.chat.id

    await bot.send_message(chatID, 'Pilih salah satu dari jadwal jam absensi di bawah ini.', reply_markup = await options())

# state customMsg
@bot.message_handler(state=States.customMsg)
async def customMsg(message) :
    id = sheet3.col_values(1)
    chatID = message.chat.id

    # mengambil input dari user
    async with bot.retrieve_data(chatID) as data :
        data['customMsg'] = message.text

    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # menambahkan custom reminder ke GSS
        cell = id.index(str(chatID)) + 1
        sheet3.update_cell(cell, column, data['customMsg'])

        await bot.send_message(chatID, 'Custom reminder berhasil diterapkan ✅')

        # mengakhiri state customMsg
        await bot.delete_state(chatID)
    
    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 User tidak ditemukan. Tekan /start.')

        # mengakhiri state customMsg
        await bot.delete_state(chatID)

# Pilihan 'Kurang 5 Menit', '8 Pagi', '5 Sore', dan '8 Malam'
async def choices() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('8 Pagi', callback_data='Morning'),
               InlineKeyboardButton('5 Sore', callback_data='Afternoon'),
               InlineKeyboardButton('8 Malam', callback_data='Night'))
    return markup

@bot.message_handler(commands=['addReminder'])
async def addReminder(message) :
    global chatID

    chatID = message.chat.id

    if chatID in admin :
        await bot.send_message(chatID, 'Pilih salah satu dari jadwal reminder di bawah ini.', reply_markup = await choices())

# state addMsg
@bot.message_handler(state=States.addMsg)
async def addMsg(message) :
    template = sheet2.col_values(column)
    chatID = message.chat.id

    # mengambil input dari admin
    async with bot.retrieve_data(chatID) as data :
        data['addMsg'] = message.text
    
    try :
        # menambahkan pesan reminder baru ke GSS
        row = len(template) + 1
        sheet2.update_cell(row, column, data['addMsg'])

        await bot.send_message(chatID, 'Pesan reminder berhasil ditambahkan ✅')
    except :
        await bot.send_message(chatID, '❌ Pesan reminder gagal ditambahkan.')
    
    # mengakhiri state addMsg
    await bot.delete_state(chatID)

# tombol 'User Tertentu' dan 'Semua User'
async def selections() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('User Tertentu', callback_data='some'),
               InlineKeyboardButton('Semua User', callback_data='all'))
    return markup

@bot.message_handler(commands=['broadcast'])
async def broadcast(message) :
    global chatID

    chatID = message.chat.id

    if chatID in admin :
        await bot.send_message(chatID, 'Silakan pilih tujuan pesan broadcast di bawah ini.', reply_markup = await selections())

# state someUser
@bot.message_handler(state=States.someUser)
async def someUser(message) :
    global target, users

    chatID = message.chat.id

    # kolom id di GSS
    nik = sheet1.col_values(4)
    
    # mengambil input dari admin
    async with bot.retrieve_data(chatID) as data :
        data['someUser'] = message.text.split('\n')
    
    # mengambil chat ID user menggunakan NIK
    users = []
    for i in data['someUser'] :
        cell = nik.index(i) + 1
        dataUser = sheet3.row_values(cell)
        users.append(dataUser[0])
    
    target = 'someUser'

    await bot.send_message(chatID, 'Silakan kirim pesan broadcast untuk disiarkan.')
    await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
    
    # memulai state bcMsg
    await bot.set_state(chatID, States.bcMsg, )

# state bcMsg
@bot.message_handler(state=States.bcMsg, content_types=['text', 'photo', 'document', 'video'])
async def bcMsg(message) :
    global type

    id = sheet1.col_values(1)
    chatID = message.chat.id
    
    # mengambil input dari admin
    async with bot.retrieve_data(chatID) as data :
        # mengidentifikasi tipe pesan yang dikirim admin
        type = message.content_type
        
        if type == 'text' :
            data['broadcast'] = message.text
            ## type = 1
        elif type == 'photo' :
            data['broadcast'] = message.photo[0].file_id
            ## type = 2
        elif type == 'document' :
            data['broadcast'] = message.document.file_id
            ## type = 3
        elif type == 'video' :
            data['broadcast'] = message.video.file_id
            ## type = 4
    
    try :
        # jika broadcast akan disiarkan ke user tertertu
        if target == 'someUser' :
            # memanggil fungsi send
            await send(users, data['broadcast'], message.caption)
        
        # jika broadcast akan disiarkan ke semua user
        else :
            # memanggil fungsi send
            await send(id[1:], data['broadcast'], message.caption)
        
        await bot.send_message(chatID, 'Pesan berhasil disiarkan ✅')
    
    except :
        await bot.send_message(chatID, '❌ Pesan gagal disiarkan.')

    # mengakhiri state bcMsg
    await bot.delete_state(chatID)

# fungsi untuk mengirim broadcast ke user
async def send(target, msg, capt) :
    # mengirim pesan broadcast ke user
    for i in target :
        if type == 'text' :
            await bot.send_message(i, msg)
        elif type == 'photo' :
            await bot.send_photo(i, msg, capt)
        elif type == 'document' :
            await bot.send_document(i, msg, caption=capt)
        elif type == 'video' :
            await bot.send_video(i, msg, caption=capt)

# mengambil input dari tombol yang diklik user
@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call) :
    global column, target

    # -- BAGIAN UPDATE DATA --
    # jika user menjawab 'Sudah'
    if call.data == 'sdh' :
        await bot.send_message(chatID, 'Silakan isi data-data berikut:\
                               \nNama Lengkap:\nNomor Induk Karyawan:\nNomor Hp (Telegram):\
                               \n\nData dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                               \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        
        await bot.set_state(chatID, States.inputData)
    
    # jika user menjawab 'Belum'
    elif call.data == 'blm' :
        await bot.send_message(chatID, '⚠️ Lakukan /cekData terlebih dahulu.')

    # -- BAGIAN CUSTOM REMINDER --
    elif call.data in ['morning', 'afternoon', 'night'] :
        await bot.send_message(chatID, '💬 Silakan kirim custom reminder absensimu.')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')

        # jika user ingin custom reminder absensi pagi
        if call.data == 'morning' :
            column = 2

        # jika user ingin custom reminder absensi sore
        elif call.data == 'afternoon' :
            column = 3

        # jika user ingin custom reminder absensi malam
        elif call.data == 'night' :
            column = 4
        
        # memulai state customMsg
        await bot.set_state(chatID, States.customMsg)
    
    # -- BAGIAN ADD REMINDER (ADMIN ONLY) --
    elif call.data in ['Morning', 'Afternoon', 'Night'] :
        await bot.send_message(chatID, '💬 Silakan tambahkan pesan reminder absensi untuk semua user.')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        
        # jika admin ingin menambahkan reminder absensi pagi
        if call.data == 'Morning' :
            column = 2

        # jika admin ingin menambahkan reminder absensi sore
        elif call.data == 'Afternoon' :
            column = 3

        # jika admin ingin menambahkan reminder absensi malam
        elif call.data == 'Night' :
            column = 4
        
        # memulai state addMsg
        await bot.set_state(chatID, States.addMsg)
    
    # -- BAGIAN BROADCAST (ADMIN ONLY) --
    # jika admin ingin mengirim pesan broadcast ke user tertentu
    elif call.data == 'some' :
        await bot.send_message(chatID, 'Silakan kirim NIK user yang akan mendapatkan pesan.\
                               \nNIK user dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                               \n\nContoh:\n444567\n87765432\n98765432')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        
        # memulai state someUser
        await bot.set_state(chatID, States.someUser)
    
    # jika admin ingin mengirim pesan broadcast ke semua user
    elif call.data == 'all' :
        await bot.send_message(chatID, 'Silakan kirim pesan broadcast untuk disiarkan.')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        
        # memulai state bcMsg
        await bot.set_state(chatID, States.bcMsg)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

@bot.message_handler(commands=['cekCustom'])
async def cekCustom(message) :
    chatID = message.chat.id

    # kolom id di GSS
    id = sheet3.col_values(1)
    
    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # mengambil custom reminder user berdasarkan chat ID
        cell = id.index(str(chatID)) + 1
        dataUser = sheet3.row_values(cell)

        # mengirim custom reminder user
        await bot.send_message(chatID, f'— Custom Reminder —\
                                        \n\n8 Pagi : \n{dataUser[1]}\
                                        \n\n5 Sore : \n{dataUser[2]}\
                                        \n\n8 Malam : \n{dataUser[3]}')

        # jika user belum atau tidak membuat custom reminder
        if (dataUser[1] == '-') and (dataUser[2] == '-') and (dataUser[3] == '-') :
            await bot.send_message(chatID, '⚠️ Tekan /customReminder untuk membuat custom reminder.')
        
        # jika user sudah atau memiliki custom reminder
        else :
            await bot.send_message(chatID, '⚠️ Tekan /reset untuk menghapus semua custom remindermu.')
    
    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')

@bot.message_handler(commands=['reset'])
async def reset(message) :
    chatID = message.chat.id

    # kolom id di GSS
    id = sheet3.col_values(1)
    
    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # mengambil data user berdasarkan chat ID
        cell = id.index(str(chatID)) + 1
        for i in range(2, 5) :
            sheet3.update_cell(cell, i, '-')
        
        await bot.send_message(chatID, 'Custom reminder berhasil direset ✅')
    
    # jika chat ID tidak ada di data GSS
    else :
        await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')

@bot.message_handler(commands=['help'])
async def help(message) :
    chatID = message.chat.id
    
    command = 'Berikut daftar command dari bot ini:\
               \n/start — Memulai bot\
               \n/cekData — Mengecek data pengguna\
               \n/updateData — Memperbarui data pengguna\
               \n/customReminder — Custom pesan pengingat\
               \n/cekCustom — Mengecek custom reminder'
    
    # jika user adalah admin
    if chatID in admin :
        await bot.send_message(chatID, f'{command}\
                               \n/addReminder — Menambahkan pesan reminder\
                               \n/broadcast — Menyiarkan pesan ke semua pengguna')
    
    # jika user bukan admin
    else :
        await bot.send_message(chatID, command)

# untuk mengatasi pesan user selain yang ada di daftar command
@bot.message_handler()
async def anything(message) :
    chatID = message.chat.id
    await bot.send_message(chatID, 'Tekan /help untuk mengetahui apa saja yang dapat dilakukan oleh bot ini.')

# fungsi untuk mengirim reminder absensi ke user
async def reminder(day, time) :
    global id, idDone

    # template messages
    morning = sheet2.col_values(2)
    afternoon = sheet2.col_values(3)
    night = sheet2.col_values(4)

    # hari libur
    weekend = [5, 6]
    
    # jika hari ini adalah hari kerja
    if day not in weekend :
        id = sheet3.col_values(1)
        
        # jika waktu absensi adalah jam 8 pagi
        if time == '08:00' :
            # mengambil pesan secara acak dari template message
            randMorning = random.choice(morning[1:])

            # memanggil fungsi reminderMsg
            await reminderMsg(randMorning, 1)
        
        # jika waktu absensi adalah jam 5 sore
        elif time == '17:00' :
            # mengambil pesan secara acak dari template message
            randAfternoon = random.choice(afternoon[1:])

            # memanggil fungsi reminderMsg
            await reminderMsg(randAfternoon, 2)
        
        # jika waktu absensi adalah jam 8 malam
        elif time == '20:00' :
            # mengambil pesan secara acak dari template message
            randNight = random.choice(night[1:])

            # memanggil fungsi reminderMsg
            await reminderMsg(randNight, 3)

        print('#', len(idDone), '#')
        print('~', len(id[1:]), '~')
        
        # mereset list idDone jika semua user sudah menerima reminder
        if len(idDone) == len(id[1:]) :
            idDone = []
        
        print('#', len(idDone), '#')
        print('~', len(id[1:]), '~')
        
    # mereset list idDone pada hari libur
    else :
        idDone = []

# fungsi untuk memeriksa custom reminder di GSS
# dan mengirim pesan reminder ke user
async def reminderMsg(randomMsg, column) :
    # kolom id di GSS
    id = sheet3.col_values(1)
    
    for i in id[1:] :
        # jika chat ID belum mendapatkan reminder
        if i not in idDone :
            cell = id.index(str(i)) + 1
            dataUser = sheet3.row_values(cell)

            # memeriksa custom reminder user
            if dataUser[column] != '-' :
                randomMsg = dataUser[column]

            try :
                await bot.send_message(i, randomMsg)

            except :
                print(f"User {i} blocked me, Sir.\n")

            # menambahkan chat ID ke list idDone
            idDone.append(i)
    
async def main() :
    while True :
        # memeriksa hari
        today = date.today()
        today = today.weekday()

        # memeriksa waktu saat ini
        currentTime = time.strftime('%H:%M')

        # memanggil fungsi reminder
        await reminder(today, currentTime)

        second = time.strftime('%S')
        second = int(second)

        clock = time.strftime('%H:%M:%S')
        print('*', clock, '*')
        print('—', today, '—')
        print()

        # waktu tunggu loop
        await asyncio.sleep(60 - second)

# run using asynchronous mode
try :
    loop = asyncio.new_event_loop()
    loop.create_task(main(), name='Time Checking')
    loop.create_task(bot.polling(), name='Bot Commands')
    loop.run_forever()
except :
    pass
