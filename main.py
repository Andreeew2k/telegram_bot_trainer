from typing import Final
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler, CallbackContext
from database import init_db, insert_record, get_records
from datetime import datetime

TOKEN: Final = "7261291465:AAHNpFlX8lsO41z-M41gtjlrlTW3IrFZf5Y"
BOT_USERNAME: Final = "personal_gym_training_bot"
MENU, PUSH, PULL, LEGS, PUSH_WORKOUT = range(5)

EXERCISE_CONFIG = {
    "bench_press": {
        "name": "Bench Press",
        "sets": 3,
        "reps": [8, 9, 10],  # Possible reps per set
        "description": "Chest exercise with a barbell or dumbbells.",
    },
    "pull_ups": {
        "name": "Pull-ups",
        "sets": 3,
        "reps": [8, 10],  # Limited options
        "description": "Upper-body exercise targeting back and biceps.",
    },
    "squats": {
        "name": "Squats",
        "sets": 4,
        "reps": [10, 12, 15],
        "description": "Leg exercise to build lower-body strength.",
    },
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Push", callback_data="push")],
    ]
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

    # Get the step from callback data or user data
    callback_data = query.data
    step = context.user_data.get("push_step", 1)
    exercise_details = list(EXERCISE_CONFIG.keys())
    exercise_name = exercise_details[0]
    exercise_config = EXERCISE_CONFIG.get(exercise_name, {})

    await query.edit_message_text(exercise_details)

    if step == 1:

        text = f"Today we start with {exercise_config.get('name', 1)}"

        keyboard = [[InlineKeyboardButton("Start!", callback_data="set_perform")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["push_step"] = 2  # Move to Step 2
        return PUSH_WORKOUT

    elif step == 2:
        text = "Good Job We recorded your progress!"

        keyboard = [[InlineKeyboardButton(f"Next exercise", callback_data="push_step_3")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["current_exercise"] = exercise_name  
        await query.edit_message_text(text, reply_markup=reply_markup)
        return PUSH_WORKOUT

    else:
        # Handle unknown state
        await query.edit_message_text("Unknown step. Please restart the workout.")
        return MENU


async def set_perform(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Fetch exercise details
    exercise_name = context.user_data.get("current_exercise", "Unknown Exercise")
    exercise_config = EXERCISE_CONFIG.get(exercise_name, {})
    total_sets = exercise_config.get("sets", 3)  # Default to 3 sets if not specified
    reps = max(exercise_config.get("reps", [8, 10]))  # Default reps

    # Track the current set
    current_set = context.user_data.get("current_set", 1)

    if current_set <= total_sets:
        # Prepare message for the current set
        text = (
            f"Set {current_set}/{total_sets}\n"
            f"Target: {reps} reps!\n"
            f"Exercise: {exercise_name.replace('_', ' ').title()}"
        )
        keyboard = [[InlineKeyboardButton(f"Set {current_set} done!", callback_data="set_done")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)

        # Update the current set for the next call
        context.user_data["current_set"] = current_set + 1
        return PUSH_WORKOUT
    else:
        # If all sets are completed
        await query.edit_message_text(f"All {total_sets} sets completed for {exercise_name.replace('_', ' ').title()}! Well done!")
        context.user_data["current_set"] = 1  # Reset for future use
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
                CallbackQueryHandler(set_perform, pattern="^set_perform$"),
                 CallbackQueryHandler(set_perform, pattern="^set_done$"),


            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )

    app.add_handler(conv_handler)
    print('Polling...')
    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()
