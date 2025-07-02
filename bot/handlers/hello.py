def hello(update, context):
    """
    /hello
    just say hello and reply
    """
    update.message.reply_text(
        'Hi {}, how are you?'.format(update.message.from_user.first_name))

