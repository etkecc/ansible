from lib import versions_md


def test_parse_ignores_non_bullets():
    text = "# Versions\n\n* Synapse: 1.100.0\n* Signal: 0.7.5\n"
    assert versions_md.parse(text) == {'Synapse': '1.100.0', 'Signal': '0.7.5'}


def test_format_lines_sorted():
    assert versions_md.format_lines({'Signal': '0.7.5', 'Synapse': '1.100.0'}) == \
        "* Signal: 0.7.5\n* Synapse: 1.100.0\n"


def test_parse_format_round_trip():
    data = {'Alpha': '1', 'Beta': '2', 'Gamma': '3'}
    assert versions_md.parse(versions_md.format_lines(data)) == data


def test_parse_diff_update_and_add():
    diff = "\n".join([
        "@@ -1,2 +1,3 @@",
        "-* Synapse: 1.100.0",
        "+* Synapse: 1.101.0",
        "+* Steam: 1.2.3",
    ])
    assert versions_md.parse_diff(diff) == {
        'synapse': '1.100.0 -> 1.101.0',
        'steam': '1.2.3',
    }
