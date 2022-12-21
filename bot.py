# IMPORT LIBRARY YANG DIBUTUHKAN
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import asyncio_filters
from datetime import date, datetime
import time, asyncio, gspread, random
from fpdf import FPDF

# TOKEN BOT
token = '5088370919:AAHa6lHh_S8jR--KGU2Y3u-D3jNV3KktfNU'
bot = AsyncTeleBot(token, state_storage=StateMemoryStorage())

# CUSTOM STATES
class States(StatesGroup):
    inputData = State()
    customMsg = State()
    addMsg = State()
    bcMsg = State()
    someUser = State()
    baAbsen = State()

# MENGHUBUNGKAN KE GSS
gs = gspread.service_account(filename='presensi-reminder.json')
sh = gs.open_by_key('1kNYfAQGDcZD-EcJQOfkFKErJ_QfilyQH4NwNxLAe5OM')

# SHEETS GSS
sheet1 = sh.worksheet("user_data")
sheet2 = sh.worksheet("template_messages")
sheet3 = sh.worksheet("custom_messages")
sheet4 = sh.worksheet("absen_karyawan")
sheet5 = sh.worksheet("exp_date_absen")

# NAMA NAMA BULAN UNTUK TANGGAL DI BA ABSEN
months = ('Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
          ' Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember')

# CHAT ID ADMIN (ARINA, MIDAH, NESSA, MAS FAIZHAL, MAS BAGAS)
admin = (1372954700, 5033311508, 5142972565, 117145654, 116126490)

# COMMAND /START
@bot.message_handler(commands=['start'])
async def start(message) :
    # CHAT ID USER
    chatID = message.chat.id

    try :
        # USERNAME USER
        user = '@' + message.from_user.username
    except :
        # BOT MEMBERITAHU USER
        await bot.send_message(chatID, f'_Username_ tidak terdeteksi.\
                                       \nHarap _setting_ *username* terlebih dahulu.', 'Markdown')

    try :
        # KOLOM ID DI GSS
        id = sheet1.col_values(1)

        # JIKA USER ADALAH USER BARU
        if str(chatID) not in id :
            try :
                # BOT MEMBALAS COMMAND USER
                await bot.send_message(chatID, f'Halo, {message.from_user.first_name}! 👋🏻\
                                            \n\nBot ini akan mengingatkanmu untuk absensi pada jam 8 pagi, 5 sore, dan 8 malam.\
                                            \n\nSalam Akhlak,\nFA & HCM Semarang 😉')

                # LOG BOT
                print(f'New user ({chatID}) started me, Sir.')

            except :
                # LOG BOT JIKA TERJADI ERROR
                print(f"I can't reply to a new user ({chatID}), Sir.")

            # MENAMBAHKAN CHAT ID DAN USERNAME KE GSS
            row = len(id) + 1
            sheet1.update_cell(row, 1, chatID)
            sheet1.update_cell(row, 2, user)
            sheet3.update_cell(row, 1, chatID)
            for i in range(2, 6) :
                sheet3.update_cell(row, i, '-')

            try :
                # BOT REQUEST DATA KE USER
                await bot.send_message(chatID, 'Server kami mendeteksi bahwa kamu adalah pengguna baru.\
                                                \n\nMohon kesediaannya untuk mengisi data-data berikut.\
                                                \n\n*Nama Lengkap:*\n*Nomor Induk Karyawan:*\n*Nomor Hp (Telegram):*\
                                                \n\n_Data dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter)._\
                                                \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788',
                                                'Markdown')
                
                # MEMULAI STATE INPUTDATA
                await bot.set_state(chatID, States.inputData)
                
            except :
                # LOG BOT JIKA TERJADI ERROR
                print(f"I'm not able to ask data to a new user ({chatID}), Sir.")
        
        # JIKA USER BUKAN USER BARU
        else :
            # LOG BOT
            print(f'A user ({chatID}) greetings to me, Sir.')

            # UPDATE USERNAME USER DI GSS
            cell = id.index(str(chatID)) + 1
            sheet1.update_cell(cell, 2, user)

            # DATA DIRI USER DI GSS
            dataUser = sheet1.row_values(cell)

            # JIKA DATA DIRI USER KURANG
            if len(dataUser) < 5 :
                try :
                    # BOT REQUEST DATA KE USER
                    await bot.send_message(chatID, 'Server kami mendeteksi bahwa kamu belum melengkapi data pengguna.\
                                                    \n\nMohon kesediaannya untuk mengisi data-data berikut.\
                                                    \n\n*Nama Lengkap:*\n*Nomor Induk Karyawan:*\n*Nomor Hp (Telegram):*\
                                                    \n\n_Data dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter)._\
                                                    \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788',
                                                    'Markdown')

                    # MEMULAI STATE INPUTDATA
                    await bot.set_state(chatID, States.inputData)

                except :
                    # LOG BOT JIKA TERJADI ERROR
                    print(f"I'm not able to ask data to the user ({chatID}), Sir.")

            # JIKA DATA USER SUDAH LENGKAP  
            else :
                try :
                    # BOT MENYAPA USER DAN MENAMPILKAN DAFTAR COMMANDS
                    await bot.send_message(chatID, f'Halo, {message.from_user.first_name}! 👋🏻')
                    await help(message)

                except :
                    # LOG BOT JIKA TERJADI ERROR
                    print(f"I'm not able to ask data to the user ({chatID}), Sir.")

    except :
        # LOG BOT JIKA TERJADI ERROR
        print("Something went wrong, Sir.")

