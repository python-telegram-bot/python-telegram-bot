f

# --- 1. CONFIGURATION ---
# REPLACE THESE WITH YOUR ACTUAL VALUES!
BOT_TOKEN = "8543434272:AAFmwQfhh15HrNnyZpNnxO6WfPkeUNd2uqQ"
# This is the URL you copied from Railway
DATABASE_URL = "YOUR_POSTGRESQL_CONNECTION_URL" 

# --- 2. DATABASE CONNECTION FUNCTION ---
def get_db_connection():
    # Helper function to connect to the DB
    result = urlparse(DATABASE_URL)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

# --- 3. BOT COMMANDS AND HANDLERS ---

# Dictionary to hold conversational state for incomplete registrations
user_registration_state = {} 

# All city options (This list should be extensive in the real bot)
CITIES_INDIA = ["Bengaluru", "Jaipur", "New Delhi", "Mumbai", "Chennai"] 
COUNTRIES = ["India", "USA", "UK"]

# Start of Registration /start
async def start_command(update: Update, context):
    user_id = update.effective_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT nickname FROM users WHERE user_id = %s", (user_id,))
    if cursor.fetchone():
        await update.message.reply_text("👋 Welcome back! You are already registered. Type /find to look for a match.")
        cursor.close()
        conn.close()
        return

    # Start the registration process
    await update.message.reply_text("🤖 Welcome to the anonymous matching bot! Let's set up your profile.")
    await update.message.reply_text("First, please choose an **anonymous nickname** (e.g., 'StarDust').")
    user_registration_state[user_id] = {'step': 'NICKNAME'} # Set state for next message handler

    cursor.close()
    conn.close()

# Handler for collecting registration messages (Nickname, City, etc.)
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    
    if user_id not in user_registration_state:
        # User is not in a registration flow, so ignore or give them a default message
        return

    state = user_registration_state[user_id]
    
    if state['step'] == 'NICKNAME':
        # 1. Save Nickname
        nickname = update.message.text.strip()
        user_registration_state[user_id]['nickname'] = nickname
        
        # 2. Ask for Category
        keyboard = [
            [InlineKeyboardButton("Single", callback_data='category_Single')],
            [InlineKeyboardButton("Married", callback_data='category_Married')],
            [InlineKeyboardButton("Gay", callback_data='category_Gay')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"✅ Nickname saved as **{nickname}**. Now, please select your primary group:",
            reply_markup=reply_markup
        )
        user_registration_state[user_id]['step'] = 'WAITING_CATEGORY_SELECTION'
    
    # Other message handling (like city input if we used manual text, but we'll use buttons)
    # The rest of the flow is handled by the `handle_callback_query` for buttons!

# Handler for inline button clicks (Category, Preferences, City)
async def handle_callback_query(update: Update, context):
    query = update.callback_query
    await query.answer() # Acknowledge the button press
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_registration_state:
        await query.edit_message_text("Sorry, your registration session expired. Please type /start again.")
        return

    state = user_registration_state[user_id]
    
    # --- Step 2: Handle Category Selection ---
    if data.startswith('category_'):
        category = data.split('_')[1]
        user_registration_state[user_id]['category'] = category
        
        # 3. Ask for Preferences (Multi-Select)
        # We'll keep a simple single selection for now, but the code can be adapted for multiple
        keyboard = [
            [InlineKeyboardButton("Match only with my category", callback_data='pref_self')],
            [InlineKeyboardButton("Match with Single", callback_data='pref_Single')],
            [InlineKeyboardButton("Match with Married", callback_data='pref_Married')],
            [InlineKeyboardButton("Match with Gay", callback_data='pref_Gay')],
            [InlineKeyboardButton("Match with Anyone", callback_data='pref_all')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ Category saved as **{category}**. Who are you open to matching with?",
            reply_markup=reply_markup
        )
        user_registration_state[user_id]['step'] = 'WAITING_PREFERENCE_SELECTION'

    # --- Step 3: Handle Preference Selection ---
    elif data.startswith('pref_'):
        preference = data.split('_')[1]
        
        # Logic to determine the final list of preferences
        if preference == 'self':
            preferences_list = [state['category']]
        elif preference == 'all':
            preferences_list = ['Single', 'Married', 'Gay']
        else:
            preferences_list = [preference] # Simple single selection for now
            
        user_registration_state[user_id]['preferences'] = preferences_list
        
        # 4. Ask for Country
        keyboard = [[InlineKeyboardButton(country, callback_data=f'country_{country}')] for country in COUNTRIES]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ Preferences saved. Finally, please select your country:",
            reply_markup=reply_markup
        )
        user_registration_state[user_id]['step'] = 'WAITING_COUNTRY_SELECTION'

    # --- Step 4: Handle Country Selection (We assume only India for this example) ---
    elif data.startswith('country_'):
        country = data.split('_')[1]
        user_registration_state[user_id]['country'] = country
        
        # 5. Ask for City
        if country == "India":
            keyboard = [[InlineKeyboardButton(city, callback_data=f'city_{city}')] for city in CITIES_INDIA]
        else:
            # Add logic for other countries here
            keyboard = [[InlineKeyboardButton("Other City", callback_data='city_Other')]]
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ Country saved. Now select your city for local matching:",
            reply_markup=reply_markup
        )
        user_registration_state[user_id]['step'] = 'WAITING_CITY_SELECTION'

    # --- Step 5: Handle City Selection and FINAL SAVE ---
    elif data.startswith('city_'):
        city = data.split('_')[1]
        
        # Prepare data for insertion
        final_data = user_registration_state[user_id]
        nickname = final_data['nickname']
        category = final_data['category']
        preferences = final_data['preferences']
        
        # Save to Database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # The INSERT statement must match your SQL table definition
            cursor.execute("""
                INSERT INTO users (user_id, nickname, category, preferences, city) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, nickname, category, preferences, city))
            
            conn.commit()
            await query.edit_message_text(
                f"🎉 **Registration Complete!**\n\n"
                f"Nickname: **{nickname}**\n"
                f"Category: **{category}**\n"
                f"Matching City: **{city}**\n\n"
                f"You are all set. Type **/find** to look for a local match!"
            )
            
        except Exception as e:
            conn.rollback()
            await query.edit_message_text(f"❌ An error occurred during saving: {e}. Please try /start again.")
        
        finally:
            cursor.close()
            conn.close()
            del user_registration_state[user_id] # Clear the state

# --- 4. MAIN FUNCTION TO RUN THE BOT ---

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers for the registration flow
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    
