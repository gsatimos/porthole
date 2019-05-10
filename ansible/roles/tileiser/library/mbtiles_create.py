import glob
import os
import subprocess

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        geojson_dir=dict(type='str', required=True),
        mbtiles_dir=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    geojson_files = glob.glob(os.path.join(p.geojson_dir, '*.geojson'))

    for geojson_file in geojson_files:
        mb_path = os.path.join(p.mbtiles_dir, os.path.basename(geojson_file).split('.')[0] + '.mbtiles')

        command = [
            "tippecanoe",
            "-z6",
            "-r1",
            "-pk",
            "-pf",
            "-o",
            mb_path,
            "--drop-densest-as-needed",
            "--extend-zooms-if-still-dropping",
            geojson_file
        ]

        subprocess.Popen(command)

    module.exit_json(changed=True)

def main():
    run_module()


if __name__ == '__main__':
    main()


