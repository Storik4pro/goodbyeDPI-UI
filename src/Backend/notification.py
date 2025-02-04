from PySide6.QtCore import QObject, Slot
from PySide6.QtCore import QProcess, Signal, QThread
from qasync import QEventLoop, asyncSlot
from toasted import ToastDismissReason

from utils import show_error, show_message
from _data import text


class Toast(QObject):
    notificationAction = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.notifications = {}

    @asyncSlot(str, str, str)
    async def show_notification(self, notification_id, title, message, callback=None):
        self.notifications[notification_id] = callback

        result = await show_message("GoodbyeDPI_app", title, message)

        if result.dismiss_reason == ToastDismissReason.NOT_DISMISSED:
            action = "user_not_dismissed"
        elif result.dismiss_reason == ToastDismissReason.APPLICATION_HIDDEN:
            action = "application_hidden"
        else:
            action = "other"

        self.notificationAction.emit(notification_id, action)

    @asyncSlot(str, str, str, str, str)
    async def show_error(
        self, notification_id, title, message, button1, button2, callback=None
    ):
        self.notifications[notification_id] = callback

        result = await show_error(
            "GoodbyeDPI_app",
            title,
            message,
            button1,
            button2 if button2 != "" else None,
        )

        if result.dismiss_reason == ToastDismissReason.NOT_DISMISSED:
            action = "user_not_dismissed"
        elif result.dismiss_reason == ToastDismissReason.APPLICATION_HIDDEN:
            action = "application_hidden"
        else:
            action = "other"

        self.notificationAction.emit(notification_id, action)
