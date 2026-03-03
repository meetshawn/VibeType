import json
import os
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Optional

import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf
from pynput import keyboard as pynput_keyboard

from sensevoice_service import svc

DEFAULT_HOTKEY = "Ctrl+Shift+Space"
SAMPLE_RATE = 16000
CHANNELS = 1
BG = "#edf3f8"
CARD_BG = "#ffffff"
TEXT = "#1f2937"
SUBTEXT = "#5b6575"
PRIMARY = "#0b67ff"
ACCENT = "#14b8a6"
BORDER = "#d8e1ec"
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

I18N = {
    "zh": {
        "title": "VibeType 桌面版",
        "header_title": "VibeType 桌面语音转文字",
        "header_hotkey": "全局快捷键：{hotkey}",
        "header_desc": "在任意应用输入框聚焦后，按一次快捷键开始录音，再按一次停止并自动输入。",
        "settings": "设置",
        "control": "控制",
        "ready": "就绪，快捷键：{hotkey}",
        "ready_detail": "按一次开始录音，再按一次停止并转写。",
        "record_btn_start": "开始录音",
        "record_btn_stop": "停止并转写",
        "record_btn_busy": "识别中...",
        "recording": "录音中...",
        "recording_detail": "请说话，再按一次快捷键结束。",
        "transcribing": "识别中...",
        "transcribing_detail": "正在将语音转换为文字。",
        "inserted": "已输入到当前输入框",
        "inserted_detail": "识别完成。",
        "no_speech": "未检测到有效语音",
        "no_speech_detail": "请靠近麦克风并提高音量。",
        "meter_title": "麦克风电平",
        "meter_desc": "用于确认麦克风是否正常拾音。",
        "meter_idle": "空闲",
        "meter_busy": "识别中...",
        "meter_live": "实时电平：{pct}%",
        "history_title": "历史记录",
        "history_desc": "最新在最上。可选中复制，也可双击快速复制。",
        "copy_selected": "复制选中",
        "copy_latest": "复制最新",
        "copied_selected": "已复制选中记录",
        "copied_latest": "已复制最新记录",
        "copied_detail": "文本已写入剪贴板。",
        "hide_bg": "退到后台",
        "exit": "退出",
        "settings_title": "设置",
        "lang_title": "界面语言",
        "lang_zh": "中文",
        "lang_en": "English",
        "opt_topmost": "窗口置顶",
        "opt_hide_on_stop": "停止后退到后台",
        "hotkey_title": "自定义快捷键",
        "hotkey_hint": "示例：Ctrl+Shift+Space / Ctrl+Alt+R",
        "hotkey_apply": "应用快捷键",
        "hotkey_capture": "监听录入",
        "hotkey_capture_wait": "正在监听，请按下组合键后松开...",
        "hotkey_capture_ok": "录入成功：{hotkey}",
        "hotkey_ok": "快捷键已更新：{hotkey}",
        "hotkey_fail": "快捷键无效，请检查格式。",
        "close": "关闭",
        "err_prefix": "错误：",
        "err_detail": "请检查麦克风和模型环境。",
    },
    "en": {
        "title": "VibeType Desktop",
        "header_title": "VibeType Desktop Voice To Text",
        "header_hotkey": "Global hotkey: {hotkey}",
        "header_desc": "Focus any input box, press once to record, press again to stop and type automatically.",
        "settings": "Settings",
        "control": "Control",
        "ready": "Ready. Hotkey: {hotkey}",
        "ready_detail": "Press once to record, press again to stop and transcribe.",
        "record_btn_start": "Start Recording",
        "record_btn_stop": "Stop And Transcribe",
        "record_btn_busy": "Transcribing...",
        "recording": "Recording...",
        "recording_detail": "Speak now, press hotkey again to stop.",
        "transcribing": "Transcribing...",
        "transcribing_detail": "Converting your voice to text.",
        "inserted": "Text inserted into active input",
        "inserted_detail": "Recognition completed.",
        "no_speech": "No speech detected",
        "no_speech_detail": "Try speaking closer to the microphone.",
        "meter_title": "Microphone Level",
        "meter_desc": "This confirms whether your microphone is receiving audio.",
        "meter_idle": "Idle",
        "meter_busy": "Transcribing...",
        "meter_live": "Live level: {pct}%",
        "history_title": "History",
        "history_desc": "Newest at top. Select to copy, or double-click for quick copy.",
        "copy_selected": "Copy Selected",
        "copy_latest": "Copy Latest",
        "copied_selected": "Copied selected history",
        "copied_latest": "Copied latest history",
        "copied_detail": "Text is now in clipboard.",
        "hide_bg": "Hide To Background",
        "exit": "Exit",
        "settings_title": "Settings",
        "lang_title": "Language",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "opt_topmost": "Window always on top",
        "opt_hide_on_stop": "Send window to background after stop",
        "hotkey_title": "Custom Hotkey",
        "hotkey_hint": "Example: Ctrl+Shift+Space / Ctrl+Alt+R",
        "hotkey_apply": "Apply Hotkey",
        "hotkey_capture": "Capture",
        "hotkey_capture_wait": "Listening... press your key combo then release.",
        "hotkey_capture_ok": "Captured: {hotkey}",
        "hotkey_ok": "Hotkey updated: {hotkey}",
        "hotkey_fail": "Invalid hotkey format.",
        "close": "Close",
        "err_prefix": "Error: ",
        "err_detail": "Check microphone and model environment.",
    },
}

