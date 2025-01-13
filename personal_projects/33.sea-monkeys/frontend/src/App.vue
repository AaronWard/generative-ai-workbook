<template>
  <div id="app">
    <FishBowl ref="fishbowl" />
  </div>
</template>

<script>
import FishBowl from './components/FishBowl.vue';

export default {
  name: 'App',
  components: {
    FishBowl,

  },
};
</script>

<style>
#app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>