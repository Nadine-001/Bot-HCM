from telebot.async_telebot import AsyncTeleBot
from datetime import date
import time, asyncio, csv

# token bot
bot = AsyncTeleBot('5538226702:AAGdbNQmMSCiQS_861iti98NBh69J1UwBzI')

# chat ID untuk testing bot :
# Nessa : 5363691964, 5142972565
# Midaj : 5033311508
# Arini : 1372954700

# waktu untuk trigger pesan reminder
fiveTo = ['07:55:00', '16:55:00', '19:55:00', '18:44:00']
exactTime = ['08:00:00', '17:00:00', '20:00:00', '18:45:00']
## fivepast = ['08:05', '17:05', '20:05']

# pesan reminder
template = ['SEMANGAT PAGI! 🙌🏻\n📌 Jangan lupa untuk absensi 5 menit lagi!',
            'SEMANGAT PAGI! 🙌🏻\n📢 Waktunya untuk absensi!',
            'Bot ini akan mengingatkan Anda untuk absensi pada jam 8 pagi, \
5 sore, dan 8 malam.\n\nSalam kenal,\nPresensiReminder 😊',
            'Tes']

# /start command dari user
@bot.message_handler(commands=['start'])
async def welcome(message) :
    # mengambil chat ID
    chatID = message.chat.id
    
    # pesan balasan
    await bot.send_message(chatID, f'Halo, {message.from_user.first_name}! 👋🏻\n\n{template[2]}')

    chatID = [str(chatID)]

    # memanggil fungsi readChatID
    await readChatID()

    # memanggil fungsi writeChatID
    await writeChatID(chatID)

async def readChatID() :
    global id

    with open('id.csv', newline = '') as read :
        # membaca data csv
        csvReader = csv.reader(read)
        
        # memasukkan data ke list id
        id = []
        for row in csvReader:
            id.append(row)

async def writeChatID(chatID) :
    global id

    with open('id.csv', 'a', newline = '') as write :  
        # menambahkan chat ID baru ke data csv
        if chatID not in id :
            csvWriter = csv.writer(write)
            csvWriter.writerow(chatID)

async def reminder(day, time) :
    global id
    
    # memanggil fungsi readChatID
    await readChatID()

    ## print('#', id, '#')

    # hari libur
    weekend = [5, 6]

    for i in id[1:] :
        # jika hari ini adalah hari kerja
        if day not in weekend :
            # jika waktu presensi kurang 5 menit
            if time in fiveTo :
                await bot.send_message(i[0], template[3] + ' doang')

            # jika sudah masuk waktu presensi
            elif time in exactTime :
                await bot.send_message(i[0], template[3] + ' lagi')

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
    asyncio.set_event_loop(loop)
    cors = asyncio.wait([main(), bot.polling()])
    loop.run_until_complete(cors)
except :
    pass
