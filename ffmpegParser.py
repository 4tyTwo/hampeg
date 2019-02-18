import subprocess
import os

def durationToSeconds(strDuration):
    tokens = strDuration[: -1].split(":")
    res = int(tokens[0]) * 3600 + int(tokens[1]) * 60 + float(tokens[2])
    return res

def parseResolution(resolution):
    resolution = resolution.split("x")
    return {
        "WIDTH" : resolution[0],
        "HEIGHT": resolution[1]
    }

def parseStreamInfo(streamInfo):
    res = dict()
    res["CODEC"] = streamInfo[3]
    res["CODEC_PROFILE"] = streamInfo[4][1 : -2]
    res["COLOR_ENCODING"] = streamInfo[5][ : -1]
    res = {**res, **parseResolution(streamInfo[6])} # merge dicts
    res["SAR"] = streamInfo[8]
    res["DAR"] = streamInfo[10][ : -2]
    res["FPS"] = streamInfo[11]
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
    res["VIDEO_NAME"] = video.split("/")[-1]
    for line in content:
        tokens = line.strip().split()
        if (tokens[0] == "configuration:"):
            res["CONFIG"] = " ".join(tokens[1 : ])
        if (tokens[0] == "Duration:" and len(tokens) != 2):
            strDuration = tokens[1]
            res["DURATION"] = durationToSeconds(strDuration)
            res["BITRATE"]  = int(tokens[-2])
        if (tokens[0] == "Stream" and tokens[2] == "Video:"):
            res = {**res, **parseStreamInfo(tokens)}
    os.remove(tmp)
    return res
