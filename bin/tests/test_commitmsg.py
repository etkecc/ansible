from conftest import load_script

commitmsg = load_script('commitmsg.py')


def test_update_add_remove():
    msg = commitmsg.format_message({
        'foo': '1.0 -> 2.0',
        'bar': '3.0',
        'baz': '4.0 -> ',
    })
    assert 'update foo (1.0 -> 2.0); ' in msg
    assert 'add bar (3.0); ' in msg
    assert 'remove baz (4.0); ' in msg
    assert '-> )' not in msg  # the dangling-arrow bug must not come back


def test_no_changes_is_skip_ci():
    assert commitmsg.format_message({}) == "[skip ci] update without version changes"