# COMMAND /CANCEL
@bot.message_handler(state='*', commands=['cancel'])
async def cancel(message):
    # CHAT ID USER 
    chatID = message.chat.id
    
    # MEMERIKSA STATE USER SAAT INI
    state = await bot.get_state(chatID)

    # JIKA USER BERADA DI SEBUAH STATE 
    if state != None :
        try :
            # BOT MEMBATALKAN STATE
            await bot.delete_state(chatID)
            await bot.send_message(chatID, 'Berhasil membatalkan proses ✔️\n\nApa yang ingin kamu lakukan selanjutnya?\
                                            \nTekan /help untuk mengetahui daftar command bot ini.')
                                            
        except :
            # LOG BOT JIKA TERJADI ERROR
            print(f"I can't delete the state of user ({chatID}), Sir.")
    
    # JIKA USER TIDAK BERADA DI SEBUAH STATE
    else :
        try :
            # BOT MEMBALAS USER
            await bot.send_message(chatID, 'Tidak ada proses yang perlu dibatalkan.\
                                            \n\nTekan /help untuk mengetahui daftar command bot ini.')
            
        except :
            # LOG BOT JIKA TERJADI ERROR
            print(f"I can't reply to the user ({chatID}), Sir.")

# STATE /INPUTDATA
@bot.message_handler(state=States.inputData)
async def inputData(message) :
    chatID = message.chat.id

    try :
        # USERNAME USER
        user = '@' + message.from_user.username
    except :
        # BOT MEMBERITAHU USER
        await bot.send_message(chatID, f'_Username_ tidak terdeteksi.\
                                       \nHarap _setting_ *username* terlebih dahulu.', 'Markdown')

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

            try :
                await bot.reply_to(message, f'Data berhasil ditambahkan ✅\
                                            \n\nTekan /help untuk mengetahui daftar command bot ini.')

                # mengakhiri state inputData
                await bot.delete_state(chatID)

            except :
                print(f"I can't reply to the user ({chatID}), Sir.")

        # jika input user tidak sesuai format
        else :
            try :
                await bot.reply_to(message, '❌ Teliti kembali data ini. Pastikan sudah sesuai format.\
                                            \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788')
            except :
                print(f"I can't reply to the user ({chatID}), Sir.")

    # jika input user kurang atau lebih dari 3 data
    else :
        try :
            await bot.reply_to(message, '❌ Pastikan pesan ini terdiri dari 3 baris data.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")

# COMMAND /CEKDATA
@bot.message_handler(commands=['cekdata'])
async def cekData(message) :
    chatID = message.chat.id

    try :
        # USERNAME USER
        user = '@' + message.from_user.username
    except :
        # BOT MEMBERITAHU USER
        await bot.send_message(chatID, f'_Username_ tidak terdeteksi.\
                                       \nHarap _setting_ *username* terlebih dahulu.', 'Markdown')

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

        try :
            # mengirim data user
            await bot.send_message(chatID, f'*— Data Pengguna —*\
                                            \n\nUsername: {dataUser[1]}\
                                            \n\nNama: {dataUser[2]}\
                                            \n\nNomor Induk Karyawan: {dataUser[3]}\
                                            \n\nNomor Hp: {dataUser[4]}',
                                            'Markdown')
            await bot.send_message(chatID, '⚠️ Tekan /updatedata untuk melengkapi data atau jika data tidak sesuai.')
            
        except :
            print(f"I can't send data of the user ({chatID}), Sir.")
    
    # jika chat ID tidak ada di data GSS
    else :
        try :
            await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")

# PILIHAN 'SUDAH' DAN 'BELUM' UNTUK COMMAND /UPDATEDATA
async def answers() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Sudah', callback_data='sdh'),
               InlineKeyboardButton('Belum', callback_data='blm'))
    return markup

# COMMAND /UPDATEDATA
@bot.message_handler(commands=['updatedata'])
async def updateData(message) :
    global chatID

    chatID = message.chat.id

    try :
        # USERNAME USER
        user = '@' + message.from_user.username
    except :
        # BOT MEMBERITAHU USER
        await bot.send_message(chatID, f'_Username_ tidak terdeteksi.\
                                       \nHarap _setting_ *username* terlebih dahulu.', 'Markdown')
    
    # kolom id di GSS
    id = sheet1.col_values(1)

    # jika chat ID ada di data GSS
    if str(chatID) in id :
        cell = id.index(str(chatID)) + 1
        sheet1.update_cell(cell, 2, user)

        try :
            await bot.send_message(chatID, 'Apakah kamu sudah melakukan pengecekan data?', reply_markup=await answers())
        except :
            print(f"I'm not able to ask the user ({chatID}), Sir.")

    # jika chat ID tidak ada di data GSS
    else :
        try :
            await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")

# PILIHAN '8 PAGI', '5 SORE', DAN '8 MALAM' UNTUK COMMAND /CUSTOMREMINDER
async def options() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('8 Pagi', callback_data='morning'),
               InlineKeyboardButton('5 Sore', callback_data='afternoon'),
               InlineKeyboardButton('8 Malam', callback_data='night'))
    return markup

