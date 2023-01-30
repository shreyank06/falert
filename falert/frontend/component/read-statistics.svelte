<script>
    import { onMount, createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let data = {
        fire_locations: [],
        subscriptions_count: null,
        matches_count: null,
        fire_locations_count: null,
    };

    onMount(() => {
        fetch('/statistics')
            .then((response) => response.json())
            .then((json) => {
                data = json;
            });
    });

    const formatNumber = (input) => {
        if (input >= 1000000) {
            return (input / 1000000).toFixed(1) + 'M';
        }

        if (input >= 1000) {
            return (input / 1000).toFixed(0) + 'K';
        }

        return input;
    };

    const formatDateTime = (dateTime) => {
        const date = new Date(dateTime);
        return date.toLocaleString();
    };

    const onFireLocationClick = (fire_location) => {
        dispatch('click', fire_location);
    };
</script>

<div class="prose flex flex-col">
    {#if data.subscriptions_count || data.matches_count || data.fire_locations_count}
        <h4>Statistics</h4>
        <div class="stats stats-vertical lg:stats-horizontal shadow mb-2">
            {#if data.subscriptions_count}
                <div class="stat">
                    <div class="stat-title">Subscriptions</div>
                    <div class="stat-value">{formatNumber(data.subscriptions_count)}</div>
                </div>
            {/if}

            {#if data.fire_locations_count}
                <div class="stat">
                    <div class="stat-title">Fire Locations</div>
                    <div class="stat-value">{formatNumber(data.fire_locations_count)}</div>
                </div>
            {/if}

            {#if data.matches_count}
                <div class="stat">
                    <div class="stat-title">Matches</div>
                    <div class="stat-value">{formatNumber(data.matches_count)}</div>
                </div>
            {/if}
        </div>
    {/if}

    {#if data.fire_locations.length > 0}
        <h4>Last Fire Locations</h4>
        <table class="table table-compact w-full mt-2">
            <thead>
                <tr>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Acquired</th>
                </tr>
            </thead>
            <tbody>
                {#each data.fire_locations as fire_location}
                    <tr on:click={() => onFireLocationClick(fire_location)} class="hover">
                        <td>{fire_location.latitude.toFixed(2)}</td>
                        <td>{fire_location.longitude.toFixed(2)}</td>
                        <td>{formatDateTime(fire_location.acquired)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {/if}
</div>
