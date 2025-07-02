def echo(update, context):
    """
    /echo:
    a simple echo function that replies the same text
    """
    update.message.reply_text(update.message.text)