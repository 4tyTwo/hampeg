import subprocess
import importlib
import os
import dbOps
import hampegUtils
import time
from subprocess import Popen, STDOUT
import platform
from hampegUtils import sep


def deleteIfExists(filename):
    if os.path.isfile(filename):
        os.remove(filename)


def run(command):
    if platform.system() == "Windows":
        windowsRun(command)
    else
        unixRun(command)

def windowsRun(command):
    start = time.time()
    DEVNULL = open(os.devnull, 'wb', 0)
    subprocess.run(command, stderr=STDOUT)
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
    elapsed = time.time() - start
    DEVNULL.close()
    return {
        "REAL_T": elapsed,
        "USER_T": ru.ru_utime,
        "SYSTEM_T": ru.ru_stime
    }

sep = sep()
dir_path = os.path.dirname(os.path.realpath(__file__))
database_name = "acceleration.db"
table_name = "VIDEO_INFO"
conn = dbOps.setupDb(database_name, table_name)
video_name = "white_noise"
ext = "mkv"
input_codec = "h264"
output_codec = "mpeg2video"
full_input_name = video_name + "_" + input_codec + "." + ext
full_output_name = video_name + "_" + output_codec + "." + ext
rel_input_path =  "resources" + sep + "input" + sep + full_input_name
rel_output_path = "resources" + sep + "output" + sep + full_output_name
input_path = dir_path + rel_input_path
output_path = dir_path + rel_output_path

# command = ['ffmpeg', '-i', str(rel_output_path), '-c:v', 'h264_nvenc', '-rc', 'constqp', '-qp', '28', str(rel_input_path)]

srcInfo = hampegUtils.getInfo(rel_input_path)
# deleteIfExists(rel_input_path)
run(command)
# destInfo = hampegUtils.getInfo(rel_output_path)
if not(dbOps.recordExists(conn, table_name, srcInfo)):
    dbOps.insert(conn, table_name, srcInfo)
# dbOps.insert(conn, table_name, destInfo)
# id = dbOps.getLastId(conn, table_name)
# runInfo["SOURCE"] = id - 1
# runInfo["DEST"] = id
# dbOps.insert(conn, "RUN_INFO", runInfo)

conn.close()
