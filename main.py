import subprocess
import importlib
import os
import dbops
import ffmpegParser

#main 
dir_path = os.path.dirname(os.path.realpath(__file__))
database_name = dir_path + "\\" + "acceleration.db"
table_name = "video_info"
conn = dbops.setup_database(database_name, table_name)
video_path = dir_path + "\\resources\\noise\\white_noise.mkv"
res = ffmpegParser.getInfo(video_path)
c = conn.cursor()
vals = [(
    2, 
    res["name"],
    res["config"],
    res["duration"],
    res["bitrate"],
    res["codec"],
    res["codec profile"],
    res["color encoding"],
    res["width"],
    res["height"],
    res["SAR"],
    res["DAR"],
    res["FPS"]
)]
c.executemany('INSERT INTO video_info VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', vals)
conn.commit()

for row in c.execute('SELECT * FROM video_info'):
    print(row)

c.close()

conn.close()
