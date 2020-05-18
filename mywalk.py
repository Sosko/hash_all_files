import os


def is_junction(path: str) -> bool:
    try:
        return bool(os.readlink(path))
    except OSError:
        return False
    except:
        return True


def mywalk(start_path):
    if not os.path.isdir(start_path):
        raise Exception("Not a dir")
    nextdirs = [os.path.abspath(start_path)]
    while True:
        if len(nextdirs) == 0:
            break
        d = nextdirs.pop(0)
        try:
            for file in os.listdir(d):
                file_with_path = os.path.join(d, file)
                if os.path.isfile(file_with_path):
                    yield d, file
                elif os.path.isdir(file_with_path) and not is_junction(file_with_path):
                    nextdirs.append(file_with_path)
        except PermissionError:
            yield d, PermissionError()