MOD_ALIASES = {
    "ctrl": "<ctrl>",
    "control": "<ctrl>",
    "alt": "<alt>",
    "shift": "<shift>",
    "cmd": "<cmd>",
    "win": "<cmd>",
    "meta": "<cmd>",
}

KEY_ALIASES = {
    "space": ("<space>", "Space"),
    "enter": ("<enter>", "Enter"),
    "return": ("<enter>", "Enter"),
    "tab": ("<tab>", "Tab"),
    "esc": ("<esc>", "Esc"),
    "escape": ("<esc>", "Esc"),
    "backspace": ("<backspace>", "Backspace"),
    "delete": ("<delete>", "Delete"),
    "up": ("<up>", "Up"),
    "down": ("<down>", "Down"),
    "left": ("<left>", "Left"),
    "right": ("<right>", "Right"),
}


class Recorder:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stream: Optional[sd.InputStream] = None
        self._frames: list[np.ndarray] = []
        self._level = 0.0
        self.recording = False
        self.busy = False

    def _callback(self, indata, frames, time, status):  # noqa: ANN001
        if status:
            return
        self._frames.append(indata.copy())
        rms = float(np.sqrt(np.mean(np.square(indata)))) if indata.size else 0.0
        with self._lock:
            self._level = min(1.0, rms * 8.0)

    def start(self) -> bool:
        with self._lock:
            if self.recording or self.busy:
                return False
            self._frames = []
            self._level = 0.0
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()
            self.recording = True
            return True

    def stop(self) -> Optional[str]:
        with self._lock:
            if not self.recording or self.busy or self._stream is None:
                return None
            self.busy = True
            self.recording = False
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._level = 0.0
            if not self._frames:
                self.busy = False
                return ""
            audio = np.concatenate(self._frames, axis=0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            temp_path = tmp.name
        try:
            sf.write(temp_path, audio, SAMPLE_RATE)
            return svc.transcribe_file(temp_path)
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass
            with self._lock:
                self.busy = False

    def get_level(self) -> float:
        with self._lock:
            return self._level


def card(parent: tk.Widget) -> tk.Frame:
    return tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1, bd=0)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(data: dict) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def parse_hotkey(user_text: str) -> tuple[str, str]:
    tokens = [t.strip().lower() for t in user_text.split("+") if t.strip()]
    if not tokens:
        raise ValueError("empty hotkey")

    mods: list[str] = []
    main_pynput = ""
    main_display = ""

    for token in tokens:
        if token in MOD_ALIASES:
            mod = MOD_ALIASES[token]
            if mod not in mods:
                mods.append(mod)
            continue

        if token in KEY_ALIASES:
            if main_pynput:
                raise ValueError("multiple non-modifier keys")
            main_pynput, main_display = KEY_ALIASES[token]
            continue

        if token.startswith("f") and token[1:].isdigit():
            if main_pynput:
                raise ValueError("multiple non-modifier keys")
            idx = int(token[1:])
            if idx < 1 or idx > 24:
                raise ValueError("invalid function key")
            main_pynput = f"<f{idx}>"
            main_display = f"F{idx}"
            continue

        if len(token) == 1 and token.isalnum():
            if main_pynput:
                raise ValueError("multiple non-modifier keys")
            main_pynput = token
            main_display = token.upper()
            continue

        raise ValueError("unsupported key token")

    if not main_pynput:
        raise ValueError("missing main key")

    order = ["<ctrl>", "<alt>", "<shift>", "<cmd>"]
    mods = [m for m in order if m in mods]
    display_map = {"<ctrl>": "Ctrl", "<alt>": "Alt", "<shift>": "Shift", "<cmd>": "Cmd"}
    display_parts = [display_map[m] for m in mods] + [main_display]
    pynput_parts = mods + [main_pynput]
    return "+".join(display_parts), "+".join(pynput_parts)


