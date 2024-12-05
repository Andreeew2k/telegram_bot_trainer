from typing import Final
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler, CallbackContext
from database import init_db, insert_record, get_records
from datetime import datetime

TOKEN: Final = "7261291465:AAHNpFlX8lsO41z-M41gtjlrlTW3IrFZf5Y"
BOT_USERNAME: Final = "personal_gym_training_bot"
MENU, PUSH, PULL, LEGS, PUSH_WORKOUT = range(5)



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Push", callback_data="push")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What you will train today?", reply_markup=reply_markup)
    return MENU

async def start_question_button(update: Update, context: CallbackContext): 
    query = update.callback_query
    await query.answer()

    if query.data == "push":
        await query.edit_message_text(text="You selected Push")
        return await push(update, context)
    else:
        await query.edit_message_text(text="Unknown option")
        return MENU

async def push(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if "push_step" not in context.user_data:
        context.user_data["push_step"] = 0
    step = context.user_data.get("push_step")
    callback_data = query.data  # Get the callback data from the clicked button

    print(step)
    
    if step == 0:
        
        text = f"Today we will do push up, pull ups, bench press! If you ready press start!"

        keyboard = [[InlineKeyboardButton("Start!", callback_data="push_step_1")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["push_step"] = 1  

        await query.edit_message_text(text, reply_markup=reply_markup)
        return PUSH_WORKOUT

    elif step == 1:
        
        text = "First exercise is push ups 3 sets 8 to 10 reps!"
        keyboard = [[InlineKeyboardButton("Start set 1", callback_data="push_step_2")]]
        reply_markup = InlineKeyboardMarkup(keyboard)   

        context.user_data["push_step"] = 2  # Move to Step 2        
        await query.edit_message_text(text, reply_markup=reply_markup)
        return PUSH_WORKOUT
    
    elif step == 2:
        text = "Your target 8-10 reps, with 25 pounds weight!"
        keyboard = [[InlineKeyboardButton("Set done!", callback_data="push_step_3")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data["push_step"] = 3
        await query.edit_message_text(text, reply_markup=reply_markup)
        return PUSH_WORKOUT

    elif step == 3:
        text = "Good job on set 1! take 1:30 min break!"
        keyboard = [[InlineKeyboardButton("Break done!", callback_data="push_step_3")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data["push_step"] = 4
        await query.edit_message_text(text, reply_markup=reply_markup)
        return PUSH_WORKOUT
    
    else:
        # Handle unknown state
        await query.edit_message_text("Unknown step. Please restart the workout.")
        return MENU

# Main function
def main():
    print('Starting bot....')

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)], 
        states={
            MENU: [CallbackQueryHandler(start_question_button)],
            PUSH_WORKOUT: [
                CallbackQueryHandler(push, pattern="^push_step_\\d+$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )

    app.add_handler(conv_handler)
    print('Polling...')
    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
