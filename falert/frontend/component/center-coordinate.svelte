<script>
    export let latitude;
    export let longitude;
</script>

<div class="py-4 prose">
    <h4>Center Coordinate</h4>

    <input type="text" bind:value={latitude} placeholder="Latitude" class="input w-full mb-1" />

    <input
        type="text"
        bind:value={longitude}
        placeholder="Longitude"
        class="input w-full mt-1 mb-2"
    />
</div>
