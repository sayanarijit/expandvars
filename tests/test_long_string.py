from expandvars import expandvars


def test_parsing_long_string():
    long_string = " ".join("$VAR" for _ in range(1000))
    expandvars(long_string)
