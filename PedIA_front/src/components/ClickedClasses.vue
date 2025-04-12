<template>
  <div class="clicked-classes-container">
    <h3>A l'interrogatoire, on retrouve :</h3>
    <ul>
      <li v-for="className in mainStore.clickedClasses" :key="className">
        {{ className }} 
        <button @click="removeClass(className)">Retirer</button>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue';
import { useMainStore } from '@/stores/store';

export default defineComponent({
  name: 'ClickedClasses',
  setup() {
    const mainStore = useMainStore();

    const removeClass = async (className: string) => {
      await mainStore.removeClickedClass(className);
    };

    onMounted(() => {
      mainStore.fetchClickedClasses();
    });

    return {
      mainStore,
      removeClass
    };
  }
});
</script>

<style scoped>
.clicked-classes-container {
  flex: 1;
  padding: 20px;
  background-color: white;
  color: black;
  border: 4px solid grey;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  box-sizing: border-box;
  overflow-y: auto;
  margin: 10px;
}

.clicked-classes-container h3 {
  font-weight: bold;
}

button {
  padding: 5px 10px;
  margin-right: 5px;
  background-color: #f49999;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 5px;
}

button:hover {
  background-color: #e8e8e8;
}
</style>
