import glob
import os
import shutil
import subprocess

from ansible.module_utils.basic import AnsibleModule


def create_layer_dir(base_dir, name):
    path = os.path.join(base_dir, name)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def run_module():
    module_args = dict(
        mbtiles_dir=dict(type='str', required=True),
        disktiles_dir=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    mbtiles_files = glob.glob(os.path.join(p.mbtiles_dir, '*.mbtiles'))

    for mbtiles_file in mbtiles_files:

        layer_disktiles_dir = os.path.join(p.disktiles_dir, os.path.basename(mbtiles_file).split('.')[0])

        command = ["mb-util", "--image_format", "pbf", mbtiles_file, layer_disktiles_dir]
        subprocess.Popen(command)

    module.exit_json(changed=True)

def main():
    run_module()


if __name__ == '__main__':
    main()


