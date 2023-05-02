import json
from pathlib import Path, PurePath
from nextcloud import NextCloud


nextcl = None
temp_dir = Path('./temp/')
if not temp_dir.is_dir():
    temp_dir.mkdir(parents=True)


def login():
    """
    Login into nextcloud
    """
    global nextcl
    if nextcl is None:
        with open(PurePath('./credentials.json'), 'r') as fileobj:
            credentials = json.load(fileobj)['nextcloud']
        nextcl = NextCloud(endpoint=credentials['url'], user=credentials['user'], password=credentials['password'])


def upload_file(path_to_file, target_path, del_file=False):
    """
    This function shall upload a file to nextcloud
    """
    login()
    if PurePath(target_path).suffix == '':
        filename = PurePath(path_to_file).name
        target_path = PurePath(target_path).joinpath(filename)

    path = Path(path_to_file)
    if path.is_file():
        nextcl.upload_file(str(path_to_file), str(target_path))

        if del_file:
            path.unlink()
    else:
        print('file doesnt exist.')


def upload_content(path_to_file, content):
    name = PurePath(path_to_file).name
    temp_file = PurePath(temp_dir).joinpath(name)

    if PurePath(path_to_file).suffix == '.json':
        with open(temp_file, 'w') as fileobj:
            json.dump(content, fileobj, indent=4)
    else:
        msg = "[nxc.upload_content] The extension '{ext}' can not be handled."
        raise FileNotFoundError(msg.format(ext=path_to_file.suffix))

    upload_file(temp_file, path_to_file, del_file=True)


def get_file(path_to_file):
    """
    This function shall get a file from the nextcloud
    """
    login()
    path_to_file = PurePath(path_to_file)
    name = path_to_file.name
    target = temp_dir.joinpath(name)
    nextcl.download_file(str(path_to_file), str(target))

    if Path(target).is_file:
        if path_to_file.suffix == '.json':
            with open(target, 'r') as fileobj:
                content = json.load(fileobj)
            Path(target).unlink()
        else:
            msg = "[nxc.get_file] The extension '{ext}' can not be handled."
            raise FileNotFoundError(msg.format(ext=path_to_file.suffix))

    else:
        msg = "[nxc.get_file] File at '{path}' in Nextcloud not found."
        raise FileNotFoundError(msg.format(path=path_to_file))

    return content


def make_dir(dir):
    """
    """
    login()
    nextcl.assure_tree_exists(str(dir))


def test():
    # make_dir('report/submissions/class/F2022')
    nxc_path_add_courses = 'courses/add/add_courses.json'
    content = get_file(nxc_path_add_courses)
    print(content)


if __name__ == '__main__':
    test()
