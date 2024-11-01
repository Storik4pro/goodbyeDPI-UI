import Cocoa
import objc


def hide_title_bar(win_id):
    native_view = objc.objc_object(c_void_p=win_id.__int__())
    native_window = native_view.window()
    native_window.setStyleMask_(
        native_window.styleMask() | Cocoa.NSFullSizeContentViewWindowMask)
    native_window.setTitlebarAppearsTransparent_(True)
    native_window.setMovableByWindowBackground_(False)
    native_window.setMovable_(False)
    native_window.setTitleVisibility_(Cocoa.NSWindowTitleHidden)
