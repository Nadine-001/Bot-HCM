from telebot.async_telebot import AsyncTeleBot
from datetime import date
import time, asyncio

# token bot
bot = AsyncTeleBot('5538226702:AAGdbNQmMSCiQS_861iti98NBh69J1UwBzI')

# list chat ID user
id = [5363691964, 5033311508, 1372954700]

# chat ID untuk testing bot :
# Nessa : 5363691964, 5142972565
# Midaj : 5033311508
# Arini : 1372954700

# list chat ID yang sudah mendapatkan pesan reminder
# untuk menghindari spam
idDone = []

# waktu untuk trigger pesan reminder
fiveTo = ["07:55", "16:55", "19:55"]
exactTime = ["08:00", "17:00", "20:00"]
## fivepast = ["08:05", "17:05", "20:05"]

# pesan reminder
template = ['📌 Jangan lupa untuk mengisi presensi 5 menit lagi!',
            '📢 Waktunya untuk mengisi presensi!',
            'Saya akan mengingatkan Anda untuk mengisi presensi pada jam 8 pagi, \
5 sore, dan 8 malam.\n\nSalam kenal,\nPresensiReminder 😊']

# /start command dari user
@bot.message_handler(commands=['start'])
async def welcome(message) :
    # mengambil chat ID
    chatID = message.chat.id

    # menambahkan chat ID baru ke list chatID
    if chatID not in id:
        id.append(chatID)

    ## print(id)

    # pesan balasan
    await bot.send_message(chatID, f'Halo, {message.from_user.first_name}! 👋🏻\n\n{template[2]}')

async def reminder(day, time) :
    global idDone

    # hari libur
    weekend = [5, 6]

    for i in id : 
        # jika hari ini adalah hari kerja
        if day not in weekend :
            # jika waktu presensi kurang 5 menit
            if time in fiveTo :
                # jika user belum mendapatkan pesan reminder
                if i not in idDone :
                    # mengirim pesan
                    await bot.send_message(i, template[0])
                    idDone.append(i)

            # jika sudah masuk waktu presensi
            elif time in exactTime :
                # jika user belum mendapatkan pesan reminder
                if i not in idDone :
                    # mengirim pesan
                    await bot.send_message(i, template[1])
                    idDone.append(i)

            # mereset list idDone jika semua user sudah menerima reminder
            if len(idDone) == len(id) :
                idDone = []  
        
        # mereset list idDone pada hari libur
        else :
            idDone = []
        
        ## print("\nidDone :", idDone)     

async def main() :
    while True :
        # memeriksa hari
        today = date.today()
        today = today.weekday()

        # memeriksa waktu saat ini
        currentTime = time.strftime("%H:%M")
        
        # mengambil detik saat ini
        second = time.strftime("%S")
        second = int(second)

        # memanggil fungsi reminder
        await reminder(today, currentTime)

        ## currentTime = time.strftime("%H:%M:%S")
        ## print("*", currentTime, "*")
        ## print("-", today, "-")

        # waktu tunggu loop
        await asyncio.sleep(60 - second)

# run using asynchronous mode
try :
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    cors = asyncio.wait([main(), bot.polling()])
    loop.run_until_complete(cors)
except :
    pass
