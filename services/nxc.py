import json
from pathlib import Path, PurePath
from nextcloud import NextCloud


nxc = None
temp_dir = Path('./temp/')
if not temp_dir.is_dir():
    temp_dir.mkdir(parents=True)


def login():
    """
    Login into nextcloud
    """
    global nxc
    if nxc is None:
        with open(PurePath('./credentials.json'), 'r') as fileobj:
            credentials = json.load(fileobj)['nextcloud']
        nxc = NextCloud(endpoint=credentials['url'], user=credentials['user'], password=credentials['password'])


def upload_file(path_to_file, target_path, del_file=False):
    """
    This function shall upload a file to next cloud
    """
    login()
    if PurePath(target_path).suffix == '':
        filename = PurePath(path_to_file).name
        target_path = PurePath(target_path).joinpath(filename)

    path = Path(path_to_file)
    if path.is_file():
        nxc.upload_file(str(path_to_file), str(target_path))

        if del_file:
            path.unlink()
    else:
        print('file doesnt exist.')


def make_dir(dir):
    """
    """
    login()
    nxc.assure_tree_exists(str(dir))


def test():
    # make_dir('report/submissions/class/F2022')
    upload_file('./temp/readme.md', 'report/submissions/class/F2022/Class_Ancient_Runes_September_2022/readme.md')


if __name__ == '__main__':
    test()
