#v1.02J
import subprocess
from telegram.ext import Updater, CommandHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from functools import wraps
import requests
import json
import time
import math
import matplotlib

updater = Updater(token='BOT_TOKEN')#Insert Your Telegram Bot Token Here
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
#PATH TO Daemon
core = "/home/divi/divi_ubuntu/divi-cli"
#
# Restricted Commands, Channel or Status(private or admin only)

ADMIN_ONLY = ['admin1', 'admin2','admin3'] #change 'admin' to telegram usernames withouth '@'
GROUP_ONLY = ['groupnumber'] #change to the telegram group id example -1001183647288

def adminonly(func):
	@wraps(func)
	def wrapped(bot, update):
		user = update.message.from_user.username
#		group = update.message.chat.id
		if user not in ADMIN_ONLY:
			bot.send_message(chat_id=update.message.chat_id, text="Sorry you dont have access to this function.".format(user))
			return
		if group not in GROUP_ONLY:
			bot.send_message(chat_id=update.message.chat_id, text="You can only do this in Admin Channel")
			return
		return func(bot, update)
	return wrapped

def privatecommands(func):
	@wraps(func)
	def wrapped(bot, update):
		if update.message.chat.type != "private":
			button = [InlineKeyboardButton("YourBotName", callback_data="button", url='t.me/YourBotName')],
			reply_markup = InlineKeyboardMarkup(button)
			bot.send_message(chat_id=update.message.chat_id, text="Please click the button below to talk with me privately about balance, deposits and withdrawls", reply_markup = reply_markup)
			return
		return func(bot, update)
	return wrapped
#
# To use the restricted commands wrap them like the example
# Example
#	@privatecommands
#	def balance(bot, update):
#		pass
#
def commands(bot, update):
	user = update.message.from_user.username
	bot.send_message(chat_id=update.message.chat_id, text="Initiating commands /tip & /withdraw have a specfic format,\n use them like so:" + "\n \n Parameters: \n <user> = target user to tip \n <amount> = amount of reddcoin to utilise \n <address> = reddcoin address to withdraw to \n \n Tipping format: \n /tip <user> <amount> \n \n Withdrawing format: \n /withdraw <address> <amount>")

def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="The following commands are at your disposal: /hi , /commands , /deposit , /tip , /withdraw , /price , /marketcap or /balance")


