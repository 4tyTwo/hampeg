import subprocess
import importlib
import os
import dbops
import ffmpegParser
import time
from subprocess import Popen, STDOUT
import platform


def getLastId(dbcon, table_name):
    c = dbcon.cursor()
    c.execute("select max(ID) from " + table_name)
    i = int(c.fetchone()[0])
    c.close()
    return i

def sep():
    return "\\" if platform.system() == "Windows" else "/"

def runTime(rel_input_path, rel_output_path):
    if os.path.isfile(rel_output_path):
        os.remove(rel_output_path)
    start = time.time()
    DEVNULL = open(os.devnull, 'wb', 0)
    p = Popen(['ffmpeg', '-i', rel_input_path, "-c:v", "mpeg2video",rel_output_path], stdout=DEVNULL, stderr=STDOUT)
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
database_name = dir_path + sep + "acceleration.db"
table_name = "VIDEO_INFO"
conn = dbops.setup_database(database_name, table_name)
video_name = "white_noise"
ext = "mkv"
full_input_name = video_name + "." + ext
full_output_name = video_name + "_mpeg" + "." + ext
rel_input_path =  "resources" + sep + "noise" + sep + full_input_name
rel_output_path = "resources" + sep + "noise" + sep + full_output_name
input_path = dir_path + rel_input_path
output_path = dir_path + rel_output_path

command = ['ffmpeg', '-i', rel_input_path,"-c:v", "mpeg2video", rel_output_path],

srcInfo = ffmpegParser.getInfo(rel_input_path)
print("Run started")
runInfo = runTime(str(rel_input_path), str(rel_output_path))
print("Run finished, est time:", runInfo["REAL_T"])
destInfo = ffmpegParser.getInfo(rel_output_path)
dbops.insert_values(conn, table_name, srcInfo)
dbops.insert_values(conn, table_name, destInfo)
id = getLastId(conn, table_name)
runInfo["SOURCE"] = id - 1
runInfo["DEST"] = id
dbops.insert_values(conn, "RUN_INFO", runInfo)
conn.close()
