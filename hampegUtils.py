import platform

def durationToSeconds(strDuration):
    tokens = strDuration[: -1].split(":")
    res = int(tokens[0]) * 3600 + int(tokens[1]) * 60 + float(tokens[2])
    return res

def sep():
    return "\\" if platform.system() == "Windows" else "/"
