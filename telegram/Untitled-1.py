import telegram
import tensorflow as tf
import numpy as np

# Set up Telegram bot
bot = telegram.Bot(token='6174586334:AAHr5IOhdTvFupoOQAvq30HbGzLDhTeLVIU')

# Load LSTM model
model = tf.keras.models.load_model('path/to/lstm_model.h5')

# Define function to generate text based on initial seed
def generate_text(seed_text, next_words=100, temperature=1.0):
    for _ in range(next_words):
        # Convert seed text to input tensor for LSTM model
        input_seq = np.zeros((1, len(seed_text)))
        for i, char in enumerate(seed_text):
            input_seq[0, i] = char_to_index.get(char, 0)
        
        # Predict probabilities for next character using LSTM model
        predictions = model.predict(input_seq, verbose=0)[0]
        
        # Apply temperature to adjust probability distribution
        predictions = np.log(predictions) / temperature
        exp_preds = np.exp(predictions)
        predictions = exp_preds / np.sum(exp_preds)
        
        # Sample next character from probability distribution
        next_index = np.argmax(np.random.multinomial(1, predictions, 1))
        next_char = index_to_char[next_index]
        
        # Update seed text with new character
        seed_text += next_char
        
    return seed_text

# Define function to handle messages from user
def handle_message(update, context):
    # Get message text from user
    message_text = update.message.text
    
    # Generate response text based on message text
    response_text = generate_text(message_text)
    
    # Send response to user
    bot.send_message(chat_id=update.effective_chat.id, text=response_text)

# Set up message handler for bot
message_handler = telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_message)
dispatcher = bot.dispatcher
dispatcher




