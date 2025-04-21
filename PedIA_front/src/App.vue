<template>
  <div id="app">
    <div class="content">
      <main>
        <router-view/>
      </main>
    </div>

  </div>
</template>

<script>
import { provide, reactive, onBeforeMount, onMounted, computed } from 'vue';
import { useMainStore } from './stores/store.ts'; 
import ClickedClasses from './components/ClickedClasses.vue';

export default {
  name: 'App',
  components: {
    ClickedClasses
  },

  setup() {
    const store = useMainStore();
    const expandedClasses = reactive(new Set());
    provide('expandedClasses', expandedClasses);

    const currentDecision = computed(() => store.currentDecision);
    
    return { currentDecision };
  },
};
</script>

<style>
/* Add global styles here */
#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.content {
  display: flex;
  flex: 1;
  flex-direction: row;
}

.main-content {
  flex: 2;
  padding: 20px;
  overflow-y: auto;
}


button {
  display: block;
  margin: 10px 0;
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

button:hover {
  background-color: #0056b3;
}

</style>