# COMMAND /CUSTOMREMINDER
@bot.message_handler(commands=['customreminder'])
async def customReminder(message) :
    global chatID

    chatID = message.chat.id

    try :
        await bot.send_message(chatID, 'Pilih salah satu dari jadwal jam absensi di bawah ini.', reply_markup=await options())
    except :
        print(f"I'm not able to ask the user ({chatID}), Sir.")

# STATE CUSTOMMSG UNTUK MENERIMA INPUT PESAN CUSTOM REMINDER
@bot.message_handler(state=States.customMsg)
async def customMsg(message) :
    id = sheet3.col_values(1)
    chatID = message.chat.id

    # mengambil input dari user
    async with bot.retrieve_data(chatID) as data :
        data['customMsg'] = message.text

    # jika chat ID ada di data GSS
    if str(chatID) in id[1:] :
        # menambahkan custom reminder ke GSS
        cell = id.index(str(chatID)) + 1
        sheet3.update_cell(cell, column, data['customMsg'])

        try :
            await bot.send_message(chatID, 'Custom reminder berhasil diterapkan ✅\
                                            \n\nTekan /help untuk mengetahui daftar command bot ini.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")
    
    # jika chat ID tidak ada di data GSS
    else :
        try :
            await bot.send_message(chatID, '🚫 User tidak ditemukan. Tekan /start.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")

    # mengakhiri state customMsg
    await bot.delete_state(chatID)

# PILIHAN 'AKTIFKAN' DAN 'NONAKTIFKAN' UNTUK COMMAND /WEEKENDREMINDER
# async def weekend() :
#     markup = InlineKeyboardMarkup()
#     markup.row_width = 2
#     markup.add(InlineKeyboardButton('Aktifkan', callback_data='on'),
#                InlineKeyboardButton('Nonaktifkan', callback_data='off'))
#     return markup

# @bot.message_handler(commands=['weekendreminder'])
# async def weekendReminder(message) :
#     global chatID

#     chatID = message.chat.id

#     try :
#         await bot.send_message(chatID, 'Kamu ingin mengaktifkan atau menonaktifkan reminder untuk akhir pekan?', reply_markup=await weekend())
#     except :
#         print(f"I'm not able to ask the user ({chatID}), Sir.")

# PILIHAN 'HCM' DAN 'FA/FX' UNTUK COMMAND /HCM_HELPDESK
async def question() :
    id = sheet1.col_values(1)
    username = sheet1.col_values(2)

    hcm = id.index(str(admin[4]))
    hcm = username[hcm]
    
    fa = id.index(str(admin[3]))
    fa = username[fa]

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('HCM', f'https://t.me/{hcm[1:]}'),
               InlineKeyboardButton('FA/FX', f'https://t.me/{fa[1:]}'))
    return markup

# COMMAND /HCM_HELPDESK
@bot.message_handler(commands=['hcm_helpdesk'])
async def hcm_helpdesk(message) :
    global chatID

    chatID = message.chat.id

    try :
        await bot.send_message(chatID, 'Silakan pilih topik pertanyaanmu.', reply_markup=await question())
    except :
        print(f"I'm not able to ask the user ({chatID}), Sir.")

# PILIHAN '8 PAGI', '5 SORE', DAN '8 MALAM' UNTUK COMMAND /ADDREMINDER
async def choices() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('8 Pagi', callback_data='Morning'),
               InlineKeyboardButton('5 Sore', callback_data='Afternoon'),
               InlineKeyboardButton('8 Malam', callback_data='Night'))
    return markup

# COMMAND /ADDREMINDER
@bot.message_handler(commands=['addreminder'])
async def addReminder(message) :
    global chatID

    chatID = message.chat.id

    if chatID in admin :
        try :
            await bot.send_message(chatID, 'Pilih salah satu dari jadwal reminder di bawah ini.', reply_markup=await choices())
        except :
            print(f"I'm not able to ask the admin ({chatID}), Sir.")

# STATE ADDMSG UNTUK MENERIMA INPUT TEMPLATE PESAN
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

        await bot.send_message(chatID, 'Pesan reminder berhasil ditambahkan ✅\
                                        \n\nTekan /help untuk mengetahui daftar command bot ini.')
    except :
        await bot.send_message(chatID, '❌ Pesan reminder gagal ditambahkan.')
    
    # mengakhiri state addMsg
    await bot.delete_state(chatID)

# PILIHAN 'USER TERTENTU' DAN 'SEMUA USER' UNTUK COMMAND /BROADCAST
async def selections() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('User Tertentu', callback_data='some'),
               InlineKeyboardButton('Semua User', callback_data='all'))
    return markup

# COMMAND /BROADCAST
@bot.message_handler(commands=['broadcast'])
async def broadcast(message) :
    global chatID

    chatID = message.chat.id

    if chatID in admin :
        try :
            await bot.send_message(chatID, 'Silakan pilih tujuan pesan broadcast di bawah ini.', reply_markup=await selections())
        except :
            print(f"I'm not able to ask the admin ({chatID}), Sir.")

# PILIHAN 'HCM' DAN 'FA' UNTUK JENIS INFO BROADCAST
async def ask() :
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('HCM', callback_data='hcm'),
               InlineKeyboardButton('FA', callback_data='fa'))
    return markup

