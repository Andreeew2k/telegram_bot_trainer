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


# Initialize the database
init_db()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Push", callback_data="push")],
        [InlineKeyboardButton("Pull", callback_data="pull")],
        [InlineKeyboardButton("Legs", callback_data="legs")],
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
    elif query.data == "pull":
        await query.edit_message_text(text="You selected Pull")
        return PULL
    elif query.data == "legs":
        await query.edit_message_text(text="You selected Legs")
        return LEGS
    else:
        await query.edit_message_text(text="Unknown option")
        return MENU

async def push(update: Update, context: CallbackContext):
    """Handles the Push workout flow."""
    query = update.callback_query
    await query.answer()

    # Get the step from callback data or user data
    callback_data = query.data
    step = context.user_data.get("push_step", 1)

    if callback_data == "push_step_1" or step == 1:
        text = "Push Workout Plan:\n1. Bench Press - 3x8-10\n2. Shoulder Press - 3x10\n3. Push-ups - 3x15\n\nStart when ready!"
        keyboard = [[InlineKeyboardButton("Start Exercise 1", callback_data="push_step_2")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["push_step"] = 2  # Move to Step 2
        return PUSH_WORKOUT

    elif callback_data == "push_step_2" or step == 2:
        # Step 2: First exercise first set
        text = "Exercise 1: Bench Press - 3 sets, 8-10 reps"

        keyboard = [[InlineKeyboardButton(f"Log Bench Press set 1", callback_data="push_step_3")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["push_step"] = 3  # Move to Step 3
        context.user_data["current_exercise"] = "bench_press"
        return PUSH_WORKOUT

    elif callback_data == "push_step_3" or step == 3:
        # Step 3: Log exercise data
        text = "How many reps did you complete for Bench Press?"
        keyboard = [
            [InlineKeyboardButton("8 reps", callback_data="log_reps_8")],
            [InlineKeyboardButton("10 reps", callback_data="log_reps_10")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["next_step"] = push  # Return to the push flow after logging
        context.user_data["push_step"] = 4
        return PUSH_WORKOUT

    elif callback_data == "push_step_4" or step == 4:
        # Step 2: First exercise first set
        text = "Exercise 1: Bench Press - 2 sets, 8-10 reps"

        keyboard = [[InlineKeyboardButton(f"Log Bench Press set 2", callback_data="push_step_5")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["push_step"] = 5  # Move to Step 3
        context.user_data["current_exercise"] = "bench_press"
        return PUSH_WORKOUT

    elif callback_data == "push_step_5" or step == 5:
        # Step 3: Log exercise data
        text = "How many reps did you complete for Bench Press?"
        keyboard = [
            [InlineKeyboardButton("8 reps", callback_data="log_reps_8")],
            [InlineKeyboardButton("10 reps", callback_data="log_reps_10")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["next_step"] = push  # Return to the push flow after logging
        context.user_data["push_step"] = 6
        return PUSH_WORKOUT
    
    elif callback_data == "push_step_6" or step == 6:
        # Step 2: First exercise first set
        text = "Exercise 1: Bench Press - 1 set, 8-10 reps"

        keyboard = [[InlineKeyboardButton(f"Log Bench Press set 3", callback_data="push_step_6")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["push_step"] = 7
        context.user_data["current_exercise"] = "bench_press"
        return PUSH_WORKOUT

    elif callback_data == "push_step_7" or step == 7:
        # Step 3: Log exercise data
        text = "How many reps did you complete for Bench Press?"
        keyboard = [
            [InlineKeyboardButton("8 reps", callback_data="log_reps_8")],
            [InlineKeyboardButton("10 reps", callback_data="log_reps_10")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
        context.user_data["next_step"] = push  # Return to the push flow after logging
        context.user_data["push_step"] = 8
        return PUSH_WORKOUT


    else:
        # Handle unknown state
        await query.edit_message_text("Unknown step. Please restart the workout.")
        return MENU

async def log_reps(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Extract reps from callback_data (e.g., "log_reps_8" -> 8)
    reps = int(query.data.split("_")[-1])

    # Fetch the current exercise and user info from context
    exercise = context.user_data.get("current_exercise", "Unknown Exercise")
    user_id = update.effective_user.id
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the data to the database
    insert_record(exercise, date, reps, user_id)

    # Notify the user
    await query.edit_message_text(f"Recorded: {exercise}, {reps} reps on {date}!")

    # Determine the next step dynamically
    next_step = context.user_data.get("next_step")
    if next_step:
        # Dynamically call the next step function
        return await next_step(update, context)

    # If no next step is defined, return to MENU
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
                CallbackQueryHandler(log_reps, pattern="^log_reps_\\d+$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )

    app.add_handler(CallbackQueryHandler(log_reps, pattern="^log_reps_\\d+$"))

    app.add_handler(conv_handler)
    print('Polling...')
    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()
