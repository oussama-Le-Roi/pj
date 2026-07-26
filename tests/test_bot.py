#!/usr/bin/env python3
"""End-to-end tests for the Telegram AI bot against a local mock API."""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mock_server  # noqa: E402  (same directory)

SERVER, BASE = mock_server.start()

os.environ.update(
    TELEGRAM_BOT_TOKEN="123:TESTTOKEN",
    GROQ_API_KEY="groq-key",
    OPENROUTER_API_KEY="or-key",
    GEMINI_API_KEY="gem-key",
    TELEGRAM_API_BASE=BASE,
    GEMINI_API_BASE=f"{BASE}/v1beta",
    GROQ_API_URL=f"{BASE}/groq/chat/completions",
    OPENROUTER_API_URL=f"{BASE}/openrouter/chat/completions",
    SETTINGS_FILE="/tmp/test_settings.json",
    RUN_DURATION="0",
)

import bot  # noqa: E402
from providers import PROVIDERS  # noqa: E402

STATE = mock_server.STATE


def message(text, chat_id=555, update_id=1):
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "chat": {"id": chat_id},
            "from": {"first_name": "Oussama"},
            "text": text,
        },
    }


def callback(data, chat_id=555, update_id=1):
    return {
        "update_id": update_id,
        "callback_query": {
            "id": "cb1",
            "data": data,
            "message": {"message_id": 10, "chat": {"id": chat_id}},
        },
    }