# STATE SOMEUSER UNTUK MENERIMA NIK USER DARI ADMIN
@bot.message_handler(state=States.someUser)
async def someUser(message) :
    global target, users, niks, names, failedUsers

    target = 'some'

    nik = sheet1.col_values(4)
    chatID = message.chat.id

    # mengambil input dari admin
    async with bot.retrieve_data(chatID) as data :
        data['someUser'] = message.text.split('\n')
    
    # mengambil chat ID user menggunakan NIK
    users = []
    niks = []
    names = []
    failedUsers = []

    for i in data['someUser'] :
        try :
            cell = nik.index(i) + 1
            dataUser = sheet1.row_values(cell)
            users.append(dataUser[0])
            names.append(dataUser[2])
            niks.append(dataUser[3])
        except :
            failedUsers.append(i)

    try :
        await bot.send_message(chatID, 'Silakan kirim pesan broadcast untuk disiarkan.')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        
        # memulai state bcMsg
        await bot.set_state(chatID, States.bcMsg)

    except :
        print(f"I'm not able to ask the admin ({chatID}), Sir.")

# STATE BCMSG UNTUK BROADCAST KE PENGGUNA
@bot.message_handler(state=States.bcMsg, content_types=['text', 'photo', 'document', 'video'])
async def bcMsg(message) :
    global type, count, target, names, niks

    chatID = message.chat.id
    
    # mengambil input dari admin
    async with bot.retrieve_data(chatID) as data :
        # mengidentifikasi tipe pesan yang dikirim admin
        type = message.content_type
        
        if type == 'photo' :
            data['broadcast'] = message.photo[0].file_id
        elif type == 'document' :
            data['broadcast'] = message.document.file_id
        elif type == 'video' :
            data['broadcast'] = message.video.file_id
    
    # jika broadcast akan disiarkan ke user tertertu
    if target == 'some' :
        if type == 'text' :
            # memanggil fungsi text
            await text(users, names, niks, message.text)

        else :        
            # memanggil fungsi send
            await send(users, data['broadcast'], message.caption)

        if bool(failedUsers) :
            try :
                await bot.send_message(chatID, f'Pengguna dengan NIK : {failedUsers} tidak ditemukan ‼️')
            except :
                print(f"I'm not able to message the admin ({chatID}), Sir.")

    # jika broadcast akan disiarkan ke semua user
    else :
        id = sheet1.col_values(1)
        id = id[1:]

        names = sheet1.col_values(3)
        names = names[1:]

        niks = sheet1.col_values(4)
        niks = niks[1:]

        if len(names) < len(id) :
            for i in range(0, len(id) - len(names)) :
                names.append('')
                niks.append('')

        if type == 'text' :
            # memanggil fungsi text
            await text(id, names, niks, message.text)

        else :                
            # memanggil fungsi send
            await send(id, data['broadcast'], message.caption)
    
    if count > 0 :
        try :
            await bot.send_message(chatID, f'Pesan berhasil disiarkan ke {count} pengguna ✅\
                                        \n\nApa yang ingin kamu lakukan selanjutnya?\
                                        \nTekan /help untuk mengetahui daftar command bot ini.')
            
            count = 0

        except :
            print(f"I'm not able to message the admin ({chatID}), Sir.")

    else :
        try :
            await bot.send_message(chatID, '❌ Pesan gagal disiarkan.')
        except :
            print(f"I'm not able to message the admin ({chatID}), Sir.")

    # mengakhiri state bcMsg
    await bot.delete_state(chatID)

# FUNGSI UNTUK MENGIRIM BROADCAST BERUPA TEKS KE USER
async def text(targets, identity1, identity2, message) :
    global count
    
    blocker = []
    count = 0

    for i in range(0, len(targets)) :
        msg = f'{header}\
                \nSemangat Pagi !!!\
                \nKepada sdr. {identity1[i]} / NIK. {identity2[i]}\
                \n{message}'

        try :
            count += 1
            await bot.send_message(targets[i], msg, 'Markdown')
        except :
            blocker.append(targets[i])
    
    if bool(blocker) :
        try :
            await bot.send_message(chatID, f'Pengguna dengan chat ID : {blocker} memblokir bot ini ‼️')
        except :
            print(f"I'm not able to message the admin ({chatID}), Sir.")

# FUNGSI UNTUK MENGIRIM BROADCAST SELAIN TEKS KE USER
async def send(targets, msg, capt) :
    global count

    blocker = []
    count = 0

    # mengirim pesan broadcast ke user
    for i in targets :
        count += 1
        try :
            if type == 'photo' :
                await bot.send_photo(i, msg, capt)
            elif type == 'document' :
                await bot.send_document(i, msg, caption=capt)
            elif type == 'video' :
                await bot.send_video(i, msg, caption=capt)
                
        except :
            blocker.append(i)
    
    if bool(blocker) :
        try :
            await bot.send_message(chatID, f'User : {blocker} memblokir bot ini ‼️')
        except :
            print(f"I can't send message to the admin ({chatID}), Sir.")

