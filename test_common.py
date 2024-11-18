"""Auxiliary functions used by more than one test file."""


def get(filename, varname):
    """Read a value from a ML-KEM-*.txt file."""
    prefix = varname + " = "
    with open(filename, encoding="utf8") as f:
        for line in f:
            if line.startswith(prefix):
                val = line.strip()[len(prefix) :]
                break
    # is this a list of integers?
    if val[0] == "{":
        end = val.find("}")
        lst = [int(v) for v in val[1:end].split(", ")]
        # the list is followed by its serialized version
        start = end + len("} = ")
        ser = bytes.fromhex(val[start:])

        return lst, ser

    # if not, it must be bytes
    return bytes.fromhex(val)
