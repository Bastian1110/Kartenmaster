<script lang="ts">
    export let rating = 0;
    const totalStars = 5;

    function setRating(newRating : any) {
        rating = newRating;
    }

    function handleKeydown(event : any, newRating : any) {
        if (event.key === 'Enter' || event.key === ' ') {
            setRating(newRating);
        }
    }
</script>

<style>
    .star {
        cursor: pointer;
        outline: none; 
    }
</style>

<div class="star-rating">
    {#each Array(totalStars) as _, i}
        <span
            class="star text-[4rem] -mx-2 text-violet-400"
            role="button"
            tabindex="0"
            aria-label={`Rate ${i + 1} stars`}
            on:click={() => setRating(i + 1)}
            on:keydown={(event) => handleKeydown(event, i + 1)}
        >
            {i < rating ? '★' : '☆'}
        </span>
    {/each}
</div>