def deposit(bot,update):
	pass
	user = update.message.from_user.username
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a Telegram username in your profile settings!")
	else:
		core = "/home/divi/divi_ubuntu/divi-cli"
		result = subprocess.run([core,"getaccountaddress",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		bot.send_message(chat_id=update.message.chat_id, text="@{0} your depositing address is: {1}".format(user,clean))

def tip(bot,update):
	user = update.message.from_user.username
	target = update.message.text[5:]
	if(len(target.split(" "))<2):
		bot.send_message(parse_mode='MARKDOWN', chat_id=update.message.chat_id, text="You are missing information. \n\nPlease use this format\n/tip <@username> <amount>")
		return
	else:
		amount =  target.split(" ")[1]
		target =  target.split(" ")[0]
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a Telegram username in your profile settings!")

	else:
		if target == "@Divi_Tip_Bot" or target == "@diviguard_bot" or target == "@username":
			bot.send_message(chat_id=update.message.chat_id, text="It's part of my culture to tip you if you tip me. So its back in your account already!")
		elif "@" in target:
			target = target[1:]
			core = "/home/divi/divi_ubuntu/divi-cli"
			try:
				amount = float(amount)
				#get decimals
				decimals = amount - math.floor(amount)

				if(len(str(decimals)) > 5):
					bot.send_message(chat_id=update.message.chat_id, text="Tips are restricted to three decimal places.")
				amount = math.floor(amount*1000)/1000

				result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
				balance = float((result.stdout.strip()).decode("utf-8"))

				if balance < amount:
					bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds to send this tip.".format(user))
				elif target == user:
					bot.send_message(chat_id=update.message.chat_id, text="You can't tip yourself silly.")
				elif amount <= 0.001:
					bot.send_message(chat_id=update.message.chat_id, text="You shouldnt be so cheap.")
				else:
					balance = str(balance)
					amount = str(amount)
					tx = subprocess.run([core,"move",user,target,amount],stdout=subprocess.PIPE)
					clean = (tx.stdout.strip()).decode("utf-8")
					bot.send_message(chat_id=update.message.chat_id, text="@{0} tipped @{1} {2} DIVI\n {3}".format(user, target, amount, clean))
			except ValueError:
				bot.send_message(chat_id=update.message.chat_id, text="Sorry! That amount didn't work. Try again only numbers.")
		else:
			bot.send_message(chat_id=update.message.chat_id, text="Oops! I can't find that user! Make sure you have the right username and include the @ symbol before the username. If the recipient doesn't have an @username they will need to set one to receive your tip.")


def balance(bot,update):
	user = update.message.from_user.username
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a Telegram username in your profile settings!")
	else:
		core = "/home/divi/divi_ubuntu/divi-cli"
		result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		balance  = float(clean)
		balance =  str(math.floor(balance*1000)/1000)
		bot.send_message(chat_id=update.message.chat_id, text="@{} your current balance is: {} DIVI".format(user,balance))



def price(bot,update):# Update 'yourcoin' to your asset
	usdprice = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=yourcoin&vs_currencies=USD&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true')
	btcprice = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=yourcoin&vs_currencies=BTC&include_market_cap=fals&include_24hr_vol=fals&include_24hr_change=false&include_last_updated_at=false')
	sats = json.loads(btcprice.text)
	details = json.loads(usdprice.text)
	usdp = details['yourcoin']['usd']
	usdp = round(usdp,4)
	mcap = details['yourcoin']['usd_market_cap']
	mcap = round(mcap,1)
	vol = details['yourcoin']['usd_24h_vol']
	vol = round(vol,1)
	chg = details['yourcoin']['usd_24h_change']
	chg = round(chg,1)
	lua = details['yourcoin']['last_updated_at']
	lua = time.strftime('%H:%M:%S %m-%d-%Y', time.localtime(lua))
	sats = sats['yourcoin']['btc']
	sats = float(sats)
	bot.send_message(parse_mode='MARKDOWN',chat_id=update.message.chat_id, text="""```
YourCoin        | Current Trading
--------------- | --------------------
USD:            | ${:,}
BTC:            | {:.8f}
Market Cap:     | ${:,}
24 Hour Volume: | ${:,}
24 Hour Change: | {:,}%
Updated:        | {}
```""".format(usdp, sats, mcap, vol, chg, lua))


price_handler = CommandHandler('price', price)
dispatcher.add_handler(price_handler)

def withdraw(bot,update):
	user = update.message.from_user.username
	if user is None:
		bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
	else:
		target = update.message.text[9:]
		address = target[:35]
		address = ''.join(str(e) for e in address)
		target = target.replace(target[:35], '')
		amount = float(target)
		core = "/usr/local/bin/reddcoind"
		result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		balance = float(clean)
		if balance < amount:
			bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
		else:
			amount = str(amount)
			tx = subprocess.run([core,"sendfrom",user,address,amount],stdout=subprocess.PIPE)
			bot.send_message(chat_id=update.message.chat_id, text="@{0} has successfully withdrew to address: {1} of {2} RDD" .format(user,address,amount))

def hi(bot,update):
	user = update.message.from_user.username
	bot.send_message(chat_id=update.message.chat_id, text="Hello @{0}, how are you doing today?".format(user))

def moon(bot,update):
  bot.send_message(chat_id=update.message.chat_id, text="Moon mission inbound!")

def marketcap(bot,update):
	quote_page = requests.get('https://www.worldcoinindex.com/coin/reddcoin')
	strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
	soup = BeautifulSoup(quote_page.content, 'html.parser', parse_only=strainer)
	name_box = soup.find('div', attrs={'class':'col-md-6 col-xs-6 coin-marketcap'})
	name = name_box.text.replace("\n","")
	mc = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
	bot.send_message(chat_id=update.message.chat_id, text="The current market cap of Reddcoin is valued at {0}".format(mc))

from telegram.ext import CommandHandler

commands_handler = CommandHandler('commands', commands)
dispatcher.add_handler(commands_handler)

moon_handler = CommandHandler('moon', moon)
dispatcher.add_handler(moon_handler)

hi_handler = CommandHandler('hi', hi)
dispatcher.add_handler(hi_handler)

withdraw_handler = CommandHandler('withdraw', withdraw)
dispatcher.add_handler(withdraw_handler)

marketcap_handler = CommandHandler('marketcap', marketcap)
dispatcher.add_handler(marketcap_handler)

deposit_handler = CommandHandler('deposit', deposit)
dispatcher.add_handler(deposit_handler)

price_handler = CommandHandler('price', price)
dispatcher.add_handler(price_handler)

tip_handler = CommandHandler('tip', tip)
dispatcher.add_handler(tip_handler)

balance_handler = CommandHandler('balance', balance)
dispatcher.add_handler(balance_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

updater.start_polling()