# mengambil input dari tombol yang diklik user
@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call) :
    global column, target, header

    # -- BAGIAN UPDATE DATA --
    # jika user menjawab 'Sudah'
    if call.data == 'sdh' :
        try :
            await bot.send_message(chatID, 'Silakan isi data-data berikut.\
                                \n*Nama Lengkap:*\n*Nomor Induk Karyawan:*\n*Nomor Hp (Telegram):*\
                                \n\nData dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                                \n\nContoh:\nFaizhal Rifky Alfaris\n934567\n085566677788',
                                'Markdown')
            await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
            
            await bot.set_state(chatID, States.inputData)

        except :
            print(f"I can't send message to the user ({chatID}), Sir.")
    
    # jika user menjawab 'Belum'
    elif call.data == 'blm' :
        try :
            await bot.send_message(chatID, '⚠️ Lakukan /cekdata terlebih dahulu.')
        except :
            print(f"I can't send message to the user ({chatID}), Sir.")

    # -- BAGIAN CUSTOM REMINDER --
    elif call.data in ['morning', 'afternoon', 'night'] :
        try :
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

        except :
            print(f"I can't send message to the user ({chatID}), Sir.")
    
    # -- BAGIAN ADD REMINDER (ADMIN ONLY) --
    elif call.data in ['Morning', 'Afternoon', 'Night'] :
        try :
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
            
        except :
            print(f"I can't send message to the user ({chatID}), Sir.")
    
    # -- BAGIAN BROADCAST (ADMIN ONLY) --
    # jika admin ingin mengirim pesan broadcast ke user tertentu
    elif call.data in ['some', 'all'] :
        try :
            await bot.send_message(chatID, 'Silakan pilih jenis informasi pesan yang ingin disampaikan.', reply_markup=await ask())
        except :
            print(f"I'm not able to ask the admin ({chatID}), Sir.")

        # menentukan target pesan broadcast
        target = call.data
    
    elif call.data in ['hcm', 'fa'] :
        if call.data == 'hcm' :
            header = '‼️ INFO HCM ‼️\n'
        elif call.data == 'fa' :
            header = '‼️ INFO FIBER ACADEMY ‼️\n'
        
        if target == 'some' :
            try :
                await bot.send_message(chatID, 'Silakan kirim *NIK* user yang akan mendapatkan pesan.\
                                                \n_NIK user dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter)._\
                                                \n\nContoh:\n444567\n87765432\n98765432', 'Markdown')
                await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
                
                # memulai state someUser
                await bot.set_state(chatID, States.someUser)

            except :
                print(f"I can't send message to the admin ({chatID}), Sir.")
        
        elif target == 'all' :
            try :
                await bot.send_message(chatID, 'Silakan kirim pesan broadcast untuk disiarkan ke semua pengguna.')
                await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
                
                # memulai state bcMsg
                await bot.set_state(chatID, States.bcMsg)

            except :
                print(f"I can't send message to the admin ({chatID}), Sir.")

    # -- BAGIAN WEEKEND REMINDER --
    # jika user ingin mengaktifkan weekend reminder
    # elif call.data in ['on', 'off'] :
    #     id = sheet3.col_values(1)
    #     cell = id.index(str(chatID)) + 1

    #     if call.data == 'on' :
    #         sheet3.update_cell(cell, 5, call.data)
    #         await bot.send_message(chatID, 'Berhasil mengaktifkan reminder untuk akhir pekan ✅\
    #                                         \nApa yang ingin kamu lakukan selanjutnya?\
    #                                         \n\nTekan /help untuk mengetahui daftar command bot ini.')

    #     # jika user ingin menonaktifkan weekend reminder
    #     elif call.data == 'off' :
    #         sheet3.update_cell(cell, 5, '-')
    #         await bot.send_message(chatID, 'Berhasil menonaktifkan reminder untuk akhir pekan ✅\
    #                                         \nApa yang ingin kamu lakukan selanjutnya?\
    #                                         \n\nTekan /help untuk mengetahui daftar command bot ini.')

# COMMAND /BA_ABSEN
@bot.message_handler(commands=['ba_absen'])
async def BAabsen(message) :
    chatID = message.chat.id
    
    try :
        await bot.send_message(chatID, 'Silakan isi data-data berikut.\
                                        \n*Jabatan:*\n*Lokasi Kerja:*\n*Tanggal Absen:*\
                                        \n*Jabatan Atasan (SM/Manager):*\n*Nama Atasan:*\n*NIK Atasan:*\
                                        \n\nData dikirim dalam satu pesan yang dipisahkan oleh baris baru (Enter).\
                                        \n\nContoh:\nDeveloper\nTelkom Akses Singotoro\n27 September 2022\nMgr\nFaizhal Rifky Alfaris\n934567',
                                        'Markdown')
        await bot.send_message(chatID, '⚠️ Tekan /cancel untuk membatalkan proses.')
        
        await bot.set_state(chatID, States.baAbsen)

    except :
        print(f"I can't ask the user ({chatID}), Sir.")

