import os

def getHerePath():
    return os.path.dirname(os.path.realpath(__file__))

def pathJoin(path1, path2):
    return os.path.join(path1, path2)

def pathCombine(pathList):
    return os.path.join(*pathList) # 元组拆包