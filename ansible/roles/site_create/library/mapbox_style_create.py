import json
import glob
import os


from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        imos_tiles=dict(type='list', required=True),
        base_tiles=dict(type='dict', required=True),
        site=dict(type='dict', required=True),
        mapbox=dict(type='dict', required=True),
        layers=dict(type='list', required=True),
        www_base_tiles_dir=dict(type="str", required=True),
        www_imos_tiles_dir=dict(type="str", required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    p = type('Params', (), module.params)

    config_mb_style = p.mapbox['style']

    base_url = p.site['host']['dev'] if p.site['dev_mode'] else p.site['host']['prod']
    base_tiles_url = base_url + '/' + p.www_base_tiles_dir.split('www/')[1]
    imos_tiles_url = base_url + '/' + p.www_imos_tiles_dir.split('www/')[1]

    layer_index = {layer['name'].replace(':', '-'): layer for layer in p.layers}

    mapbox_style = {
        'version': config_mb_style['version'],
        'name': config_mb_style['name'],
        'centre': [config_mb_style['center']['lon'],config_mb_style['center']['lon']],
        'zoom': config_mb_style['zoom'],
        'sources': {},
        'layers': []
    }

    # create raster sources:
    for raster_source in p.base_tiles['raster']:
        mapbox_style['sources'][raster_source] = {
                "tiles": [base_tiles_url + '/raster/' + raster_source + '/{z}/{x}/{y}.png'],
                "type": "raster",
                "tileSize": config_mb_style['sources']['raster']['tilesize']
        }

    # create vector base sources:
    for vector_source in p.base_tiles['vector']:
        mapbox_style['sources'][vector_source] = {
            "tiles": [base_tiles_url + '/vector/' + vector_source + '/{z}/{x}/{y}' + '' if p.site['dev_mode'] else '.pbf'],
            "type": "vector"
        }

    # create vector imos sources and layers:
    for layer in p.imos_tiles:

        # mapbox style
        mapbox_style['sources'][layer] = {
            "tiles": [imos_tiles_url + '/' + layer + '/{z}/{x}/{y}' + '' if p.site['dev_mode'] else '.pbf'],
            "type": "vector"
        }

        # clustering for style
        if 'source' in layer_index[layer]['mapbox'] and 'clustering' in layer_index[layer]['mapbox']['source']:
            mapbox_style['sources'][layer]['cluster'] = True
            mapbox_style['sources'][layer]['clusterRadius'] = layer_index[layer]['mapbox']['source']['clustering']['cluster_radius']

        # mapbox layer
        mapbox_style['layers'].append({
            "id": layer.replace(':', '-'),
            "type": "circle",
            "source": layer.replace(':', '-'),
            "source-layer": layer.replace('-', ''),
            "paint": layer_index[layer]['mapbox']['layer']['paint'],
            "layout": {"visibility": "none"}
        })

    # create layers (base)
    for style_layer in config_mb_style['layers']:
        mapbox_style['layers'].append(style_layer)

    module.exit_json(changed=True, mapbox_style=mapbox_style)


def main():
    run_module()


if __name__ == '__main__':
    main()
