# run this first on terminal :
# pip install pyTelegramBotAPI
import telebot

from datetime import date
import time

# token bot
bot = telebot.TeleBot('5538226702:AAGdbNQmMSCiQS_861iti98NBh69J1UwBzI')

# list chat ID user
id = [5363691964]

# chat ID untuk testing bot :
# Nessa : 5363691964, 5142972565
# Midaj : 5033311508
# Arini : 1372954700

# list chat ID yang sudah mendapatkan pesan reminder
# untuk menghindari spam
idDone = []

# list hari
days = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday",
        "Sunday"]

# waktu untuk trigger pesan reminder
# elemen terakhir untuk testing bot
fiveTo = ["07:55", "16:55", "19:55", "01:12"]
exactTime = ["08:00", "17:00", "20:00", "01:13"]
## aMinute = ["07:54", "16:54", "19:54"
##             "07:59", "16:59", "19:59"]
## fivepast = ["08:05", "17:05", "20:05"]

# pesan reminder
template = ['Jangan lupa untuk mengisi presensi 5 menit lagi!',
            'Waktunya untuk mengisi presensi!']

# /start command dari user
@bot.message_handler(commands=['start'])
def welcome(message) :
    # mengambil chat ID
    chatID = message.chat.id

    # menambahkan chat ID baru ke list chatID
    if chatID not in id:
        id.append(chatID)

    ## print(id)

    # pesan balasan
    bot.reply_to(message, "What's up, mate?")

## last_textchat = ""

def reminder(day, time) :
    global idDone

    # hari libur
    weekend = [days[5], days[6]]

    for i in id :
        # jika hari ini adalah hari kerja
        if day not in weekend :
            # jika waktu presensi kurang 5 menit
            if time in fiveTo :
                ## msg = template[0]
                ## send(i, msg)

                # jika user belum mendapatkan pesan reminder
                if i not in idDone :
                    # mengirim pesan
                    bot.send_message(i, template[0])
                    idDone.append(i)

            # jika sudah masuk waktu presensi
            elif time in exactTime :
                ## msg = template[1]
                ## send(i, msg)

                # jika user belum mendapatkan pesan reminder
                if i not in idDone :
                    # mengirim pesan
                    bot.send_message(i, template[1])
                    idDone.append(i)

            # mereset list idDone jika semua user sudah menerima reminder
            if len(idDone) == len(id) :
                idDone = []  
        
        # mereset list idDone pada hari libur
        else :
            idDone = []
        
        ## idDone.append(i)

        # untuk mengecek isi list idDone
        print(idDone)     

## def send(chatID, chat) :
##     global last_textchat, idDone
##    if chatID not in idDone :
##        bot.send_message(chatID, chat)
##        last_textchat = chat

def main() :
    while True :
        # mengecek hari
        today = date.today()
        today = today.weekday()
        ## print(today)

        # mengecek waktu saat ini
        currentTime = time.strftime("%H:%M:%S")
        print(currentTime)
        
        # mengambil detik saat ini
        second = currentTime.split(':')
        second = int(second[2])

        # memanggil fungsi reminder
        reminder(today, currentTime)

        # waktu tunggu loop
        time.sleep(60 - second)

# nah, bagian bawah ini yang masih belum bisa
# main() bisa jalan, tapi nanti command /start ga bisa
# karena /start baru bisa hidup pake bot.polling(),
# sedangkan dua-duanya ini infinite loop yang bikin botnya hidup terus.
# Dengan kata lain, bot jalannya di atau karena main()
# dan tidak akan pernah sampai ke bot.polling()
# selama tidak ada terminate, seperti error.
if __name__ == '__main__' :
    main()

bot.polling()

# Ngopi, gengs
