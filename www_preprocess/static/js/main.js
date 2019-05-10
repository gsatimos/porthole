

mapboxgl.accessToken = 'pk.eyJ1IjoiZ3NhdDM4IiwiYSI6ImNqZWdqdTg4ZDF2ZW8yeG1rNnNtaGYxZDUifQ.i42n4bVGXhBfc-V5KRJHuA';
var map = new mapboxgl.Map({
    container: 'map',
    style: './style.json'
});
map.setMinZoom(3);
map.setCenter([147, -35]);

var site_config = null;
var state = {collections: [], mapboxLayers: [], filters: {}};

$.getJSON( "./config.json", function(data) {
        site_config = data;
        startApp();
});

var depthValueMap = {
    'greater than': '>',
    'greater than or equal to': '>=',
    'equal to': '==',
    'not equal to': '!=',
    'less than': '<',
    'less than or equal to': '<=',
    'between (inclusive)': ''
}

function setCollectionInState(collectionTitle) {
    // add layer to collection
    var collection = collectionIndex()[collectionTitle];
    collection.layer = layerIndex()[collection.layer];
    state.collections.push(collection);
    state.filters[collectionTitle] = {};
}

function isCollectionSetInState(collectionTitle) {
    var collectionsInState = [];
    state.collections.forEach(function(collection) {
        if (collectionTitle === collection.title) {
            collectionsInState.push(collection);
        }
    });
    return collectionsInState.length > 0;
}

function layerIndex() {
    li = {};
    site_config.layers.forEach(function(layer) {
        li[layer['name']] = layer;
    });
    return li
}

function collectionIndex() {
    ci = {};
    site_config.collections.forEach(function(collection) {
        ci[collection['title']] = collection;
    });
    return ci;
}

function startApp() {
    setCollectionsModal();
}

// collections 

function setCollectionsModal() {
    $('#collections-body').empty();

    site_config.collections.forEach(function(collection) {
        $('<div>').attr('id', 'collections-body-items').appendTo('#collections-body');
        $('<h5>').text(collection.title).appendTo('#collections-body-items');
        $('<p>').text(collection.organisation).appendTo('#collections-body-items');
        if (!isCollectionSetInState(collection.title)) {
            $('<button>')
                .text('add to map')
                .attr('class', 'btn btn-secondary popover-test')
                .attr('title', collection.title)
                .on('click', function () {
                    uICollectionSelected(this.title)
                })
                .appendTo('#collections-body-items');
        }
        else {
            $('<button>')
                .text('added')
                .attr('class', 'btn btn-secondary popover-test')
                .attr('disabled', 'true')
                .appendTo('#collections-body-items');
        }
        $('<hr>').appendTo('#collections-body-items');
    });
}

function uICollectionSelected(collectionTitle) {
    $('.collectionsModal').modal('hide');
    setCollectionInState(collectionTitle);

    emptyAllFilters();

    state.collections.forEach(function(collection) {
        setFilterOptions(collection);
        setLayerFilterOptionValues(collection);
        setLayerOnMap(collection);
    });

    // re-init collections modal
    setCollectionsModal();
}

// end collections


function minMaxCollectionDates() {
    earliest = 4000000000;
    latest = 0;

    state.collections.forEach(function(collection) {
        if (collection.layer.analysis.timestamp_params.earliest < earliest) {
            earliest = collection.layer.analysis.timestamp_params.earliest
        }
        if (collection.layer.analysis.timestamp_params.latest > latest) {
            latest = collection.layer.analysis.timestamp_params.latest
        }
    });

    return {earliest: earliest, latest: latest}
}

function addDateTimeFields() {

    var minMax = minMaxCollectionDates();

    var picker_from_str = '<div class="input-group date" id="date-picker-from">' +
            '<input type="text" class="form-control" />' +
            '<span class="input-group-addon">' +
            '        from' +
            '</span>' +
            '</div>' +
            '</div>';
    var picker_to_str = '<div class="input-group date" id="date-picker-to">' +
            '<input type="text" class="form-control" />' +
            '<span class="input-group-addon">' +
            '        to' +
            '</span>' +
            '</div>' +
            '</div>'

    $('<label>').text('Temporal').appendTo('#global-date-pickers');
    $('#global-date-pickers').append(picker_from_str);
    //$("#date-picker-from").datepicker();
    $('#global-date-pickers').append(picker_to_str);
    //$("#date-picker-to").datepicker();

    var minDate = new Date(minMax.earliest*1000).toString();

    $("#date-picker-from").datepicker({startDate: new Date(minMax.earliest*1000).toString()}).on('changeDate', uIFilterChanged);
    $("#date-picker-to").datepicker({endDate: new Date(minMax.earliest*1000).toString()}).on('changeDate', uIFilterChanged);
}

function dateTimeFieldIsAdded() {
    return !$('#global-date-pickers').is(':empty')
}

function setLayerFilterOptionValues(collection) {

    var filter_options = collection.layer.ui.filter_options;

    filter_options.forEach(function(opt) {
        if (opt.type == 'select' || opt.type == 'comparison_input') {
            opt.values.forEach(function (val) {
                $('<option>').attr('value', val).text(val).appendTo('#' + opt.name + '-selection');
            })
        }
    });
}