class BotTests(unittest.TestCase):
    def setUp(self):
        mock_server.reset()
        bot.SETTINGS = {}
        if os.path.exists("/tmp/test_settings.json"):
            os.remove("/tmp/test_settings.json")

    # ── basics ──
    def test_token_is_validated(self):
        self.assertTrue(bot.tg_request("getMe").get("ok"))

    def test_invalid_token_reports_error(self):
        STATE["getme_ok"] = False
        result = bot.tg_request("getMe")
        self.assertFalse(result.get("ok"))
        self.assertEqual(result.get("error_code"), 404)

    def test_start_command(self):
        bot.handle_message(message("/start")["message"])
        self.assertIn("بوت الذكاء", STATE["sent"][0]["text"])

    def test_help_lists_model_command(self):
        bot.handle_message(message("/help")["message"])
        self.assertIn("/model", STATE["sent"][0]["text"])

    def test_unknown_command(self):
        bot.handle_message(message("/nope")["message"])
        self.assertIn("غير معروف", STATE["sent"][0]["text"])

    # ── AI ──
    def test_question_uses_default_provider(self):
        bot.handle_message(message("مرحبا")["message"])
        self.assertEqual(STATE["ai_calls"][0][0], "groq")
        self.assertIn("reply from groq", STATE["sent"][0]["text"])

    def test_falls_back_when_provider_fails(self):
        STATE["fail"] = {"groq"}
        bot.handle_message(message("hi")["message"])
        providers_tried = [c[0] for c in STATE["ai_calls"]]
        self.assertIn("openrouter", providers_tried)
        self.assertIn("reply from openrouter", STATE["sent"][-1]["text"])

    def test_all_providers_fail_gives_error_message(self):
        STATE["fail"] = {"groq", "openrouter", "gemini"}
        bot.handle_message(message("hi")["message"])
        self.assertIn("⚠️", STATE["sent"][-1]["text"])

    def test_long_answer_is_split(self):
        bot.send_message(555, "x" * 9000)
        self.assertEqual(len(STATE["sent"]), 3)

    # ── keyboards ──
    def test_model_command_shows_providers(self):
        bot.handle_message(message("/model")["message"])
        keyboard = STATE["sent"][0]["reply_markup"]["inline_keyboard"]
        labels = [row[0]["callback_data"] for row in keyboard]
        self.assertEqual(labels, ["p:groq", "p:openrouter", "p:gemini"])

    def test_only_configured_providers_are_offered(self):
        os.environ["OPENROUTER_API_KEY"] = ""
        try:
            keyboard = bot.provider_keyboard("groq")
            data = [row[0]["callback_data"] for row in keyboard]
            self.assertNotIn("p:openrouter", data)
        finally:
            os.environ["OPENROUTER_API_KEY"] = "or-key"

    def test_selecting_provider_shows_models(self):
        bot.handle_callback(callback("p:openrouter")["callback_query"])
        keyboard = STATE["edits"][0]["reply_markup"]["inline_keyboard"]
        data = [row[0]["callback_data"] for row in keyboard]
        self.assertIn("m:openrouter:ds", data)
        self.assertEqual(data[-1], "back")

    def test_selecting_model_persists_and_is_used(self):
        bot.handle_callback(callback("p:openrouter")["callback_query"])
        bot.handle_callback(callback("m:openrouter:ds")["callback_query"])
        self.assertEqual(bot.get_choice(555), ("openrouter", "ds"))

        # reload from disk -> preference survived
        bot.SETTINGS = bot.load_settings()
        self.assertEqual(bot.get_choice(555), ("openrouter", "ds"))

        bot.handle_message(message("سؤال")["message"])
        self.assertEqual(
            STATE["ai_calls"][0], ("openrouter", "deepseek/deepseek-chat-v3.1:free")
        )

    def test_back_button_returns_to_providers(self):
        bot.handle_callback(callback("back")["callback_query"])
        keyboard = STATE["edits"][0]["reply_markup"]["inline_keyboard"]
        self.assertTrue(all(row[0]["callback_data"].startswith("p:") for row in keyboard))

    def test_callback_is_always_answered(self):
        bot.handle_callback(callback("p:groq")["callback_query"])
        self.assertEqual(len(STATE["callbacks"]), 1)

    def test_bad_callback_data_does_not_crash(self):
        bot.handle_callback(callback("p:doesnotexist")["callback_query"])
        bot.handle_callback(callback("m:groq:nope")["callback_query"])
        self.assertEqual(len(STATE["callbacks"]), 2)

    def test_callback_data_within_telegram_limit(self):
        for pid, info in PROVIDERS.items():
            for key in info["models"]:
                self.assertLessEqual(len(f"m:{pid}:{key}".encode()), 64)

    def test_each_chat_keeps_its_own_model(self):
        bot.handle_callback(callback("m:openrouter:qw", chat_id=1)["callback_query"])
        bot.handle_callback(callback("m:groq:l8", chat_id=2)["callback_query"])
        self.assertEqual(bot.get_choice(1), ("openrouter", "qw"))
        self.assertEqual(bot.get_choice(2), ("groq", "l8"))

    # ── main loop ──
    def test_main_processes_queue_and_acknowledges(self):
        STATE["queue"] = [message("مرحبا", update_id=41)]
        bot.main()
        self.assertIn(42, STATE["offsets"])
        self.assertTrue(any("reply from" in m["text"] for m in STATE["sent"]))

    def test_main_handles_empty_queue(self):
        STATE["queue"] = []
        bot.main()
        self.assertEqual(STATE["sent"], [])

    def test_live_mode_polls_until_deadline(self):
        os.environ["RUN_DURATION"] = "2"
        import importlib
        importlib.reload(bot)
        try:
            STATE["queue"] = [message("hello", update_id=7)]
            start = time.time()
            bot.main()
            elapsed = time.time() - start
            self.assertGreaterEqual(elapsed, 1.5)
            self.assertIn(8, STATE["offsets"])
            self.assertTrue(any("reply from" in m["text"] for m in STATE["sent"]))
        finally:
            os.environ["RUN_DURATION"] = "0"
            importlib.reload(bot)

    def test_no_duplicate_model_retry(self):
        STATE["fail"] = {"groq"}
        bot.handle_message(message("hi")["message"])
        groq_models = [m for p, m in STATE["ai_calls"] if p == "groq"]
        self.assertEqual(len(groq_models), len(set(groq_models)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
