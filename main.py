import subprocess
import importlib
import os
import dbOps
import hampegUtils
import time
from subprocess import Popen, STDOUT
import platform


def deleteIfExists(filename):
    if os.path.isfile(filename):
        os.remove(filename)

def run(command):
    if platform.system() == "Windows":
        return windowsRun(command)
    else:
        return unixRun(command)

def windowsRun(command):
    start = time.time()
    DEVNULL = open(os.devnull, 'wb', 0)
    subprocess.call(command, stderr=STDOUT)
    elapsed = round(time.time() - start, 4)

    DEVNULL.close()
    return {
        "REAL_T": elapsed
    }

def unixRun(command):
    start = time.time()
    DEVNULL = open(os.devnull, 'wb', 0)
    p = Popen(command, stdout=DEVNULL, stderr=STDOUT)
    ru = os.wait4(p.pid, 0)[2]
    elapsed = round(time.time() - start, 4)
    DEVNULL.close()
    return {
        "REAL_T": elapsed,
        "USER_T": ru.ru_utime,
        "SYSTEM_T": ru.ru_stime
    }


def setupAndRun(dbcon, video_table_name, res_table_name, command, hwaccel, hwaccel_type = ""):
    output_path = command[-1]
    input_path = command[command.index("-i") + 1]
    deleteIfExists(output_path)
    runInfo = run(command)
    srcInfo = hampegUtils.getInfo(input_path)
    srcId = dbOps.recordId(conn, video_table_name, srcInfo)
    if (srcId == -1):
        dbOps.insert(conn, video_table_name, srcInfo)
        srcId = dbOps.recordId(conn, video_table_name, srcInfo)

    destInfo = hampegUtils.getInfo(output_path)
    destId = dbOps.recordId(conn, video_table_name, destInfo)
    if (destId == -1):
        dbOps.insert(conn, video_table_name, destInfo)
        destId = dbOps.recordId(conn, video_table_name, destInfo)

    runInfo["SOURCE"] = srcId
    runInfo["DEST"] = destId
    runInfo["HWACCEL"] = hwaccel
    runInfo["HWACCEL_TYPE"] = hwaccel_type
    dbOps.insert(conn, res_table_name, runInfo)

def test(dbcon, video_table_name, res_table_name, commandPair):
    cpu_command = commandPair["cpu"]
    setupAndRun(dbcon, video_table_name, res_table_name, cpu_command, False)
    gpu_command = commandPair["gpu"]
    hwaccel_type = commandPair["hwaccel type"]
    setupAndRun(dbcon, video_table_name, res_table_name, gpu_command, True, hwaccel_type)
    

def streamtest(dbcon, video_table_name, res_table_name, commands):
    i = 1
    for commandPair in commands:
        print("Running command pair №", i)
        test(dbcon, video_table_name, res_table_name, commandPair)
        print("Command pair №", i, "finished")
        time.sleep(10) # cooldown to avoid throttling
        i += 1

database_name = "acceleration.db"
if not(os.path.isfile(database_name)):
    dbOps.setupDb()
conn = dbOps.connectToDb(database_name)
input_name = str("resources/input/white_noise_h264.mkv")

commandPair0 = {
    "cpu": ['ffmpeg', '-i', input_name, '-c:v', 'h264',       '-b:v', '74278k', "resources/output/white_noise_h264.mkv"],
    "gpu": ['ffmpeg', '-i', input_name, '-c:v', 'h264_nvenc', '-b:v', '74278k', "resources/output/white_noise_h264_nvenc.mkv"],
    "hwaccel type":  "h264_nvenc"
}

commandPair1 = {
    "cpu": ['ffmpeg', '-i', input_name, '-c:v', 'libx265',    '-b:v', '74278k', "resources/output/white_noise_hevc.mkv"],
    "gpu": ['ffmpeg', '-i', input_name, '-c:v', 'hevc_nvenc', '-b:v', '74278k', "resources/output/white_noise_hevc_nvenc.mkv"],
    "hwaccel type":  "hevc_nvenc"
}

commandPair2 = {
    "cpu": ['ffmpeg', '-c:v', 'h264', '-i', input_name, '-vcodec', 'h264', '-b:v', '74278k', "resources/output/white_noise_transcode_h264.mkv"],
    "gpu": ['ffmpeg', '-hwaccel', 'cuvid', '-c:v', 'h264_cuvid', '-i', input_name, '-vcodec', 'h264_nvenc', '-b:v', '74278k', "resources/output/white_noise_cuvid_h264.mkv"],
    "hwaccel type": "h264_cuvid h264_nvenc"
}

commandPair3 = {
    "cpu": ['ffmpeg', '-c:v', 'h264', '-i', input_name, '-vcodec', 'libx265', '-b:v', '74278k', "resources/output/white_noise_trancode_hevc.mkv"],
    "gpu": ['ffmpeg', '-hwaccel', 'cuvid', '-c:v', 'h264_cuvid', '-i', input_name, '-vcodec', 'hevc_nvenc', '-b:v', '74278k', "resources/output/white_noise_cuvid_h264.mkv"],
    "hwaccel type": "h264_cuvid hevc_nvenc"  
}

streamtest(conn, "VIDEO_INFO", "RUN_INFO", [commandPair0, commandPair1, commandPair2, commandPair3])
time.sleep(15)
streamtest(conn, "VIDEO_INFO", "RUN_INFO", [commandPair0, commandPair1, commandPair2, commandPair3])
time.sleep(15)
streamtest(conn, "VIDEO_INFO", "RUN_INFO", [commandPair0, commandPair1, commandPair2, commandPair3])

conn.close()
print("Finished")
