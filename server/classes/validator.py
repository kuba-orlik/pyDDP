import json


def attributesPresent(needles, haystack):
    for needle in needles:
        if not needle in haystack:
            return False
    return True

def isCorerctJSON(string):
    try:
        json.loads(string)
    except Exception as e:
        print(str(e))
        return False
    return True