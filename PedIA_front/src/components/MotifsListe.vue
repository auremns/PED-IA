<template>
  <div>
    <div id="app">
      <header>
        <nav>
          <router-link to="/list">Liste des motifs d'appel</router-link>
        </nav>
        <button @click="startEncounter">Commencer la régulation</button>
        <button @click="endEncounter">Fin de la régulation</button>
      </header>
      <div class="content">
        <main>
          <router-view/>
          <div class="motif-appel-container">
            <div class="search-bar">
              <input type="text" v-model="searchQuery" placeholder="Rechercher un motif d'appel" />
            </div>
            <div class="subclass-list">
              <div class="columns">
                <div class="column" v-for="(filteredSubclassList, index) in chunkedSubclasses" :key="index">
                  <ul>
                    <li v-for="subclass in filteredSubclassList" :key="subclass" class="subclass-item" @click="goToDetailPage(subclass)">
                      {{ subclass }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
      <footer>
        <p>© 2024 Ped IA</p>
      </footer>
    </div>
  </div>
</template>


<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useMainStore } from '@/stores/store'; 
const BACK_URL = "https://ped-ia-back-384d733bb8ae.herokuapp.com";

export default {
  name: 'MotifsListe',

  setup() {
    const subclasses = ref([]);
    const searchQuery = ref('');
    const router = useRouter();  
    const store = useMainStore();
    const filteredSubclasses = computed(() => {
      return subclasses.value.filter(subclass =>
        subclass.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    const chunkedSubclasses = computed(() => {
      const perColumn = Math.ceil(filteredSubclasses.value.length / 3);
      return new Array(3).fill().map((_, i) => {
        return filteredSubclasses.value.slice(i * perColumn, (i + 1) * perColumn);
      });
    });

    onMounted(async () => {
      try {
        const response = await axios.get(BACK_URL + '/get_motives');
        subclasses.value = response.data;
      } catch (error) {
        console.error('There was an issue fetching the subclasses:', error);
        subclasses.value = [];
      }
    });

    const startEncounter = () => {
      axios.get(BACK_URL + '/start_encounter')
        .then(response => {
          store.setEncounterId(response.data.encounter_id);
          console.log("Encounter started: " + response.data.encounter_id);
        })
        .catch(error => {
          console.error("Error starting encounter: ", error);
        });
    };

    const endEncounter = () => {
      const currentEncounterId = mainStore.getEncounterId();
      axios.post(BACK_URL + '/end_encounter', currentEncounterId)
        .then(response => {
          store.clearEncounterId();
          console.log("Encounter ended");
        })
        .catch(error => {
          console.error("Error ending encounter: ", error);
        });
    };

    const goToDetailPage = (subclass) => {
      router.push({ name: 'motivesDetail', params: { motifs: subclass } });
    };

    return {
      startEncounter,
      endEncounter,
      searchQuery,
      chunkedSubclasses,
      goToDetailPage
    };
  }
};
</script>

<style scoped>

header {
  background: #edf7ec; 
  padding: 10px 20px; 
  display: flex;
  align-items:baseline;
  display: flex;
  flex-direction: column;
}

nav a {
  margin-right: 10px;
  margin-bottom: 30px;
  text-decoration:overline;
  color: #475a42;
  white-space: nowrap;
}

.motif-appel-container {
  padding: 30px;
  height: 100%;
  width: 100%; /* Ensure it takes all available height */
  box-sizing: border-box;
}

.search-bar input {
  width: 100%;
  width: 100%;
  padding: 10px;
  margin-bottom: 20px;
  box-sizing: border-box;
}

.columns {
  display: flex;
  height: 100%;
  width: 100%; /* Ensure it takes all available height */
}

.column {
  flex: 1;
  padding: 0 20px;
}

.subclass-list ul {
  list-style-type: none;
  padding: 0;
  height: 100%;
  width: 100%; /* Ensure it takes all available height */
  box-sizing: border-box;
}

.subclass-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f4f4f4;
  border-radius: 6px;
  cursor: pointer;
  display: inline-block;
  white-space: nowrap; /* Prevents text from wrapping to the next line */
  overflow: hidden; /* Prevents content from spilling out of the box */
  text-overflow: ellipsis;
  margin-right: 15px;
}

button {
  background-color: #9ac597; 
  color: white;
  padding: 8px 16px;
  font-size: 10px;
  border: none;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  margin-right: 10px;
  margin-top: 10px;
}
button:last-child {
  margin-right: 0; 
}

button:hover {
  background-color: #0056b3;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}
</style>