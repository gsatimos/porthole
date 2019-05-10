import json
import os
import xml.etree.ElementTree as ElementTree
import requests
from ansible.module_utils.basic import AnsibleModule


def merge_layers(l1, l2):
    z = l1.copy()
    z.update(l2)
    return z


def get_filter_values(wms_endpoint, filter_name, layer):
    params = {
        "request": "uniqueValues",
        "service": "layerFilters",
        "version": "1.0.0",
        "layer": layer,
        "propertyName": filter_name,
        "outputFormat": "application/json"
    }

    r = requests.get(wms_endpoint, params=params)
    return [valueElement.text for valueElement in ElementTree.fromstring(r.content).findall('.//value')]


def geojson_analysis(geojson_file):

    with open(geojson_file, 'r') as _file:
        geojson = json.loads(_file.read())

    timestamp_params = {
        'earliest': 4000000000,  # bad hardcoded future date :( needs changing after 30/1/2098
        'latest': 0
    }

    for feature in geojson['features']:
        if 'timestamp' in feature['properties']:
            timestamp = feature['properties']['timestamp']

            if timestamp > 0:
                if timestamp > timestamp_params['latest']:
                    timestamp_params['latest'] = timestamp
                if timestamp < timestamp_params['earliest']:

                    timestamp_params['earliest'] = timestamp

    return {'timestamp_params': timestamp_params}


def run_module():
    module_args = dict(
        geojson_dir=dict(type='str', required=True),
        geoserver_endpoint=dict(type='str', required=True),
        layers=dict(type='list', required=True),
        collections=dict(type='list', required=True),
        base_tiles=dict(type='dict', required=True),
        imos_tiles=dict(type='list', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    web_config = {'layers': []}

    for layer in p.layers:

        wc_layer = dict(layer)

        # filter values
        for filter_option in wc_layer['ui']['filter_options']:
            if filter_option['type'] == 'select':
                filter_values = get_filter_values(p.geoserver_endpoint + "/wms", filter_option['name'], wc_layer['name'])
                filter_option['values'] = filter_values

        # geojson analysis
        wc_layer['analysis'] = geojson_analysis(
            os.path.join(p.geojson_dir, layer['name'].replace(':', '-') + '.geojson')
        )

        web_config['layers'].append(wc_layer)

    web_config['base_tiles'] = p.base_tiles
    web_config['collections'] = p.collections

    module.exit_json(changed=True, web_config=web_config)


def main():
    run_module()


if __name__ == '__main__':
    main()


