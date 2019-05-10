#!/bin/bash

# usage example: ./base_tile_processing.sh ../resources ../www/tiles/base/

set -e

resources_dir=$1
tiles_dest=$2
tmp_working_dir=/tmp/porthole_temp_work
tmp_tile_export_dir=$tmp_working_dir/tile_export

echo $tmp_working_dir
echo $tmp_expo

echo "setting up"
rm -rf $tmp_working_dir
mkdir -p $tmp_working_dir
mkdir -p $tmp_tile_export_dir

echo ""
echo "converting shape files to json"
ogr2ogr -f GeoJSON $tmp_working_dir/cstauscd_r.geojson -t_srs EPSG:4326 -s_srs EPSG:4326 $resources_dir/cstauscd_r.shp
ogr2ogr -f GeoJSON $tmp_working_dir/continent.geojson -t_srs EPSG:4326 -s_srs EPSG:4326 $resources_dir/continent.shp


echo ""
echo "adding georeferencing data to tifs"
gdal_translate -a_nodata 0 -of GTiff -a_srs EPSG:4326 -a_ullr -180.00 90.00 180.00 -90.00 $resources_dir/worldmap_large_default.tif $tmp_working_dir/worldmap_large_default.tif
gdal_translate -a_nodata 0 -of GTiff -a_srs EPSG:4326 -a_ullr 102.00 -8.00 172.00 -52.00 $resources_dir/bathcl500md_coloured.tif $tmp_working_dir/bathcl500md_coloured.tif

echo ""
echo "generating mbtiles from tifs"
gdal_translate -of mbtiles $tmp_working_dir/bathcl500md_coloured.tif $tmp_working_dir/bathcl500md_coloured.mbtiles
gdal_translate -of mbtiles $tmp_working_dir/worldmap_large_default.tif $tmp_working_dir/worldmap_large_default.mbtiles

echo ""
echo "generating mbtiles from geojson"
tippecanoe -o $tmp_working_dir/cstauscd_r.mbtiles -Z 0 -z 6 $tmp_working_dir/cstauscd_r.geojson
tippecanoe -o $tmp_working_dir/continent.mbtiles -Z 0 -z 6 $tmp_working_dir/continent.geojson

echo ""
echo "exporting mbtiles to disk"
mb-util --image_format png $tmp_working_dir/bathcl500md_coloured.mbtiles $tmp_tile_export_dir/bathcl500md_coloured
mb-util --image_format png $tmp_working_dir/worldmap_large_default.mbtiles $tmp_tile_export_dir/worldmap_large_default
mb-util --image_format pbf $tmp_working_dir/cstauscd_r.mbtiles $tmp_tile_export_dir/cstauscd_r
mb-util --image_format pbf $tmp_working_dir/continent.mbtiles $tmp_tile_export_dir/continent

echo ""
echo "moving tiles to $tiles_dest"
rm -rf $tiles_dest
mkdir -p $tiles_dest/raster
mkdir -p $tiles_dest/vector
cp  -R $tmp_tile_export_dir/bathcl500md_coloured $tiles_dest/raster
cp  -R $tmp_tile_export_dir/worldmap_large_default $tiles_dest/raster
cp  -R $tmp_tile_export_dir/cstauscd_r $tiles_dest/vector
cp  -R $tmp_tile_export_dir/continent $tiles_dest/vector
