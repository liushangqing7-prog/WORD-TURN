from word_replacer import parse_rules, ReplacementRule


def test_parse_rules_ok():
    raw = """
# comment
literal:甲方=>采购方
regex:(\\d+)=>编号-$1
"""
    rules = parse_rules(raw)
    assert len(rules) == 2
    assert rules[0] == ReplacementRule(mode="literal", source="甲方", target="采购方")


def test_parse_rules_invalid_line():
    try:
        parse_rules("bad line")
    except ValueError as exc:
        assert "格式错误" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_regex_group_replacement():
    rule = ReplacementRule(mode="regex", source=r"(\d+)", target="编号-$1")
    assert rule.apply("ID: 42") == "ID: 编号-42"
