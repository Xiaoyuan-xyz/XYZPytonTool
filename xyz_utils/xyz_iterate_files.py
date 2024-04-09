import os


def file_suffix_criterion(types):
    if isinstance(types, str):
        types = [types]

    def suffix_criterion(file):
        return os.path.splitext(file)[1] in types

    return suffix_criterion


def iterate_files(folder_path, callback, criterion=None):
    if isinstance(criterion, str) or isinstance(criterion, list):
        criterion = file_suffix_criterion(criterion)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if criterion is None or criterion(file):
                file_path = os.path.join(root, file)
                callback(file_path)
