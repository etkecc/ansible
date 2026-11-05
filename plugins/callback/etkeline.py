# (c) 2012-2014 Michael DeHaan, 2017 Ansible Project; modified oneline callback, GPL-3.0+

from __future__ import annotations

DOCUMENTATION = '''
name: etkeline
type: stdout
short_description: timestamped one-line output
description: One line per task result, plus one per loop item.
'''

import typing as t
from datetime import datetime, timezone

from ansible import constants as C
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor

if t.TYPE_CHECKING:
    from ansible.executor.task_result import CallbackTaskResult


class CallbackModule(CallbackBase):
    """Timestamped one-line stdout callback derived from the oneline callback."""

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'etkeline'

    def __init__(self):
        self._task_lines = {}
        super().__init__()

    def _ts(self) -> str:
        now = datetime.now(timezone.utc)
        return "%s.%03d" % (now.strftime('%H:%M:%S'), now.microsecond // 1000)

    @staticmethod
    def _task_name(result: CallbackTaskResult) -> str:
        return result.task.get_name().strip()

    @staticmethod
    def _state(result: CallbackTaskResult) -> tuple[str, str]:
        if result.result.get('changed', False):
            return '+', C.COLOR_CHANGED
        return '✓', C.COLOR_OK

    @staticmethod
    def _key(result: CallbackTaskResult) -> tuple[str, str]:
        return result.task._uuid, result.host.get_name()

    def _print_task_line(self, result: CallbackTaskResult, state: str, color: str, details: str = '') -> None:
        """Print the task line once; item callbacks claim it, the task's result handler releases it."""
        key = self._key(result)
        if key in self._task_lines:
            return
        self._task_lines[key] = state

        msg = "%s %s | %s" % (self._ts(), state, self._task_name(result))
        if details:
            msg += " => %s" % details
        self._display.display(msg, color=color)

    def _print_item_line(self, result: CallbackTaskResult, state: str, color: str, details: str = '') -> None:
        msg = "%s %s | %s" % (self._ts(), state, self._get_item_label(result.result))
        if details:
            msg += " => %s" % details
        self._display.display(msg, color=color)

    def v2_runner_on_failed(self, result: CallbackTaskResult, ignore_errors: bool = False) -> None:
        self._handle_warnings_and_exception(result)
        self._clean_results(result.result, result.task.action)
        shown = self._task_lines.pop(self._key(result), None)
        if result.task.loop and 'results' in result.result:
            if shown != 'x':  # failed items already carried their full results
                self._display.display("%s x | %s" % (self._ts(), self._task_name(result)), color=C.COLOR_ERROR)
            return
        self._display.display(
            "%s x | %s => %s" % (self._ts(), self._task_name(result), self._dump_results(result.result, indent=2)),
            color=C.COLOR_ERROR,
        )

    def v2_runner_on_ok(self, result: CallbackTaskResult) -> None:
        self._handle_warnings_and_exception(result)
        key = self._key(result)
        if self._task_lines.pop(key, None) is not None:
            return  # loop items already reported this task
        self._clean_results(result.result, result.task.action)
        state, color = self._state(result)
        details = self._dump_results(result.result, indent=2) if self._run_is_verbose(result) else ''
        self._print_task_line(result, state, color, details)
        self._task_lines.pop(key, None)

    def v2_runner_on_unreachable(self, result: CallbackTaskResult) -> None:
        self._handle_warnings_and_exception(result)
        self._task_lines.pop(self._key(result), None)
        self._display.display(
            "%s ☠ | %s => %s" % (self._ts(), self._task_name(result), self._dump_results(result.result, indent=2)),
            color=C.COLOR_UNREACHABLE,
        )

    def v2_runner_on_skipped(self, result: CallbackTaskResult) -> None:
        self._handle_warnings_and_exception(result)
        key = self._key(result)
        if self._task_lines.pop(key, None) is None and C.DISPLAY_SKIPPED_HOSTS:
            self._print_task_line(result, '-', C.COLOR_SKIP)
            self._task_lines.pop(key, None)

    def v2_runner_item_on_ok(self, result: CallbackTaskResult) -> None:
        self._handle_warnings_and_exception(result)
        self._clean_results(result.result, result.task.action)
        state, color = self._state(result)
        self._print_task_line(result, state, color)
        details = self._dump_results(result.result, indent=2) if self._run_is_verbose(result) else ''
        self._print_item_line(result, state, color, details)

    def v2_runner_item_on_failed(self, result: CallbackTaskResult) -> None:
        self._handle_warnings_and_exception(result)
        self._clean_results(result.result, result.task.action)
        self._print_task_line(result, 'x', C.COLOR_ERROR)
        self._print_item_line(result, 'x', C.COLOR_ERROR, self._dump_results(result.result, indent=2))

    def v2_runner_item_on_skipped(self, result: CallbackTaskResult) -> None:
        self._handle_warnings_and_exception(result)
        if C.DISPLAY_SKIPPED_HOSTS:
            self._print_task_line(result, '-', C.COLOR_SKIP)
            self._print_item_line(result, '-', C.COLOR_SKIP)

    def v2_on_file_diff(self, result: CallbackTaskResult) -> None:
        state, color = self._state(result)
        details = ''
        if self._run_is_verbose(result) and not result.task.loop:
            self._clean_results(result.result, result.task.action)
            details = self._dump_results(result.result, indent=2)
        self._print_task_line(result, state, color, details)
        diff = result.result.get('diff')
        if diff:
            text = self._get_diff(diff)
            if text:
                self._display.display(text)

    def v2_playbook_on_no_hosts_matched(self) -> None:
        self._display.display("skipping: no hosts matched", color=C.COLOR_SKIP)

    def v2_playbook_on_no_hosts_remaining(self) -> None:
        self._display.banner("NO MORE HOSTS LEFT")

    def v2_playbook_on_stats(self, stats) -> None:
        self._display.banner("PLAY RECAP")

        hosts = sorted(stats.processed.keys())
        for h in hosts:
            summary = stats.summarize(h)

            self._display.display(
                u"%s: %s %s %s %s %s %s %s" % (
                    hostcolor(h, summary),
                    colorize(u'ok', summary['ok'], C.COLOR_OK),
                    colorize(u'changed', summary['changed'], C.COLOR_CHANGED),
                    colorize(u'unreachable', summary['unreachable'], C.COLOR_UNREACHABLE),
                    colorize(u'failed', summary['failures'], C.COLOR_ERROR),
                    colorize(u'skipped', summary['skipped'], C.COLOR_SKIP),
                    colorize(u'rescued', summary['rescued'], C.COLOR_OK),
                    colorize(u'ignored', summary['ignored'], C.COLOR_WARN),
                ),
                screen_only=True
            )

            self._display.display(
                u"%s: %s %s %s %s %s %s %s" % (
                    hostcolor(h, summary, False),
                    colorize(u'ok', summary['ok'], None),
                    colorize(u'changed', summary['changed'], None),
                    colorize(u'unreachable', summary['unreachable'], None),
                    colorize(u'failed', summary['failures'], None),
                    colorize(u'skipped', summary['skipped'], None),
                    colorize(u'rescued', summary['rescued'], None),
                    colorize(u'ignored', summary['ignored'], None),
                ),
                log_only=True
            )

        self._display.display("", screen_only=True)
