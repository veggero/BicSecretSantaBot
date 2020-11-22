# -*- coding: utf-8 -*-
#!/usr/bin/python
import csv 

# This is a simple Secret Santa bot tailored for the Breaking Italy Club.
# It allows to register/delete oneself from the users that take part in the Secret Santa,
# to specify one's address/message to the Secret Santa and to proceed with the random 
# assignments.

import telebot
from database import RegisteredDatabase

def read_token(path):
	with open(path) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		for line in csv_reader:
			token = line[0]
			break
	return token

API_TOKEN = read_token("api_token.csv")

bot = telebot.TeleBot(API_TOKEN)
db = RegisteredDatabase("registered_users.json", "settings.csv")

# Handle '/start' and '/help'

admins =["Luca_MS", "merlo24"]
status =["address", "message"]

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):

	msg = """\
Ciao! Sono il bot NON ufficiale per il Secret Santa 🎅 del Breaking Italy Club. 
In questa fase mi puoi controllare solo con questo comando: \n
/register - 🎁 registrati per il Secret Santa. Segui le istruzioni, per poter partecipare dovrai fornire il tuo indirizzo 🏠 (anche di un fermo posta), che verrà divulgato solo al tuo Secret Santa. 
/user_list - 🕵️‍♂️ elenca gli utenti che si sono iscritti per ora al Secret Santa. 

Quando sarai registrato potrai usare i comandi:
/delete_me - 😢 rimuoviti dall'elenco dei partecipanti al Secret Santa.
/my_info - per sapere cosa so di te.
/add_address - 🏠 registra il tuo indirizzo. Assicurati che includa il tuo nome e cognome, in caso non sia ovvio da telegram.
/modify_address - 🏠 modifica il tuo indirizzo. 
/add_message - 📬 lascia un messaggio al tuo Secret Santa. Usalo per dare dei suggerimenti, una blacklist, o delle informazioni aggiuntive! 
/modify_message - 📬 modifica il messaggio lasciato al tuo Secret Santa.

A partire dal 2 Dicembre, sarà invece disponibile solo il comando:
/assign_me - ti verrà assegnata la persona a cui dovrai fare il regalo, e ti verrà mostrato il suo handler di Telegram, indirizzo e eventualmente il messaggio che ti ha scritto.

L'indicazione è di spendere circa 10 euro per il regalo, spese di spedizione escluse. \n
Usami con cautela! Ché il programmatore è un po' un cane 🐶 quindi è possibile che io sia buggato 🧠.\n\

"""
	if message.from_user.username in admins:
		msg+="Ah! Sei un admin! Per te esistono anche questi comandi:\n"
		msg+="/toggle_registrations - Per fermare o far ripartire i comandi che permettono di registrarsi/modificare i propri dati\n"
		msg+="/assign - Per procedere alle assegnazioni casuali.\n"
		msg+="/incomplete_users - Per sapere chi non ha ancora inserito un indirizzo \n"

	bot.reply_to(message, msg)


# Handle '/register'
@bot.message_handler(commands=['register'])
def handle_register(message):
	"""
	Add an user to the list of users that want to join the Secret Santa.

	If the user is already registered, suggest whether they want to delete their information. 
	If the user is not registered, ask to confirm their choice.
	"""
	db.reset_user_status(message.from_user.username)
	bot.reply_to(message, db.add_user(message.from_user.username))

@bot.message_handler(commands=['delete_me'])
def handle_delete(message):
	"""Delete an user from the registered users.
	"""
	db.reset_user_status(message.from_user.username)
	bot.reply_to(message, db.remove_user(message.from_user.username))

@bot.message_handler(commands=['my_info'])
def handle_myinfo(message):
	"""Print an user info.
	"""
	db.reset_user_status(message.from_user.username)
	reply = ""
	if message.from_user.username in admins:
		reply+="Sei un admin!\n"
	reply +=db.print_user_info(message.from_user.username)
	bot.reply_to(message, reply)


@bot.message_handler(commands=['add_address', 'modify_address'])
def handle_address(message):
	"""Add an address to a registered user.
	"""
	bot.reply_to(message, db.set_user_status(message.from_user.username, "address"))

@bot.message_handler(commands=['add_message', 'modify_message'])
def handle_message_to_ss(message):
	"""Add an address to a registered user.
	"""
	bot.reply_to(message, db.set_user_status(message.from_user.username, "message"))

@bot.message_handler(commands=['assign_me'])
def handle_assign_me(message):
	"""Add an address to a registered user.
	"""
	db.reset_user_status(message.from_user.username)
	bot.reply_to(message, db.get_child(message.from_user.username))

@bot.message_handler(commands=['assign'])
def handle_assign(message):
	"""Add an address to a registered user.
	"""
	db.reset_user_status(message.from_user.username)
	if message.from_user.username not in admins:
		return
	msg = db.get_incomplete_users()
	msg+= "Se vuoi procedere alle assegnazioni, scrivi \"sono sicuro di voler procedere alle assegnazioni\""
	bot.reply_to(message, msg)


@bot.message_handler(commands=['incomplete_users'])
def handle_incomplete(message):
	db.reset_user_status(message.from_user.username)
	if message.from_user.username not in admins:
		return
	bot.reply_to(message, db.get_incomplete_users())

##### Admin commands
@bot.message_handler(commands=['toggle_registrations'])
def handle_toggle_registrations(message):
	"""Toggles the registration functionalities.
	"""
	db.reset_user_status(message.from_user.username)
	if message.from_user.username not in admins:
		return 
	bot.reply_to(message, db.toggle_registrations())

@bot.message_handler(commands=['user_list'])
def handle_user_list(message):
	db.reset_user_status(message.from_user.username)
	bot.reply_to(message, db.get_user_list_msg())

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
	text = message.text.lower()
	reply = ""
	username = message.from_user.username
	status = db.get_user_status(username)

	if status == "address":
		address =message.text.replace("\n"," ")
		address =address.replace("\r"," ")
		reply = db.add_address(username, address)
		db.reset_user_status(username)
	elif status == "message":
		msg =message.text.replace("\n"," ")
		msg =msg.replace("\r"," ")
		reply = db.add_message(username, msg)
		db.reset_user_status(username)
	elif text=="sono sicuro di voler procedere alle assegnazioni" and message.from_user.username in admins:
		reply = db.assign_santas()
	else:
		reply = "Super interessante! Purtroppo non so cosa rispondere ma ti auguro un felice Natale!"
	bot.reply_to(message, reply)

bot.polling()
