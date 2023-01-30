<script>
    import Map from '../component/map/map.svelte';
    import MapPolygon from '../component/map/map-polygon.svelte';
    import MapPolygonVertex from '../component/map/map-polygon-vertex.svelte';
    import CreateSubscription from '../component/create-subscription.svelte';
    import ReadStatistics from '../component/read-statistics.svelte';
    import CenterCoordinate from '../component/center-coordinate.svelte';

    let latitude = 52.520008;
    let longitude = 13.404954;
    let vertices = [];

    const onClickMap = (event) => {
        vertices.push({
            latitude: event.detail.latitude,
            longitude: event.detail.longitude,
        });

        vertices = vertices;
    };

    const onCreateSubscriptionSubmit = () => {
        vertices = [];
    };

    const onCreateSubscriptionReset = () => {
        vertices = [];
    };

    const onReadStatisticsClick = (event) => {
        longitude = event.detail.longitude;
        latitude = event.detail.latitude;
    };
</script>

<div class="h-full w-full flex">
    <div class="basis-1/5 p-4 h-full overflow-y-scroll">
        <div class="h-full flex flex-col justify-between">
            <div>
                <div class="flex-none px-2 mx-2 pb-4">
                    <span class="text-lg font-bold">falert</span>
                </div>

                <hr />

                <CreateSubscription
                    {vertices}
                    on:reset={onCreateSubscriptionReset}
                    on:submit={onCreateSubscriptionSubmit}
                />

                <hr />

                <CenterCoordinate bind:longitude bind:latitude />
            </div>
            <div>
                <hr />
                <ReadStatistics on:click={onReadStatisticsClick} />
                <hr />
                <div class="flex justify-between">
                    <div>Made with ❤️</div>
                    <div>
                        <a href="https://github.com/Stazer/falert">GitHub</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="h-full basis-4/5">
        <Map bind:latitude bind:longitude on:click={onClickMap}>
            {#if vertices.length > 0}
                <MapPolygon color="cyan">
                    {#each vertices as vertex}
                        <MapPolygonVertex longitude={vertex.longitude} latitude={vertex.latitude} />
                    {/each}
                </MapPolygon>
            {/if}
        </Map>
    </div>
</div>
