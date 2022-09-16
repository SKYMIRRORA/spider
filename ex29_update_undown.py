import os

from matplotlib.font_manager import json_dump, json_load
import json
import numpy as np

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)



if __name__ == "__main__":
    undown_bvs = json_load("jsons/undown_bvs.json")
    # down_tmp = json_load("jsons/downed_bvs_tmp.json")
    # all_bvs = json_load("jsons/all_bvs.json")
    # downed_bvs.extend(downed_bvs_tmp)
    path = "/media/huangrq/BIGDISK/reptile_faces2/images/9-10/"
    down_tmp = []
    for bv in os.listdir(path):
        if bv in undown_bvs:
            down_tmp.append(bv)

    new_undown_bvs = []
    for bv in undown_bvs:
        if bv not in down_tmp:
            new_undown_bvs.append(bv)

    with open("jsons/undown_bvs.json", "w") as df:
        json.dump(new_undown_bvs,df,indent = 2,cls=NumpyArrayEncoder)











