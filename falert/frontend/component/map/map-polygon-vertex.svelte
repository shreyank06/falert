<script>
    import { getContext, onDestroy, onMount } from 'svelte';

    import { key } from './map-polygon-context.js';

    const { setVertex, deleteVertex } = getContext(key);
    const symbol = Symbol();

    export let longitude;
    export let latitude;

    onMount(() => {
        setVertex(symbol, {
            longitude,
            latitude,
        });
    });

    onDestroy(() => {
        deleteVertex(symbol);
    });
</script>
