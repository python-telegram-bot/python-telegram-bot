.. tip::
    When making requests to the Bot API in an asynchronous fashion (e.g. via
    :attr:`block=False <BaseHandler.block>`, :meth:`Application.create_task`,
    :meth:`concurrent_updates` or the :class:`JobQueue`), it can happen that more requests
    are being made in parallel than there are connections in the pool.
    If the number of requests is much higher than the number of connections, even setting
    :meth:`pool_timeout` to a larger value may not always be enough to prevent pool
    timeouts.
    You should therefore set :meth:`concurrent_updates`, :meth:`connection_pool_size` and
    :meth:`pool_timeout` to values that make sense for your setup.