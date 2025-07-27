# Modified version of ansible oneline callback plugin
# source: https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/callback/oneline.py
# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: etkeline
    type: stdout
    short_description: modified oneline Ansible screen output
    version_added: historical
    description:
        - The original plugin is the output callback used by the -o/--one-line command line option.
'''

from ansible import constants as C
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor


class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'etkeline'

    def __init__(self):
        self._last_task_banner = None
        super(CallbackModule, self).__init__()

    def _command_generic_msg(self, hostname, result, caption):
        stdout = result.get('stdout', '').replace('\n', '\\n').replace('\r', '\\r')
        task_name = result._task.get_name().strip()
        if 'stderr' in result and result['stderr']:
            stderr = result.get('stderr', '').replace('\n', '\\n').replace('\r', '\\r')
            return "%s | %s | rc=%s | (stdout) %s (stderr) %s" % (caption, task_name, result.get('rc', -1), stdout, stderr)
        else:
            return "%s | %s | rc=%s | (stdout) %s" % (caption, task_name, result.get('rc', -1), stdout)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if 'exception' in result._result:
            msg = "An exception occurred during task execution. The full traceback is:\n" + result._result['exception']
            if result._task.action in C.MODULE_NO_JSON and 'module_stderr' not in result._result:
                self._display.display(self._command_generic_msg(result._host.get_name(), result._result, '✖'), color=C.COLOR_ERROR)
            else:
                self._display.display(msg, color=C.COLOR_ERROR)

        self._clean_results(result._result, result._task.action)
        if self._last_task_banner == result._task._uuid:
            return
        self._last_task_banner = result._task._uuid
        self._display.display("x | %s => %s" % (result._task.get_name().strip(), self._dump_results(result._result, indent=2).replace("\\\\r\\\\n", "\n")), color=C.COLOR_ERROR)

    def v2_runner_on_ok(self, result):
        if result._result.get('changed', False):
            color = C.COLOR_CHANGED
            state = '+'
        else:
            color = C.COLOR_OK
            state = '✓'

        msg = "%s | %s" % (state, result._task.get_name().strip())
        if self._run_is_verbose(result):
            msg += " => %s" % (self._dump_results(result._result, indent=2))
        self._clean_results(result._result, result._task.action)
        if self._last_task_banner == result._task._uuid:
            return
        self._last_task_banner = result._task._uuid
        self._display.display(msg, color=color)

    def v2_runner_on_unreachable(self, result):
        self._clean_results(result._result, result._task.action)
        if self._last_task_banner == result._task._uuid:
            return
        self._last_task_banner = result._task._uuid
        self._display.display("☠ => %s" % (result._result.get('msg', '')), color=C.COLOR_UNREACHABLE)

    def v2_runner_on_skipped(self, result):
        pass

    def __item_line(self, state, result):
        return "%s | %s" % (state, self._get_item_label(result._result))


    def v2_runner_item_on_ok(self, result):
        if result._result.get('changed', False):
            color = C.COLOR_CHANGED
            state = '+'
        else:
            color = C.COLOR_OK
            state = '✓'

        msg = self.__item_line(state, result)
        if self._run_is_verbose(result):
            msg += " => %s" % (self._dump_results(result._result, indent=2))
        self._clean_results(result._result, result._task.action)
        if self._last_task_banner != result._task._uuid:
            self.v2_runner_on_ok(result)
        self._display.display(msg, color=color)

    def v2_runner_item_on_failed(self, result, ignore_errors=False):
        if 'exception' in result._result:
            msg = "An exception occurred during task execution. The full traceback is:\n" + result._result['exception']
            if result.task.action in C.MODULE_NO_JSON and 'module_stderr' not in result._result:
                self._display.display(self._command_generic_msg(result._host.get_name(), result._result, '✖'), color=C.COLOR_ERROR)
            else:
                self._display.display(msg, color=C.COLOR_ERROR)

        msg = "%s => %s" % (self.__item_line("x", result), self._dump_results(result._result, indent=2).replace("\\\\r\\\\n", "\n"))
        self._clean_results(result._result, result.task.action)
        if self._last_task_banner != result.task._uuid:
            self.v2_runner_on_failed(result)
        self._display.display(msg, color=C.COLOR_ERROR)

    def v2_playbook_on_no_hosts_matched(self):
        self._display.display("skipping: no hosts matched", color=C.COLOR_SKIP)

    def v2_playbook_on_no_hosts_remaining(self):
        self._display.banner("NO MORE HOSTS LEFT")

    def v2_playbook_on_stats(self, stats):
        self._display.banner("PLAY RECAP")

        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)

            self._display.display(
                u"%s: %s %s %s %s %s %s %s" % (
                    hostcolor(h, t),
                    colorize(u'ok', t['ok'], C.COLOR_OK),
                    colorize(u'changed', t['changed'], C.COLOR_CHANGED),
                    colorize(u'unreachable', t['unreachable'], C.COLOR_UNREACHABLE),
                    colorize(u'failed', t['failures'], C.COLOR_ERROR),
                    colorize(u'skipped', t['skipped'], C.COLOR_SKIP),
                    colorize(u'rescued', t['rescued'], C.COLOR_OK),
                    colorize(u'ignored', t['ignored'], C.COLOR_WARN),
                ),
                screen_only=True
            )

            self._display.display(
                u"%s: %s %s %s %s %s %s %s" % (
                    hostcolor(h, t, False),
                    colorize(u'ok', t['ok'], None),
                    colorize(u'changed', t['changed'], None),
                    colorize(u'unreachable', t['unreachable'], None),
                    colorize(u'failed', t['failures'], None),
                    colorize(u'skipped', t['skipped'], None),
                    colorize(u'rescued', t['rescued'], None),
                    colorize(u'ignored', t['ignored'], None),
                ),
                log_only=True
            )

        self._display.display("", screen_only=True)
