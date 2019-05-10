import json

from ansible.module_utils.basic import AnsibleModule



def run_module():
    module_args = dict(
        content=dict(type='dict', required=True),
        file=dict(type="str", required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    with open(p.file, 'w') as _file:
        _file.write(json.dumps(p.content, indent=4, sort_keys=True))

    module.exit_json(changed=True)


def main():
    run_module()


if __name__ == '__main__':
    main()


