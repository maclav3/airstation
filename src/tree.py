def print_tree(_path, indent=0):
    """
    Recursively prints the directory tree starting from the given path.
    """

    from os import ilistdir

    try:
        for entry in ilistdir(_path):
            entry_path = _path + "/" + entry[0]
            if entry[1] == 0x4000:
                print(" " * indent + "├── " + entry[0] + "/")
                print_tree(entry_path, indent + 4)
            else:
                print(" " * indent + "├── " + entry[0])
    except OSError:
        print(" " * indent + "└── " + _path.split("/")[-1] + " (inaccessible)")


if __name__ == "__main__":
    print_tree("/")