def token_from_pynput_key(key: pynput_keyboard.Key | pynput_keyboard.KeyCode) -> Optional[str]:
    if isinstance(key, pynput_keyboard.KeyCode):
        ch = key.char
        if ch and ch.isalnum():
            return ch.upper()
        return None

    mapping = {
        pynput_keyboard.Key.ctrl: "Ctrl",
        pynput_keyboard.Key.ctrl_l: "Ctrl",
        pynput_keyboard.Key.ctrl_r: "Ctrl",
        pynput_keyboard.Key.alt: "Alt",
        pynput_keyboard.Key.alt_l: "Alt",
        pynput_keyboard.Key.alt_r: "Alt",
        pynput_keyboard.Key.shift: "Shift",
        pynput_keyboard.Key.shift_l: "Shift",
        pynput_keyboard.Key.shift_r: "Shift",
        pynput_keyboard.Key.cmd: "Cmd",
        pynput_keyboard.Key.cmd_l: "Cmd",
        pynput_keyboard.Key.cmd_r: "Cmd",
        pynput_keyboard.Key.space: "Space",
        pynput_keyboard.Key.enter: "Enter",
        pynput_keyboard.Key.tab: "Tab",
        pynput_keyboard.Key.esc: "Esc",
        pynput_keyboard.Key.backspace: "Backspace",
        pynput_keyboard.Key.delete: "Delete",
        pynput_keyboard.Key.up: "Up",
        pynput_keyboard.Key.down: "Down",
        pynput_keyboard.Key.left: "Left",
        pynput_keyboard.Key.right: "Right",
    }
    return mapping.get(key)


