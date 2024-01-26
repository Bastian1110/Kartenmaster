<script lang="ts">
    export let info = "Hola";
</script>

<div
    class="z-[-1] fixed left-0 top-0 grid h-full w-full grid-cols-12 bg-slate-900 bg-opacity-50 text-slate-100 text-2xl"
>
    <div
        class="grid grid-cols-3 grid-rows-3 w-screen h-screen text-slate-100"
        style="grid-template-columns: 40% 20% 40%;"
    >
        <div class="col-start-3 row-start-2 flex flex-row items-center ml-12 font-mono capitalize text-slate-400">{info}</div>
    </div>
</div>
