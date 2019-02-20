import platform
import subprocess
import os

def durationToSeconds(strDuration):
    tokens = strDuration[: -1].split(":")
    res = int(tokens[0]) * 3600 + int(tokens[1]) * 60 + float(tokens[2])
    return res

def sep():
    return "\\" if platform.system() == "Windows" else "/"

def formatFields(record):
    return ",".join(list(record.keys()))

def formatWildcards(values):
    return ",".join("?" * len(values))


def parseResolution(resolution):
    resolution = resolution.split("x")
    return {
        "WIDTH" : resolution[0],
        "HEIGHT": resolution[1]
    }

def parseCodec(token):
    res = dict()
    border = token.index(' ')
    res["CODEC"] = token[ : border]
    res["CODEC_PROFILE"] = token[border + 1 : ][1 : -1]
    return res

def parseColor(tokens):
    border = tokens.index('(')
    return {
        "COLOR_ENCODING": tokens[ : border]
    }

def parseResolutionAndRation(token):
    tokens = token.split(' ')
    res = parseResolution(tokens[0])
    res["SAR"] = tokens[2]
    res["DAR"] = tokens[4][ : -1]
    return res

def parseStreamInfo(streamInfo):
    res = dict()
    tokens = " ".join(streamInfo[3 : ])
    tokens = tokens.split(", ")
    res = {**res, **parseCodec(tokens[0])}
    while (tokens[1][-1] != ")"):
        tokens[1] += tokens[2]
        tokens.pop(2)
    res = {**res, **parseColor(tokens[1])}
    res = {**res, **parseResolutionAndRation(tokens[2])}
    res["FPS"] = int(tokens[3].split(' ')[0])
    return res

def getInfo(video):
    tmp = "tmp"
    out = open(tmp, "w")
    subprocess.run(["ffmpeg", "-i", video], stderr = out)
    out.close()
    out = open(tmp, "r")
    content = out.readlines()
    out.close()
    res = dict()
    res["VIDEO_NAME"] = video.split(sep())[-1]
    for line in content:
        tokens = line.strip().split()
        if (tokens[0] == "Duration:" and len(tokens) != 2):
            strDuration = tokens[1]
            res["DURATION"] = durationToSeconds(strDuration)
            res["BITRATE"]  = int(tokens[-2])
        if (tokens[0] == "Stream" and tokens[2] == "Video:"):
            res = {**res, **parseStreamInfo(tokens)}
    os.remove(tmp)
    return res