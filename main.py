#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
import logging
from db import sql

db = sql()
db.SQLITE_VERSION()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
CHOOSING, TYPING_REPLY, TYPING_CHOICE, SET_CURSO = range(4)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')
    print(update.message.chat_id)
    db.query_comit("INSERT OR IGNORE INTO Auth VALUES({})".format(update.message.chat_id))


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def test(bot, update):
    x = db.query_consult("SELECT name FROM category WHERE parent IS NULL")
    markup = ReplyKeyboardMarkup(x, one_time_keyboard=True)
    update.message.reply_text("Select: ", reply_markup=markup)


def query_response(bot, update, query):
    x = db.query_consult(query)
    if len(x) != 0:
        markup = ReplyKeyboardMarkup(x, one_time_keyboard=True)
        update.message.reply_text("Select: ", reply_markup=markup)


def update(bot, update):
    reply_keyboard = [['Promocionar Usuario', 'Curso'],
                      ['Number of siblings', 'Something else...'],
                      ['Done']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Hi! My name is Monlau Botter. I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=markup)

    return CHOOSING


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              "Until next time!".format(user_data))

    user_data.clear()
    return ConversationHandler.END


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    if text == "Curso":
        db.query_comit("Update Users SET course = '' WHERE ID == {}".format(update.message.chat_id))
        query_response(bot, update, "SELECT name FROM category WHERE parent IS NULL")
        return SET_CURSO
    else:
        update.message.reply_text(
            'Your {}? Yes, I would love to hear about that!'.format(text.lower()))
        return TYPING_REPLY


def custom_choice(bot, update):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{}"
                              "You can tell me more, or change your opinion on something.".format(
        user_data))  # , reply_markup=markup)

    return CHOOSING


def respose_set_curso(bot, update, user_data):
    user_id = update.message.chat_id
    text = update.message.text
    toadd = db.query_consult("SELECT category_id FROM category WHERE name = '{}'".format(text))[0][0]

    fr = db.query_consult("SELECT course FROM Users WHERE ID = '{}'".format(user_id))[0][0].strip()
    db.query_comit("Update Users SET course = '{}' WHERE ID == {}".format(str(fr) + " " + str(toadd), user_id))
    query_response(bot, update, "SELECT name FROM category WHERE parent = {}".format(toadd))


def promote_user(bot, update):
    db.query_comit("INSERT OR IGNORE INTO Users (ID) VALUES ({})".format(update.message.chat_id))


def main():
    """Start the bot."""
    updater = Updater("493744108:AAFSwOAvqN-Ly9KgChF_VXRd_K6eimKDoqI")
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("test", test))
    # dp.add_handler(CommandHandler("update", update))


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('update', update)],

        states={
            CHOOSING: [RegexHandler('^(Curso|Favourite colour|Number of siblings)$',
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Promocionar Usuario$',
                                    promote_user),
                       RegexHandler('^Something else...$',
                                    custom_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
            SET_CURSO: [MessageHandler(Filters.text,
                                       respose_set_curso,
                                       pass_user_data=True),
                        ],
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)

    dp.add_handler(conv_handler)

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
