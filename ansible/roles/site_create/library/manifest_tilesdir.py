import os

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        www_imos_tiles_dir=dict(type='str', required=True),
        www_base_tiles_dir=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    # imos tiles
    imos_layers_tilesets = next(os.walk(p.www_imos_tiles_dir))[1]

    # base tiles
    base_layers = next(os.walk(p.www_base_tiles_dir))[1]
    base_layers_tilesets = {l: next(os.walk(os.path.join(p.www_base_tiles_dir, l)))[1] for l in base_layers}

    module.exit_json(changed=True, imos_tiles=imos_layers_tilesets, base_tiles=base_layers_tilesets)


def main():
    run_module()


if __name__ == '__main__':
    main()


