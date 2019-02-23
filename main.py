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
    hwaccel = commandPair["hwaccel"]
    hwaccel_type = commandPair["hwaccel type"]
    setupAndRun(dbcon, video_table_name, res_table_name, gpu_command, hwaccel, hwaccel_type)
    


#sep = hampegUtils.sep()
#dir_path = os.path.dirname(os.path.realpath(__file__))
database_name = "acceleration.db"
#table_name = "VIDEO_INFO"
if not(os.path.isfile(database_name)):
    dbOps.setupDb()
conn = dbOps.connectToDb(database_name)
# video_name = "white_noise"
# ext = "mkv"
# input_codec = "h264"
# output_codec = "mpeg2video"
# full_input_name = video_name + "_" + input_codec + "." + ext
# full_output_name = video_name + "_" + output_codec + "." + ext
# rel_input_path =  "resources" + sep + "input" + sep + full_input_name
# rel_output_path = "resources" + sep + "output" + sep + full_output_name


#command = ['ffmpeg', '-i', str(rel_input_path), '-c:v', 'h264_nvenc', '-rc', 'constqp', '-qp', '28', str(rel_output_path)]
#command = ['ffmpeg', '-i', str(rel_input_path), '-c:v', output_codec, str(rel_output_path)]

['ffmpeg' '-i' "resources/input/white_noise_h264.mkv" '-c:v h264' "resources/output/white_noise_h264.mkv"]
commandPair = {
    "cpu": ['ffmpeg', '-i', "resources/input/white_noise_h264.mkv", '-c:v', 'h264',       '-b', '74278k', "resources/output/white_noise_h264.mkv"],
    "gpu": ['ffmpeg', '-i', "resources/input/white_noise_h264.mkv", '-c:v', 'h264_nvenc', '-b', '74278k', "resources/output/white_noise_h264_nvenc.mkv"],
    "hwaccel": True,
    "hwaccel type":  "nvenc"
}

test(conn, "VIDEO_INFO", "RUN_INFO", commandPair)

conn.close()
print("Finished")
