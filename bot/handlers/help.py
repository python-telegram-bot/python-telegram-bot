def help_command(update, context):
    """
    /help:
    return this help
    """
    from .index import index
    text = '<b>HELP:</b>\n'
    for k, v in index().items():
        text += v.__doc__
    update.message.reply_text(text, parse_mode='HTML')
