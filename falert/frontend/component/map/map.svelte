<script>
    import { beforeUpdate, afterUpdate, createEventDispatcher, onMount, setContext } from 'svelte';
    import { browser } from '$app/env';

    import { key } from './map-context.js';

    export let latitude;
    export let longitude;
    export let zoom = 13;

    const dispatch = createEventDispatcher();

    let polygons = new Map();

    let map = null;
    let leaflet = null;

    const setPolygon = (symbol, polygon) => {
        polygons.set(symbol, {
            ...polygon,
            handle: null,
        });
    };

    const deletePolygon = (symbol) => {
        polygons.get(symbol).handle.removeFrom(map);
        polygons.delete(symbol);
    };

    const updatePolygon = () => {
        updatePolygons();
    };

    const onClick = (event) => {
        dispatch('click', {
            latitude: event.latlng.lat,
            longitude: event.latlng.lng,
        });
    };

    const onMove = (event) => {
        latitude = event.target.getCenter().lat;
        longitude = event.target.getCenter().lng;
    };

    const updatePolygons = () => {
        if (leaflet === null || map === null) {
            return;
        }

        polygons.forEach((polygon) => {
            if (polygon.handle !== null) {
                polygon.handle.removeFrom(map);
            }

            polygon.handle = leaflet.polygon(
                Array.from(polygon.vertices.values(), (vertex) => {
                    return [vertex.latitude, vertex.longitude];
                }),
                {
                    color: polygon.color,
                },
            );

            if (polygon.handle !== null) {
                polygon.handle.addTo(map);
            }
        });
    };

    setContext(key, {
        setPolygon,
        deletePolygon,
        updatePolygon,
    });

    onMount(async () => {
        if (browser) {
            if (leaflet === null) {
                leaflet = await import('leaflet');
            }

            if (map === null) {
                map = leaflet.map('map').setView([latitude, longitude], zoom);
            }

            leaflet
                .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution:
                        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                })
                .addTo(map);

            updatePolygons();

            map.on('click', onClick);
            map.on('move', onMove);
        }
    });

    beforeUpdate(() => {
        if (browser) {
            updatePolygons();
        }
    });

    afterUpdate(() => {
        if (browser) {
            updatePolygons();
        }
    });

    const updateCenter = (longitude, latitude) => {
        if (map === null) {
            return;
        }

        map.panTo({ lat: latitude, lon: longitude });
    };

    $: updateCenter(longitude, latitude);
</script>

<div id="map" />

<slot />

<style>
    @import 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';

    #map {
        height: 100%;
    }
</style>
