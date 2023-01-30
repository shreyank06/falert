<script>
    import { getContext, setContext, onDestroy, onMount } from 'svelte';

    import { key as mapKey } from './map-context.js';
    import { key as mapPolygonKey } from './map-polygon-context.js';

    export let color = 'blue';

    const symbol = Symbol();
    const vertices = new Map();
    const { setPolygon, deletePolygon, updatePolygon } = getContext(mapKey);

    const setVertex = (symbol, vertex) => {
        vertices.set(symbol, vertex);
        updatePolygon(symbol);
    };

    const deleteVertex = (symbol) => {
        vertices.delete(symbol);
        updatePolygon(symbol);
    };

    setContext(mapPolygonKey, {
        setVertex,
        deleteVertex,
    });

    onMount(() => {
        setPolygon(symbol, { vertices, color });
    });

    onDestroy(() => {
        deletePolygon(symbol);
    });
</script>

<slot />
