import re
import json
import subprocess
import timing_matrix

def process_metric(cmd, _type, position, value):
    tm = timing_matrix.timing_matrix()
    if _type == "ms":
        metric = "{} {{{}}} {}".format(cmd, tm.ms[str(position)], value)
        # print(metric)
    elif _type == "us":
        metric = "{} {{{}}} {}".format(cmd, tm.us[str(position)], value)
        # print(metric)
    elif _type == "500ms":
        metric = "{} {{{}}} {}".format(cmd, tm._500ms[str(position)], value)
        # print(metric)
    else:
        metric = "{} {{{}}} {}".format(cmd, "placeholder" value)
        print(metric)

def get_mctimings():
     proc = subprocess.Popen(['./mctimings',
                                '-h', '192.168.1.18:11210',
                                '-u', 'Administrator',
                                '-P', 'password',
                                '-b', 'travel-sample',
                                '-j'], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)

     stdout, stderr = proc.communicate()

     new_stdout = re.sub('\s+', " ", stdout)
     arr_stdout = new_stdout.split("} {")
     arr_mctimings = []
     for x in arr_stdout:
         new_str = x.strip()
         if new_str[0:1] != "{":
             new_str = "{" + new_str
         if new_str[-1:] != "}":
             new_str = new_str + "}"
         arr_mctimings.append(json.loads(new_str))
     for mctiming in arr_mctimings:
         for key in mctiming:
             if type(mctiming[key]) == type([]):
                 print(len(mctiming[key]))
                 for x, timing in enumerate(mctiming[key]):
                     process_metric(mctiming['command'], key, x, timing)
             else:
                 process_metric(mctiming['command'], key, 0, mctiming[key])
