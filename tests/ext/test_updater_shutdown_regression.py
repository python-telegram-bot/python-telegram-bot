import asyncio
import datetime as dtm

from telegram import Update


async def test_polling_stop_does_not_acknowledge_inflight_update(updater, monkeypatch):
    pending = [Update(update_id=1)]
    poll_calls = 0
    cleanup_calls = 0
    first_poll_started = asyncio.Event()
    first_poll_block = asyncio.Event()
    update_fetched = asyncio.Event()

    async def delete_webhook(*args, **kwargs):
        return True

    async def get_updates(*args, **kwargs):
        nonlocal poll_calls, cleanup_calls

        if kwargs.get("timeout") == dtm.timedelta(seconds=0):
            cleanup_calls += 1
            if pending:
                return [pending.pop(0)]
            return []

        poll_calls += 1
        if poll_calls == 1:
            first_poll_started.set()
            await first_poll_block.wait()

        if pending:
            update = pending.pop(0)
            update_fetched.set()
            return [update]
        return []

    monkeypatch.setattr(updater.bot, "delete_webhook", delete_webhook)
    monkeypatch.setattr(updater.bot, "get_updates", get_updates)

    async with updater:
        await updater.start_polling()
        await first_poll_started.wait()

        await updater.stop()

        assert pending == [Update(update_id=1)]
        assert cleanup_calls == 0

        await updater.start_polling()
        await update_fetched.wait()
        assert updater.update_queue.get_nowait().update_id == 1
        await updater.stop()
