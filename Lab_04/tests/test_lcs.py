from algorithms import lcs_iter, lcs_memo, lcs_naive


def test_lcs_empty_strings() -> None:
    assert lcs_naive("", "") == 0
    assert lcs_memo("", "ABC")[0] == 0
    assert lcs_iter("XYZ", "") == 0


def test_lcs_identical_and_disjoint() -> None:
    assert lcs_memo("PYTHON", "PYTHON")[0] == 6
    assert lcs_iter("PYTHON", "PYTHON") == 6
    assert lcs_memo("ABC", "DEF")[0] == 0
    assert lcs_iter("ABC", "DEF") == 0


def test_lcs_standard_cases() -> None:
    s1, s2 = "AGGTAB", "GXTXAYB"  # LCS: "GTAB" -> довжина 4
    assert lcs_naive(s1, s2) == 4
    length, info = lcs_memo(s1, s2)
    assert length == 4
    assert "hits=" in info
    assert lcs_iter(s1, s2) == 4


def test_lcs_long_strings_iter_vs_memo() -> None:
    s1 = "LONGESTCOMMONSUBSEQUENCEEXAMPLE"
    s2 = "DYNAMICPROGRAMMINGAPPROACH"
    memo_len, _ = lcs_memo(s1, s2)
    iter_len = lcs_iter(s1, s2)
    assert memo_len == iter_len