import numpy as np


def read_file(file_path):
    with open(file_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    # convert str to int
    return list(map(int, content))


def write_file(file_path, content):
    f = open(file_path, 'a')
    f.write(content)
    f.close()


if __name__ == '__main__':
    print('np.version.full_version : ' + np.version.full_version)
    nums = read_file('/var/nfs/read/number_to_add.txt')
    write_file('/var/nfs/write/number_added.txt', str(nums[0] + nums[1]))
    write_file('/var/nfs/write/number_added.txt', str(np.arange(6)))