# STATE BAABSEN UNTUK MENERIMA INPUT DARI USER
@bot.message_handler(state=States.baAbsen)
async def baAbsen(message) :
    chatID = message.chat.id

    id = sheet1.col_values(1)
    nama = sheet1.col_values(3)
    nik = sheet1.col_values(4)

    cell = id.index(str(chatID))
    nama_pegawai = nama[cell]
    nik_pegawai = nik[cell]

    # mengambil input dari user
    async with bot.retrieve_data(chatID) as data :
        data['baAbsen'] = message.text.split('\n')
    
    # input user harus sebanyak 6 data
    if len(data['baAbsen']) == 6 :
        jabatan_pegawai = data['baAbsen'][0]
        lokasi_kerja = data['baAbsen'][1]
        tanggal_absen = data['baAbsen'][2]
        jabatan_atasan = data['baAbsen'][3]
        nama_atasan = data['baAbsen'][4]
        nik_atasan = data['baAbsen'][5]

        pegawai = [nama_pegawai, nik_pegawai, jabatan_pegawai, lokasi_kerja, tanggal_absen]
        atasan = [jabatan_atasan, nama_atasan, nik_atasan]

        identity = ['Nama', 'NIK', 'Jabatan', 'Lokasi Kerja', 'Tanggal Absen']

        reason = ['a. Telat input tiket',
                'b. Telat approve tiket oleh atasan',
                'c. Langsung ke tempat dinas/bekerja (non SPPD)',
                'd. Sudah absen, tapi tidak tercatat di SUPERHANA', 
                'e. Dll, sebutkan ...........................................................']

        documents = ['1. Penyesuaian data absensi',
                    '2. Proses pembayaran payroll',
                    '3. Pengajuan usulan karier',
                    '4. Proses perpanjangan kontrak']

        tanggal = datetime.now()
        month = datetime.strptime(str(tanggal.month), "%m").strftime("%B")

        def iter(r, ls) :
            for i in range(0, r) :
                pdf.cell(0, 7, f'                 {ls[i]}', ln=1)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(20, 20, 20)
        pdf.set_font('Times', 'B', 12)
        pdf.cell(200, 12, 'SURAT PERNYATAAN', ln=1, align='C')
        pdf.set_font('Times', size=12)
        pdf.ln(2)
        pdf.cell(0, 10, 'Yang bertanda tangan di bawah ini menyatakan benar ada absen kosong pada :', ln=1)
        pdf.ln(1)
        for i in range(0, 5) :
            pdf.cell(50, 7, f'                {identity[i]}')
            pdf.cell(5, 7, ':')
            pdf.cell(0, 7, f'{pegawai[i]}', ln=1)
        pdf.ln(2)
        pdf.cell(0, 10, 'Dengan alasan (pilih salah satu) :', ln=1)
        pdf.ln(2)
        iter(5, reason)
        pdf.ln(2.5)
        pdf.multi_cell(0, 7, 'Untuk selanjutnya bersedia menerima sanksi administrasi sesuai dengan peraturan perusahaan yang berlaku terkait absensi karyawan Telkom Akses.')
        pdf.ln(2)
        pdf.cell(0, 10, 'Surat pernyataan ini dibuat sebagai dokumen pendukung salah satu atau beberapa proses berikut :', ln=1)
        pdf.ln(2)
        iter(4, documents)
        pdf.ln(2)
        pdf.multi_cell(0, 7, 'Demikian surat pernyataan ini dibuat dengan sesungguhnya dan untuk dipergunakan sebagaimana mestinya.')
        pdf.ln(7)
        pdf.cell(0, 10, f'Semarang, {tanggal.day} {months[tanggal.month - 1]} {tanggal.year}', ln=1, align='R')
        pdf.ln(7)
        pdf.set_font('Times', 'B', 12)
        pdf.cell(72, 7, 'Mengetahui,', align='C')
        pdf.cell(20, 7)
        pdf.cell(72, 7, 'Yang Membuat,', ln=1, align='C')
        pdf.cell(72, 7, f'{atasan[0]}', align='C')
        pdf.cell(20, 7)
        pdf.cell(72, 7, f'{pegawai[2]}', ln=1, align='C')
        pdf.ln(30)
        pdf.cell(72, 7, f'{atasan[1]}', align='C')
        pdf.cell(20, 7)
        pdf.cell(72, 7, f'{pegawai[0]}', ln=1, align='C')
        pdf.cell(72, 7, f'NIK. {atasan[2]}', align='C')
        pdf.cell(20, 7)
        pdf.cell(72, 7, f'NIK. {pegawai[1]}', ln=1, align='C')
        pdf.output(f'BA Absen_{pegawai[0]}.pdf')

        file = open(f'BA Absen_{pegawai[0]}.pdf', 'rb')

        try :
            await bot.send_document(chatID, file, caption='Silakan periksa kembali data pada file ini.\
                                                            \nJika terjadi ketidaksesuaian pada nama dan NIK pegawai, silakan lakukan /updatedata')

        except :
            print(f"I can't send the document to the user ({chatID}), Sir.")
        
        await bot.delete_state(chatID)
        
    # jika input user kurang atau lebih dari 6 data
    else :
        try :
            await bot.reply_to(message, '❌ Pastikan pesan ini terdiri dari 6 baris data.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")

# COMMAND /CEKCUSTOM
@bot.message_handler(commands=['cekcustom'])
async def cekCustom(message) :
    chatID = message.chat.id

    # kolom id di GSS
    id = sheet3.col_values(1)
    
    # jika chat ID ada di data GSS
    if str(chatID) in id :
        # mengambil custom reminder user berdasarkan chat ID
        cell = id.index(str(chatID)) + 1
        dataUser = sheet3.row_values(cell)

        try :
            # mengirim daftar custom reminder user
            await bot.send_message(chatID, f'*— Custom Reminder —*\
                                            \n\n*8 Pagi :* \n{dataUser[1]}\
                                            \n\n*5 Sore :* \n{dataUser[2]}\
                                            \n\n*8 Malam :* \n{dataUser[3]}',
                                            'Markdown')

            # jika user belum atau tidak membuat custom reminder
            if (dataUser[1] == '-') and (dataUser[2] == '-') and (dataUser[3] == '-') :
                await bot.send_message(chatID, '⚠️ Tekan /customreminder untuk membuat custom reminder.')
            
            # jika user sudah atau memiliki custom reminder
            else :
                await bot.send_message(chatID, '⚠️ Tekan /reset untuk menghapus semua custom reminder.')
                    
        except :
            print(f"I can't send data of the user ({chatID}), Sir.")
    
    # jika chat ID tidak ada di data GSS
    else :
        try :
            await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')
        except :
            print(f"I can't reply to the user ({chatID}), Sir.")

# COMMAND /RESET
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
        
        try :
            await bot.send_message(chatID, 'Custom reminder berhasil direset ✅\
                                            \n\nApa yang ingin kamu lakukan selanjutnya?\
                                            \nTekan /help untuk mengetahui daftar command bot ini.')
        except :
            print(f"I can't send message to the user ({chatID}), Sir.")
    
    # jika chat ID tidak ada di data GSS
    else :
        try :
            await bot.send_message(chatID, '🚫 Data tidak ditemukan. Tekan /start.')
        except :
            print(f"I can't send message to the user ({chatID}), Sir.")

# COMMAND /HELP
@bot.message_handler(commands=['help'])
async def help(message) :
    chatID = message.chat.id
    
    command = 'Berikut daftar command dari bot ini:\
               \n/start — Memulai bot\
               \n/cekdata — Mengecek data pengguna\
               \n/updatedata — Memperbarui data pengguna\
               \n/customreminder — Menambahkan custom reminder\
               \n/cekcustom — Mengecek custom reminder\
               \n/ba_absen — Membuat berita acara absen bolong\
               \n/hcm_helpdesk — Bertanya kepada PIC HCM Semarang'
    
    # jika user adalah admin
    if chatID in admin :
        try :
            await bot.send_message(chatID, f'{command}\
                                \n/addreminder — Menambahkan pesan reminder (template message)\
                                \n/broadcast — Menyiarkan pesan')
        
        except :
            print(f"I can't send message to the admin ({chatID}), Sir.")
    
    # jika user bukan admin
    else :
        try :
            await bot.send_message(chatID, command)
        except :
            print(f"I can't send message to the user ({chatID}), Sir.")

# UNTUK MENANGKAP PESAN USER SELAIN YANG ADA DI DAFTAR COMMAND
@bot.message_handler()
async def anything(message) :
    await help(message)

# FUNGSI UNTUK MENGIRIM REMINDER ABSENSI KE USER
async def reminder(today, time) :
    global id

    # hari libur
    weekend = (5, 6)

    # hari Selasa dan Kamis
    twoDays = (1, 3)

    id = sheet1.col_values(1)
    id = id[1:]

    # jika hari ini adalah hari kerja
    if today not in weekend :
        # jika waktu absensi adalah jam 8 pagi
        if time == '08:00' :   
            await reminderMsg(2, id)

        # jika waktu absensi adalah jam 5 sore
        elif time == '17:00' :
            await reminderMsg(3, id)

        # jika waktu absensi adalah jam 8 malam
        elif time == '20:00' :
            await reminderMsg(4, id)
            
    # else :
    #     additionReminder = sheet3.col_values(5)
        
    #     users = []
    #     for i in id :
    #         cell = id.index(str(i)) + 1
    #         weekendRemind = additionReminder[cell]

    #         if weekendRemind != '-' :
    #             users.append(i)
        
    #     if bool(users) :
    #         # jika waktu absensi adalah jam 8 pagi
    #         if time == '08:00' :   
    #             await reminderMsg(2, users)

    #         # jika waktu absensi adalah jam 5 sore
    #         elif time == '17:00' :
    #             await reminderMsg(3, users)
            
    #         # jika waktu absensi adalah jam 8 malam
    #         elif time == '20:00' :
    #             await reminderMsg(4, users)

    # jika hari ini adalah Hari Selasa dan Kamis
    if today in twoDays :
        if time == '11:00' :
            usernames  = sheet1.col_values(2)
            names = sheet1.col_values(3)

            if len(names) < len(usernames) :
                for i in range(0, len(usernames) - len(names)) :
                    names.append('')

            for i in id :
                cell = id.index(str(i)) + 1
                data = [usernames[cell], names[cell]]

                count = 0
                blocker = []

                if '' in data :
                    try :
                        count += 1
                        await bot.send_message(i, '‼️WARNING : ANDA BELUM MENGISI DATA DIRI‼️\
                                                \n\nSemangat Pagi!!\
                                                \nKepada rekan2 SPARTA yang belum mengisi data diri berupa NIK, NAMA & NO TELP mohon untuk segera mengirimkan data tersebut dengan cara membalas BOT ini dengan command */start* lalu isi format sbb :\
                                                \n\nNama Lengkap:\
                                                \nNomor Induk Karyawan:\
                                                \nNomor Hp (Telegram):\
                                                \n\n_(dengan menggunakan ENTER)_\
                                                \n\nContoh :\
                                                \nFaizhal Rifky Alfaris\
                                                \n935762\
                                                \n0812345678\
                                                \n\nTerimakasih\
                                                \n- HCM Semarang -', 'Markdown')

                    except :
                        blocker.append(i)

            if bool(blocker) :
                print(f'User : {blocker} blocked me, Sir.\n')

# FUNGSI UNTUK MEMERIKSA CUSTOM REMINDER DI GSS
# DAN MENGIRIM PESAN REMINDER KE USER
async def reminderMsg(col, targets) :
    # mengambil pesan secara acak dari template message
    templateMsg = sheet2.col_values(col)
    randMsg = random.choice(templateMsg[1:])

    customMsg = sheet3.col_values(col)

    blocker = []
    count = 0
    for i in targets :
        cell = id.index(str(i)) + 1

        # memeriksa custom reminder user
        text = randMsg
        if customMsg[cell] != '-' :
            text = customMsg[cell]

        try :
            await bot.send_message(i, text)
            count += 1
        except :
            blocker.append(i)
    
    if bool(blocker) :
        print(f"User : {blocker} blocked me, Sir.\n")
    
    print(f'Messages successfuly sent to {count} from {len(id)} users, Sir.')

# NOTIFIKASI KEPADA ADMIN UNTUK MENGGANTI TANGGAL REKAP ABSEN
async def notif() :
    exp_date = sheet4.row_values(3)
    have_used = sheet5.row_values(1)

    msg = 'Yth. Admin di tempat,\
           \n\nRekap absen karyawan pada _database_ saat ini belum diperbarui.\
           \nSegera lakukan pembaruan dengan memasukkan rekap absen karyawan periode bulan ini pada *_sheet_ absen karyawan* di _database_.\
           \nDemikian pemberitahuan ini saya sampaikan.\
           \n\nSalam,\
           \nBOT HCM'

    if exp_date == have_used :
        for i in admin[2:] :
            try :
                await bot.send_message(i, msg, 'Markdown')
            except :
                print(f"I can't send message to the admin ({i}), Sir.")

# BROADCAST OTOMATIS ABSEN KURANG UNTUK KARYAWAN
async def absen_kurang() :
    exp_date = sheet4.row_values(3)
    have_used = sheet5.row_values(1)

    niks = sheet4.col_values(2)
    nik_list = list(dict.fromkeys(niks[4:]))

    names = sheet4.col_values(3)
    name_list = list(dict.fromkeys(names[4:]))

    nama_absen = []
    nik_absen = []
    hari_absen = []
    id_absen = []

    count_success = 0
    count_failed = 0

    if exp_date != have_used :
        for i in range(0, len(nik_list)) :
            days = niks.count(nik_list[i])
            
            if days < 20 :
                try :
                    id = sheet1.col_values(1)
                    nikss = sheet1.col_values(4)

                    cell = nikss.index(nik_list[i])
                    id_absen.append(id[cell])    
                    hari_absen.append(20 - days)
                    nik_absen.append(nik_list[i])
                    nama_absen.append(name_list[i])

                    count_success += 1

                except :
                    count_failed += 1

        for i in range(0, len(id_absen)) :
            warning_msg = f'‼️REMINDER HCM‼️\
                            \n\nSemangat Pagi,\
                            \nKepada Sdr. {nama_absen[i]} / NIK. {nik_absen[i]}\
                            \nBahwa ada indikasi kurangnya absensi saudara untuk _payroll_ bulan ini sebanyak {hari_absen[i]} kali.\
                            \n\nMohon untuk menghubungi HR Area setempat guna mengkonfirmasi absensi, atau bisa langsung membuat Berita Acara Absen menggunakan command */ba_absen* pada BOT ini.\
                            \nTerimakasih\
                            \n\n~ HCM Semarang ~'
            try :
                await bot.send_message(id_absen[i], warning_msg, 'Markdown')
            except :
                print(f"I can't send message to the user ({id_absen[i]}), Sir.")

        sheet5.update_cell(1, 1, exp_date[0])

# FILTER STATE UNTUK MEMBEDAKAN STATE SAAT USER MEMBERI INPUT
bot.add_custom_filter(asyncio_filters.StateFilter(bot))

async def main() :
    while True :
        # MEMERIKSA TANGGAL
        dt = datetime.now()
        dt = dt.strftime('%d')

        # MEMERIKSA HARI
        today = date.today()
        today = today.weekday()

        # MEMERIKSA WAKTU
        currentTime = time.strftime('%H:%M')

        # MEMANGGIL FUNGSI REMINDER
        await reminder(today, currentTime)

        # JIKA HARI INI TANGGAL 8, 10, ATAU 12
        if dt in ['8', '10', '12'] :
            if currentTime == '13:00' :
                # MEMANGGIL FUNGSI NOTIF
                await notif()
        # JIKA HARI INI TANGGAL 13
        elif dt == '13' :
            if currentTime == '13:00' :
                # MEMANGGIL FUNGSI ABSEN_KURANG
                await absen_kurang()

        # MEMERIKSA DETIK DAN MENIT SAAT INI
        second = time.strftime('%S')
        second = int(second)
        minute = time.strftime('%M')
        minute = int(minute)*60

        # MENGHITUNG TOTAL DETIK SAAT INI
        seconds = second + minute

        # LOG JAM
        clock = time.strftime('%H:%M:%S')
        print(f'* {clock} *')
        print()

        # WAKTU TUNGGU LOOP UNTUK MEMERIKSA WAKTU TIAP JAM
        await asyncio.sleep(3600 - seconds)

# MENJALANKAN BOT DENGAN CARA ASYNCHRONOUS
while True :
    try :
        loop = asyncio.new_event_loop()
        loop.create_task(main(), name='Time Checking')
        loop.create_task(bot.infinity_polling(), name='Bot Commands')
        loop.run_forever()
    except :
        time.sleep(5)
        continue