def main() -> None:
    recorder = Recorder()
    cfg = load_config()
    root = tk.Tk()
    root.geometry("760x560")
    root.minsize(760, 560)
    root.configure(bg=BG)

    lang_var = tk.StringVar(value=str(cfg.get("language", "zh")))
    topmost_var = tk.BooleanVar(value=bool(cfg.get("topmost", True)))
    hide_on_stop_var = tk.BooleanVar(value=bool(cfg.get("hide_on_stop", True)))
    hotkey_var = tk.StringVar(value=str(cfg.get("hotkey", DEFAULT_HOTKEY)))
    status_var = tk.StringVar()
    subtitle_var = tk.StringVar()
    button_var = tk.StringVar()

    widgets: dict[str, tk.Widget] = {}
    settings_window: Optional[tk.Toplevel] = None
    hotkey_listener: Optional[pynput_keyboard.GlobalHotKeys] = None
    current_hotkey_display = DEFAULT_HOTKEY
    root.attributes("-topmost", bool(topmost_var.get()))

    def tr(key: str, **fmt: object) -> str:
        text = I18N.get(lang_var.get(), I18N["en"]).get(key, key)
        return text.format(**fmt) if fmt else text

    def set_status(text: str, detail: str = "") -> None:
        status_var.set(text)
        subtitle_var.set(detail)

    def apply_topmost() -> None:
        root.attributes("-topmost", bool(topmost_var.get()))

    def persist_config() -> None:
        save_config(
            {
                "language": lang_var.get(),
                "topmost": bool(topmost_var.get()),
                "hide_on_stop": bool(hide_on_stop_var.get()),
                "hotkey": hotkey_var.get(),
            }
        )

    def hide_to_background() -> None:
        if topmost_var.get():
            root.attributes("-topmost", False)
        root.iconify()
        root.after(150, apply_topmost)

    def add_history(text: str) -> None:
        history_list.insert(0, text)
        while history_list.size() > 10:
            history_list.delete(tk.END)

    def copy_text(value: str, status_key: str) -> None:
        if not value:
            return
        root.clipboard_clear()
        root.clipboard_append(value)
        set_status(tr(status_key), tr("copied_detail"))

    def copy_selected() -> None:
        selection = history_list.curselection()
        if not selection:
            return
        copy_text(history_list.get(selection[0]), "copied_selected")

    def copy_latest() -> None:
        if history_list.size() == 0:
            return
        copy_text(history_list.get(0), "copied_latest")

    def finish_transcribe() -> None:
        try:
            text = recorder.stop() or ""
            clean = text.strip()
            if clean:
                keyboard.write(clean, delay=0)
                root.after(0, lambda: set_status(tr("inserted"), tr("inserted_detail")))
                root.after(0, lambda c=clean: add_history(c))
            else:
                root.after(0, lambda: set_status(tr("no_speech"), tr("no_speech_detail")))
        except Exception as exc:
            err_msg = f"{tr('err_prefix')}{exc}"
            root.after(0, lambda m=err_msg: set_status(m, tr("err_detail")))
        finally:
            root.after(0, lambda: button_var.set(tr("record_btn_start")))
            if hide_on_stop_var.get():
                root.after(0, hide_to_background)

    def toggle_record() -> None:
        if recorder.busy:
            return
        if not recorder.recording:
            if recorder.start():
                set_status(tr("recording"), tr("recording_detail"))
                button_var.set(tr("record_btn_stop"))
        else:
            set_status(tr("transcribing"), tr("transcribing_detail"))
            button_var.set(tr("record_btn_busy"))
            threading.Thread(target=finish_transcribe, daemon=True).start()

    def on_hotkey() -> None:
        root.after(0, toggle_record)

    def bind_hotkey(user_hotkey: str) -> None:
        nonlocal hotkey_listener, current_hotkey_display
        display, pynput_expr = parse_hotkey(user_hotkey)
        new_listener = pynput_keyboard.GlobalHotKeys({pynput_expr: on_hotkey})
        new_listener.start()
        old_listener = hotkey_listener
        hotkey_listener = new_listener
        current_hotkey_display = display
        hotkey_var.set(display)
        if old_listener is not None:
            try:
                old_listener.stop()
            except Exception:
                pass

    def refresh_ui_texts() -> None:
        root.title(tr("title"))
        widgets["header_title"].config(text=tr("header_title"))
        widgets["header_hotkey"].config(text=tr("header_hotkey", hotkey=current_hotkey_display))
        widgets["header_desc"].config(text=tr("header_desc"))
        widgets["settings_btn"].config(text=tr("settings"))
        widgets["control_title"].config(text=tr("control"))
        widgets["meter_title"].config(text=tr("meter_title"))
        widgets["meter_desc"].config(text=tr("meter_desc"))
        widgets["history_title"].config(text=tr("history_title"))
        widgets["history_desc"].config(text=tr("history_desc"))
        widgets["copy_selected_btn"].config(text=tr("copy_selected"))
        widgets["copy_latest_btn"].config(text=tr("copy_latest"))
        widgets["hide_btn"].config(text=tr("hide_bg"))
        widgets["exit_btn"].config(text=tr("exit"))
        set_status(tr("ready", hotkey=current_hotkey_display), tr("ready_detail"))
        if not recorder.recording and not recorder.busy:
            button_var.set(tr("record_btn_start"))

    def open_settings() -> None:
        nonlocal settings_window
        if settings_window and settings_window.winfo_exists():
            settings_window.deiconify()
            settings_window.lift()
            settings_window.attributes("-topmost", True)
            settings_window.after(100, lambda: settings_window.attributes("-topmost", False))
            settings_window.focus_force()
            return

        settings_window = tk.Toplevel(root)
        settings_window.geometry("390x340")
        settings_window.resizable(False, False)
        settings_window.configure(bg=CARD_BG)
        settings_window.transient(root)
        settings_window.lift()
        settings_window.attributes("-topmost", True)
        settings_window.after(100, lambda: settings_window.attributes("-topmost", False))
        settings_window.focus_force()

        hotkey_input = tk.StringVar(value=hotkey_var.get())
        capture_hint_var = tk.StringVar(value="")

        lang_title = tk.Label(settings_window, bg=CARD_BG, fg=TEXT, font=("Segoe UI", 11, "bold"))
        lang_title.pack(anchor="w", padx=16, pady=(14, 6))
        rb_zh = tk.Radiobutton(settings_window, value="zh", variable=lang_var, bg=CARD_BG, selectcolor=CARD_BG, command=refresh_ui_texts)
        rb_zh.pack(anchor="w", padx=16)
        rb_en = tk.Radiobutton(settings_window, value="en", variable=lang_var, bg=CARD_BG, selectcolor=CARD_BG, command=refresh_ui_texts)
        rb_en.pack(anchor="w", padx=16, pady=(0, 8))

        topmost_ck = tk.Checkbutton(settings_window, variable=topmost_var, command=apply_topmost, bg=CARD_BG, selectcolor=CARD_BG)
        topmost_ck.pack(anchor="w", padx=16, pady=(0, 4))
        hide_ck = tk.Checkbutton(settings_window, variable=hide_on_stop_var, bg=CARD_BG, selectcolor=CARD_BG)
        hide_ck.pack(anchor="w", padx=16, pady=(0, 10))

        hotkey_title = tk.Label(settings_window, bg=CARD_BG, fg=TEXT, font=("Segoe UI", 11, "bold"))
        hotkey_title.pack(anchor="w", padx=16, pady=(0, 6))
        hotkey_entry = tk.Entry(settings_window, textvariable=hotkey_input, font=("Segoe UI", 10))
        hotkey_entry.pack(fill="x", padx=16, pady=(0, 4))
        hotkey_hint = tk.Label(settings_window, bg=CARD_BG, fg=SUBTEXT, font=("Segoe UI", 9))
        hotkey_hint.pack(anchor="w", padx=16, pady=(0, 4))
        capture_hint_label = tk.Label(settings_window, textvariable=capture_hint_var, bg=CARD_BG, fg=PRIMARY, font=("Segoe UI", 9, "bold"))
        capture_hint_label.pack(anchor="w", padx=16, pady=(0, 8))

        def apply_hotkey_from_settings() -> None:
            candidate = hotkey_input.get().strip()
            try:
                bind_hotkey(candidate)
                persist_config()
                refresh_ui_texts()
                set_status(tr("hotkey_ok", hotkey=current_hotkey_display), tr("ready_detail"))
                capture_hint_var.set("")
            except Exception:
                messagebox.showerror(tr("settings_title"), tr("hotkey_fail"))

        def capture_hotkey_from_listener() -> None:
            capture_hint_var.set(tr("hotkey_capture_wait"))
            capture_btn.config(state="disabled")
            pressed: set[str] = set()
            released: list[str] = []
            done = threading.Event()

            def on_press(key: pynput_keyboard.Key | pynput_keyboard.KeyCode) -> None:
                token = token_from_pynput_key(key)
                if token:
                    pressed.add(token)

            def on_release(key: pynput_keyboard.Key | pynput_keyboard.KeyCode) -> bool | None:
                token = token_from_pynput_key(key)
                if token and token in pressed and token not in released:
                    released.append(token)
                if pressed and all(t in released for t in pressed):
                    done.set()
                    return False
                return None

            def worker() -> None:
                with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                    done.wait(timeout=5)
                    listener.stop()

                if not pressed:
                    root.after(
                        0,
                        lambda: (
                            capture_hint_var.set(tr("hotkey_fail")),
                            capture_btn.config(state="normal"),
                        ),
                    )
                    return

                order = ["Ctrl", "Alt", "Shift", "Cmd"]
                mods = [m for m in order if m in pressed]
                mains = [k for k in released if k not in order]
                if not mains:
                    root.after(
                        0,
                        lambda: (
                            capture_hint_var.set(tr("hotkey_fail")),
                            capture_btn.config(state="normal"),
                        ),
                    )
                    return

                candidate = "+".join(mods + [mains[-1]])

                def apply_candidate() -> None:
                    try:
                        bind_hotkey(candidate)
                        hotkey_input.set(current_hotkey_display)
                        persist_config()
                        refresh_ui_texts()
                        capture_hint_var.set(tr("hotkey_capture_ok", hotkey=current_hotkey_display))
                        set_status(tr("hotkey_ok", hotkey=current_hotkey_display), tr("ready_detail"))
                    except Exception:
                        capture_hint_var.set(tr("hotkey_fail"))
                    finally:
                        capture_btn.config(state="normal")

                root.after(0, apply_candidate)

            threading.Thread(target=worker, daemon=True).start()

        capture_btn = tk.Button(settings_window, command=capture_hotkey_from_listener, relief="flat", bg="#dce9ff", fg=TEXT)
        capture_btn.pack(anchor="w", padx=16, pady=(0, 6))
        apply_btn = tk.Button(settings_window, command=apply_hotkey_from_settings, relief="flat", bg="#e8eef8", fg=TEXT)
        apply_btn.pack(anchor="w", padx=16, pady=(0, 10))
        close_btn = tk.Button(settings_window, command=settings_window.destroy, relief="flat", bg="#e8eef8", fg=TEXT)
        close_btn.pack(anchor="e", padx=16, pady=(0, 12))

        def refresh_settings_texts() -> None:
            if settings_window and settings_window.winfo_exists():
                settings_window.title(tr("settings_title"))
                lang_title.config(text=tr("lang_title"))
                rb_zh.config(text=tr("lang_zh"))
                rb_en.config(text=tr("lang_en"))
                topmost_ck.config(text=tr("opt_topmost"))
                hide_ck.config(text=tr("opt_hide_on_stop"))
                hotkey_title.config(text=tr("hotkey_title"))
                hotkey_hint.config(text=tr("hotkey_hint"))
                apply_btn.config(text=tr("hotkey_apply"))
                capture_btn.config(text=tr("hotkey_capture"))
                close_btn.config(text=tr("close"))

        settings_window._refresh_texts = refresh_settings_texts  # type: ignore[attr-defined]

        def on_destroy(event: tk.Event) -> None:  # noqa: ARG001
            nonlocal settings_window
            settings_window = None

        settings_window.bind("<Destroy>", on_destroy)
        refresh_settings_texts()

    def on_close() -> None:
        if hotkey_listener is not None:
            try:
                hotkey_listener.stop()
            except Exception:
                pass
        root.destroy()

    outer = tk.Frame(root, bg=BG)
    outer.pack(fill="both", expand=True, padx=18, pady=18)

    header = card(outer)
    header.pack(fill="x", pady=(0, 14))
    widgets["header_title"] = tk.Label(header, bg=CARD_BG, fg=TEXT, font=("Segoe UI", 18, "bold"))
    widgets["header_title"].pack(anchor="w", padx=18, pady=(16, 6))
    widgets["header_hotkey"] = tk.Label(header, bg=CARD_BG, fg=SUBTEXT, font=("Segoe UI", 11))
    widgets["header_hotkey"].pack(anchor="w", padx=18, pady=(0, 6))
    widgets["header_desc"] = tk.Label(header, bg=CARD_BG, fg=SUBTEXT, wraplength=700, justify="left", font=("Segoe UI", 10))
    widgets["header_desc"].pack(anchor="w", padx=18, pady=(0, 12))
    widgets["settings_btn"] = tk.Button(header, command=open_settings, relief="flat", bg="#e8eef8", fg=TEXT, padx=14, pady=7, cursor="hand2")
    widgets["settings_btn"].pack(anchor="e", padx=18, pady=(0, 14))

    body = tk.Frame(outer, bg=BG)
    body.pack(fill="both", expand=True)
    body.grid_columnconfigure(0, weight=3)
    body.grid_columnconfigure(1, weight=2)
    body.grid_rowconfigure(0, weight=1)
    body.grid_rowconfigure(1, weight=1)

    control_card = card(body)
    control_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
    widgets["control_title"] = tk.Label(control_card, bg=CARD_BG, fg=TEXT, font=("Segoe UI", 14, "bold"))
    widgets["control_title"].pack(anchor="w", padx=16, pady=(14, 8))
    tk.Label(control_card, textvariable=status_var, bg=CARD_BG, fg=PRIMARY, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16)
    tk.Label(control_card, textvariable=subtitle_var, bg=CARD_BG, fg=SUBTEXT, wraplength=400, justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(6, 10))
    tk.Button(
        control_card,
        textvariable=button_var,
        command=toggle_record,
        bg=PRIMARY,
        fg="white",
        activebackground="#0957d0",
        activeforeground="white",
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=18,
        pady=10,
        cursor="hand2",
    ).pack(anchor="w", padx=16, pady=(0, 14))

    meter_card = card(body)
    meter_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 0))
    widgets["meter_title"] = tk.Label(meter_card, bg=CARD_BG, fg=TEXT, font=("Segoe UI", 14, "bold"))
    widgets["meter_title"].pack(anchor="w", padx=16, pady=(14, 8))
    widgets["meter_desc"] = tk.Label(meter_card, bg=CARD_BG, fg=SUBTEXT, wraplength=400, justify="left", font=("Segoe UI", 10))
    widgets["meter_desc"].pack(anchor="w", padx=16, pady=(0, 10))
    meter_canvas = tk.Canvas(meter_card, width=420, height=34, bg="#eef4fb", bd=0, highlightthickness=0)
    meter_canvas.pack(anchor="w", padx=16, pady=(0, 12))
    meter_fill = meter_canvas.create_rectangle(0, 0, 0, 34, fill=ACCENT, width=0)
    meter_text = tk.Label(meter_card, bg=CARD_BG, fg=SUBTEXT, font=("Segoe UI", 10))
    meter_text.pack(anchor="w", padx=16, pady=(0, 14))

    history_card = card(body)
    history_card.grid(row=0, column=1, rowspan=2, sticky="nsew")
    widgets["history_title"] = tk.Label(history_card, bg=CARD_BG, fg=TEXT, font=("Segoe UI", 14, "bold"))
    widgets["history_title"].pack(anchor="w", padx=16, pady=(14, 8))
    widgets["history_desc"] = tk.Label(history_card, bg=CARD_BG, fg=SUBTEXT, wraplength=240, justify="left", font=("Segoe UI", 10))
    widgets["history_desc"].pack(anchor="w", padx=16, pady=(0, 10))

    history_wrap = tk.Frame(history_card, bg=CARD_BG)
    history_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 10))
    history_scroll = tk.Scrollbar(history_wrap)
    history_scroll.pack(side="right", fill="y")
    history_list = tk.Listbox(
        history_wrap,
        height=14,
        activestyle="none",
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        font=("Segoe UI", 10),
        yscrollcommand=history_scroll.set,
    )
    history_list.pack(side="left", fill="both", expand=True)
    history_scroll.config(command=history_list.yview)
    history_list.bind("<Double-Button-1>", lambda e: copy_selected())
    history_list.bind("<Control-c>", lambda e: copy_selected())

    actions = tk.Frame(history_card, bg=CARD_BG)
    actions.pack(fill="x", padx=16, pady=(0, 12))
    widgets["copy_selected_btn"] = tk.Button(actions, command=copy_selected, relief="flat", bg="#e8eef8", fg=TEXT, padx=12, pady=7, cursor="hand2")
    widgets["copy_selected_btn"].pack(fill="x", pady=(0, 6))
    widgets["copy_latest_btn"] = tk.Button(actions, command=copy_latest, relief="flat", bg="#e8eef8", fg=TEXT, padx=12, pady=7, cursor="hand2")
    widgets["copy_latest_btn"].pack(fill="x", pady=(0, 6))
    widgets["hide_btn"] = tk.Button(actions, command=hide_to_background, relief="flat", bg="#e8eef8", fg=TEXT, padx=12, pady=7, cursor="hand2")
    widgets["hide_btn"].pack(fill="x", pady=(0, 6))
    widgets["exit_btn"] = tk.Button(actions, command=on_close, relief="flat", bg="#f8e9e9", fg="#8b1e1e", padx=12, pady=7, cursor="hand2")
    widgets["exit_btn"].pack(fill="x")

    def update_meter() -> None:
        level = recorder.get_level() if recorder.recording else 0.0
        meter_canvas.coords(meter_fill, 0, 0, int(420 * level), 34)
        if recorder.busy:
            meter_text.config(text=tr("meter_busy"))
        elif recorder.recording:
            meter_text.config(text=tr("meter_live", pct=int(level * 100)))
        else:
            meter_text.config(text=tr("meter_idle"))
        root.after(80, update_meter)

    def on_language_changed(*args: object) -> None:
        refresh_ui_texts()
        if settings_window and settings_window.winfo_exists() and hasattr(settings_window, "_refresh_texts"):
            settings_window._refresh_texts()  # type: ignore[attr-defined]
        persist_config()

    lang_var.trace_add("write", on_language_changed)
    topmost_var.trace_add("write", lambda *args: persist_config())
    hide_on_stop_var.trace_add("write", lambda *args: persist_config())

    root.protocol("WM_DELETE_WINDOW", on_close)

    try:
        bind_hotkey(hotkey_var.get())
    except Exception:
        bind_hotkey(DEFAULT_HOTKEY)

    refresh_ui_texts()
    persist_config()
    update_meter()

    try:
        root.mainloop()
    except Exception as exc:
        messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    main()
