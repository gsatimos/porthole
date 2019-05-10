# wip - porthole

```
cd ansible
```

create tiles (imos layers and base layers)
```
ansible-playbook create_tiles_playbook.yaml -e @../config.yaml
```

create tiles (imos layers only)
```
ansible-playbook create_tiles_playbook.yaml -e @../config.yaml --skip-tags basetiles
```

create tiles without geoserver geojson download
Note that geojson files must have previously been downloaded 
```
ansible-playbook create_tiles_playbook.yaml -e @../config.yaml --skip-tags "download-geojson"
```

create site
```
ansible-playbook create_site_playbook.yaml -e @../config.yaml 
```

(work in progress)
