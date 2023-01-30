<script>
    import { createEventDispatcher } from 'svelte';

    export let vertices = [];
    let phoneNumber = null;

    const dispatch = createEventDispatcher();

    const onClickReset = () => {
        phoneNumber = null;
        dispatch('reset');
    };

    const onClickSubmit = () => {
        fetch('/subscriptions', {
            method: 'POST',
            body: JSON.stringify({
                vertices,
                phone_number: phoneNumber,
            }),
        }).then(() => {
            phoneNumber = null;
            dispatch('submit');
        });
    };
</script>

<div class="py-4 prose">
    <h4>Create Subscription</h4>

    <input
        type="text"
        bind:value={phoneNumber}
        placeholder="Phone Number"
        class="input w-full mb-2"
    />

    {#if vertices.length > 0}
        <table class="table table-compact w-full mt-2">
            <thead>
                <tr>
                    <th>Latitude</th>
                    <th>Longitude</th>
                </tr>
            </thead>
            <tbody>
                {#each vertices as vertex}
                    <tr>
                        <td>{vertex.latitude.toFixed(2)}</td>
                        <td>{vertex.longitude.toFixed(2)}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {/if}

    <div class="flex mt-2">
        <div class="btn btn-submit mr-2" on:click={onClickSubmit}>Submit</div>
        <div class="btn btn-ghost ml-2" on:click={onClickReset}>Reset</div>
    </div>
</div>