function emptyAllFilters() {
    $( "#collection-filter-selector").empty();
    $( "#global-date-pickers").empty();
}


function setFilterOptions(collection) {
    var opts = collection.layer.ui.filter_options;

    // new div for single collection
    var collection_div_id = collection.layer.name + '-collection';
    var collection_div = $('<div>').attr('id', collection_div_id)
        .attr('class', 'collection-panel')
        .appendTo('#collection-filter-selector');

    //title
    $('<h5>').attr('id', '#collection-title').text(collection.title).appendTo(collection_div);

    opts.forEach(function(opt) {

        if (opt.type == 'select') {
            $('<label>').attr('for', opt.name + '-selection').text(opt.display).appendTo(collection_div);
            var sel = $('<select>').attr('id', opt.name + '-selection')
                .attr('name', opt.name)
                .attr('class', 'form-control')
                .appendTo(collection_div)
                .on('change', function() {uIFilterChanged()});
            state.filters[collection.title][opt.name] = sel;
            $('<option>').val(opt.default).text(opt.default).appendTo('#' + opt.name + '-selection');
        }
        else if(opt.type == 'comparison_input') {
            $('<label>').attr('for', opt.name + '-selection').text(opt.display).appendTo(collection_div);
            var sel = $('<select>').attr('id', opt.name + '-selection')
                .attr('name', opt.name)
                .attr('class', 'form-control')
                .appendTo(collection_div)
                .on('change', function() {uIFilterChanged()});
            var input = $('<input>').attr('id', opt.name + '-input')
                .attr('name', opt.name)
                .attr('class', 'form-control')
                .appendTo(collection_div)
                .on('change', function() {uIFilterChanged()});
            state.filters[collection.title][opt.name + 'select'] = sel;
            state.filters[collection.title][opt.name + 'input'] = input;
        }
        else if (opt.type == 'date_range') {
            if (!dateTimeFieldIsAdded()) {
                addDateTimeFields();
            }
        }
    });
}

function timestampsFromDateFields() {

    var timestamps = {from: '', to: ''};

    if (!$('#global-date-pickers').is(':empty')) {
        var from_date = $("#date-picker-from").datepicker("getDate");
        var to_date = $("#date-picker-to").datepicker("getDate");

        if (from_date !== null && to_date !== null) {
            timestamps.from = from_date.getTime() / 1000;
            timestamps.to = to_date.getTime() / 1000;
        }
        else {
            return null;
        }
    }
    else {
        return null;
    }
    return timestamps;
}


function getValuesFromTrackedFilters(collectionTitle) {

    var collectionFitlers = state.filters[collectionTitle];

    var filterValues = {};

    Object.keys(collectionFitlers).forEach(function(key) {
        var val = collectionFitlers[key].val();
        filterValues[key] = val;
    });

    //adjust for depth selector
    if (typeof(filterValues.depthinput) !== 'undefined' && typeof(filterValues.depthselect) !== 'undefined') {
        filterValues.depth = [filterValues.depthselect, filterValues.depthinput]
        delete filterValues.depthselect;
        delete filterValues.depthinput;
    }

    var timestamps = timestampsFromDateFields();

    if (timestamps !== null) {
        filterValues['timestamps'] = timestamps;
    }
    // add any date to/from
    return filterValues;
}


function uIFilterChanged() {
    state.collections.forEach(function(collection) {
        setLayerOnMap(collection);
    });
}


function setFilterOnMap(mapboxLayerName, prop, value) {
    console.log(typeof value);
    if (typeof value === 'string') {
        map.setFilter(mapboxLayerName, ['==', prop, value]);
    }
    else if (typeof value === 'array') { // array - depth
        var filterObj = [depthValueMap[value[0]], 'DEPTH_bin', parseFloat(value[1])];
        map.setFilter(mapboxLayerName, filterObj);
    }
    else if (typeof value === 'object') {
        var filterObjFrom = ['>=', 'timestamp', value['from']];
        var filterObjTo = ['<=', 'timestamp',   value['to']];
        map.setFilter(mapboxLayerName, filterObjFrom, filterObjTo);
    }
}


function setLayerOnMap(collection) {

    var mapboxLayerName = collection.layer.name.replace(':', '-');

    if (state.mapboxLayers.indexOf(mapboxLayerName) == -1) {
        map.setLayoutProperty(mapboxLayerName, 'visibility', 'visible'); //old layer
        map.setFilter(mapboxLayerName, undefined);
        map.moveLayer(mapboxLayerName); // top z-position

        state.mapboxLayers.push(mapboxLayerName);
    }

    //iterate over collections in state
    var filterValues = getValuesFromTrackedFilters(collection.title);

    Object.keys(filterValues).forEach(function(key) {
        if (filterValues[key] !== 'all' && filterValues[key] !== 'none') {

            // case for depth filter
            if (!((key === 'depth' && filterValues[key][0] === 'none') || (key === 'depth' && filterValues[key][1] === ""))) {
                setFilterOnMap(mapboxLayerName, key, filterValues[key]);
            }
        }
    });
}
