
import os
import json

import arrow
import requests
from ansible.module_utils.basic import AnsibleModule


def get_features(ows_endpoint, layer, max_features):
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": layer,
        "outputFormat": "application/json",
    }

    # if max_features is a number then set it. otherwise don't set
    try:
        val = int(max_features)
        params['maxFeatures'] = max_features
    except ValueError:
        pass

    return requests.get(ows_endpoint, params=params).json()


def add_feature_timestamps(features, date_field):
    updated_features = []

    for feature in features:
        update_feature = dict(feature)
        update_feature['properties']['timestamp'] = arrow.get(feature['properties'][date_field]).timestamp
        updated_features.append(update_feature)
    return updated_features


def run_module():
    module_args = dict(
        geoserver_endpoint=dict(type='str', required=True),
        geojson_dir=dict(type='str', required=True),
        layers=dict(type='list', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    for layer in p.layers:

        feature_collection = get_features(
            p.geoserver_endpoint + "/ows",
            layer['name'],
            layer['tile_processing']['max_features']
        )

        geojson_path = os.path.join(p.geojson_dir, layer['name'].replace(':', '-') + '.geojson')

        with open(geojson_path, 'w') as _file:
            _file.write(json.dumps({
                "type": "FeatureCollection",
                "features": add_feature_timestamps(feature_collection['features'], layer['tile_processing']['date_field'] )}, indent=2)
            )

    module.exit_json(changed=True)


def main():
    run_module()


if __name__ == '__main__':
    main()


