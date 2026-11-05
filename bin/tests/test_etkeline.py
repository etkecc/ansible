"""etkeline callback tests: real dispatch through throwaway ansible-playbook runs."""

import os
import shutil
import subprocess
import textwrap

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYBOOK = shutil.which('ansible-playbook')

pytestmark = pytest.mark.skipif(PLAYBOOK is None, reason='ansible-core is not installed')

WARN_MODULE = (
    'from ansible.module_utils.basic import AnsibleModule\n'
    'module = AnsibleModule(argument_spec={})\n'
    'module.warn("module warning surfaced")\n'
    'module.exit_json(changed=False, msg="warned")\n'
)


def run_playbook(tmp_path, tasks, *args):
    play = '- name: etkeline smoke\n  hosts: localhost\n  gather_facts: false\n  tasks:\n'
    play += textwrap.indent(tasks.strip(), '    ') + '\n'
    (tmp_path / 'play.yml').write_text(play)
    (tmp_path / 'inventory').write_text('[local]\nlocalhost ansible_connection=local\n')
    (tmp_path / 'ansible.cfg').write_text('[defaults]\n')
    library = tmp_path / 'library'
    library.mkdir()
    (library / 'warnmod.py').write_text(WARN_MODULE)

    env = os.environ.copy()
    env.update(
        ANSIBLE_CONFIG=str(tmp_path / 'ansible.cfg'),
        ANSIBLE_CALLBACK_PLUGINS=os.path.join(REPO, 'plugins', 'callback'),
        ANSIBLE_STDOUT_CALLBACK='etkeline',
        ANSIBLE_NOCOLOR='1',
        ANSIBLE_NOCOWS='1',
        ANSIBLE_FORKS='1',
        ANSIBLE_DISPLAY_SKIPPED_HOSTS='0',
        ANSIBLE_RETRY_FILES_ENABLED='0',
    )
    result = subprocess.run(
        [PLAYBOOK, '-i', str(tmp_path / 'inventory'), str(tmp_path / 'play.yml'), *args],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120,
    )
    return result, result.stdout + result.stderr


def test_ok_task_is_a_single_line(tmp_path):
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: run true',
        '  ansible.builtin.command: /bin/true',
    ]))
    assert result.returncode == 0, out
    assert len([line for line in out.splitlines() if '| run true' in line]) == 1
    assert '"changed"' not in out


def test_loop_ok_prints_one_task_line(tmp_path):
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: loop true',
        '  ansible.builtin.command: "{{ item }}"',
        '  loop: [/bin/true, /bin/true]',
    ]))
    assert result.returncode == 0, out
    assert len([line for line in out.splitlines() if '| loop true' in line]) == 1


def test_loop_failure_dumps_failed_item(tmp_path):
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: loop with a failure',
        '  ansible.builtin.command: "{{ item }}"',
        '  loop: [/bin/true, /bin/false]',
        '  ignore_errors: true',
    ]))
    assert result.returncode == 0, out
    assert 'Callback dispatch' not in out
    assert '"rc": 1' in out
    assert 'loop with a failure' in out


def test_module_warning_is_shown(tmp_path):
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: warn',
        '  warnmod:',
    ]))
    assert result.returncode == 0, out
    assert 'module warning surfaced' in out


def test_exception_details_are_shown(tmp_path):
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: broken template',
        '  ansible.builtin.debug:',
        '    msg: "{{ missing_etkeline_var }}"',
        '  ignore_errors: true',
    ]))
    assert result.returncode == 0, out
    assert 'Callback dispatch' not in out
    assert '[ERROR]' in out
    assert 'broken template' in out
    assert 'missing_etkeline_var' in out


def test_skipped_tasks_stay_quiet(tmp_path):
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: silent skip',
        '  ansible.builtin.debug:',
        '    msg: nope',
        '  when: false',
    ]))
    assert result.returncode == 0, out
    assert 'silent skip' not in out


def test_diff_output_is_shown(tmp_path):
    target = tmp_path / 'diff.txt'
    result, out = run_playbook(tmp_path, '\n'.join([
        '- name: write file',
        '  ansible.builtin.copy:',
        '    dest: "%s"' % target,
        '    content: "one\\n"',
        '- name: change file',
        '  ansible.builtin.copy:',
        '    dest: "%s"' % target,
        '    content: "two\\n"',
    ]), '--diff')
    assert result.returncode == 0, out
    assert '--- before' in out
    assert '+two' in out
