<template>
  <div class="details-container">
    <div class="left-side">
      <div class="upper-part">
        <header>
      <nav>
        <router-link to="/list">Liste des motifs d'appel</router-link>
      </nav>
      <button @click="startEncounter">Commencer la régulation</button>
      <button @click="endEncounter">Fin de la régulation</button>
    </header>
    <h2>
      <span class="static-text">Vous êtes dans le motif d'appel:</span>
      <span class="dynamic-text">{{ classDetails.name }}</span>
    </h2>

        <div class="subclasses">
          <h3>Sous-catégories:</h3>
          <ul>
            <class-detail
              v-for="subclass in classDetails.subclasses"
              :key="subclass.name"
              :class-detail="subclass"
              :expanded-classes="expandedClasses"
              @updateDecision="handleUpdateDecision"
            />
          </ul>
        </div>
      </div>
      <div class="lower-part">
        <div class="related-classes">
          <h3>Il faut rechercher:</h3>
          <ul>
            <class-detail
              v-for="related in classDetails.relatedClasses"
              :key="related.name"
              :class-detail="related"
              :expanded-classes="expandedClasses"
              @updateDecision="handleUpdateDecision"
            />
          </ul>
        </div>
        <div class="context-classes">
          <h3>Ces éléments peuvent mener à une décision:</h3>
          <ul>
            <class-detail
              v-for="context in classDetails.contextClasses"
              :key="context.name"
              :class-detail="context"
              :expanded-classes="expandedClasses"
              @updateDecision="handleUpdateDecision"
            />
          </ul>
        </div>
      </div>
    </div>
    <div class="right-side">
      <div v-if="currentDecision" class="decision-box">
        Décision: {{ currentDecision }}
        <br>
        {{ currentDecisionExplanation }}
      </div>
      <ClickedClasses />
    </div>
  </div>
</template>


<script>
import { ref, onMounted, inject, computed } from 'vue';
import axios from 'axios';
import ClassDetail from './ClassDetail.vue';
import { useMainStore } from '@/stores/store'; 
import ClickedClasses from './ClickedClasses.vue';
const BACK_URL = "https://ped-ia-back-384d733bb8ae.herokuapp.com";

export default {
  name: 'App',
  components: {
    ClassDetail,
    ClickedClasses
  },

  props: ['motifs'],
  
  setup(props) {
    const mainStore = useMainStore();
    const expandedClasses = inject('expandedClasses');
    const classDetails = ref({
      name: props.motifs,
      subclasses: [],
      relatedClasses: [],
      contextClasses: [],
      isExpanded: true
    });

    const currentDecision = computed(() => mainStore.currentDecision);

    const decisionExplanations = {
      R1: "Envoyer un SMUR",
      R2A: "Envoyer un VSAV",
      R2B: "SAU par propres moyens ou ambulances",
      R3: "Consultation médicale en ville",
      R4: "Conseils téléphoniques"
    };

    const currentDecisionExplanation = computed(() => {
      return decisionExplanations[mainStore.currentDecision] || "";
    });



    // Fetch initial details
    onMounted(() => {
      fetchInitialDetails();
    });
    const startEncounter = () => {
      axios.get(BACK_URL + '/start_encounter')
        .then(response => {
          mainStore.setEncounterId(response.data.encounter_id);
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
          mainStore.clearEncounterId();
          console.log("Encounter ended");
        })
        .catch(error => {
          console.error("Error ending encounter: ", error);
        });
    };

    function fetchInitialDetails() {
      const currentEncounterId = mainStore.getEncounterId();
      axios.post(BACK_URL + `/get_subclasses?class_name=${classDetails.value.name}`, currentEncounterId)
        .then(response => {
          classDetails.value.subclasses = response.data.map(item => ({
            name: item.name, 
            subclasses: [],
            relatedClasses: [],
            contextClasses: [],
            isExpanded: false 
          }));
        })
        .catch(error => {
          console.error('Error fetching subclasses:', error);
        });

      axios.post(BACK_URL + `/get_classes_after_faitRechercher?class_name=${classDetails.value.name}`, currentEncounterId)
        .then(response => {
          classDetails.value.relatedClasses = response.data.map(item => ({
            name: item.name,
            subclasses: [],
            relatedClasses: [],
            contextClasses: [],
            isExpanded: false
          }));
        })
        .catch(error => {
          console.error('Error fetching related classes:', error);
        });

        axios.post(BACK_URL + `/get_classes_after_aPourContexte?class_name=${classDetails.value.name}`, currentEncounterId)
        .then(response => {
          console.log("Response data:", response.data);
          classDetails.value.contextClasses = response.data.map(item => ({
              name: item.name,
              relation: item.relation,
              subclasses: [],
              relatedClasses: [],
              contextClasses: [],
              isExpanded: false
            }));
          
        })
        .catch(error => {
          console.error('Error fetching context classes:', error);
        });

    }


    async function handleUpdateDecision(decision) {
      mainStore.setCurrentDecision(decision);
      await mainStore.fetchAndSetDecision(); 
    }

    return {
      startEncounter,
      endEncounter,
      classDetails,
      expandedClasses,
      currentDecision,
      currentDecisionExplanation,
      handleUpdateDecision,
    };
  }
};
</script>



<style scoped>
header {
  background: #edf7ec;
  padding: 10px 20px;
  
}

nav a {
  margin-right: 10px;
  margin-bottom: 30px;
  text-decoration:overline;
  color: #475a42;
  white-space: nowrap;
}
.container {
  display: flex;
  height: 100vh;
  width: 100vw; 
  gap: 10px;
}

.left-side {
  position: fixed;
  top: 0;
  left: 0;
  width: 70%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.upper-part {
  flex-grow: 1;
  flex-shrink: 1;
  padding: 20px;
  background-color: ;
  color: black;
  border: 4px solid #b2d8b2;
  box-sizing: border-box;
  overflow-y: auto;
  margin: 10px;
}

.static-text {
  color: #475a42; 
  font-weight:lighter; 
}

.dynamic-text {
  color: #559661; 
  font-weight: bold; 
  margin-left: 10px; 
}


.lower-part {
  flex-grow: 1;
  flex-shrink: 1;
  padding: 20px;
  background-color: white;
  color: black;
  border: 4px solid #b2d8d8;
  box-sizing: border-box;
  overflow-y: auto;
  margin: 10px;
}

.right-side {
  position: fixed;
  top: 0;
  right: 0;
  width: 30%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-left: 1px solid #ccc;
  box-shadow: -2px 0 4px rgba(0,0,0,0.1);
}

.decision-box {
  flex: 0 0 25%;
  padding: 20px;
  background-color: white;
  color: red;
  border: 4px solid red;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  box-sizing: border-box;
  align-items: center;
  justify-content: center;
  font-size: 1.5em;
  margin: 10px;
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
}
button:last-child {
  margin-right: 0; 
}

button:hover {
  background-color: #0056b3;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

button:active {
  transform: translateY(1px);
  box-shadow: 0 3px 5px rgba(0, 0, 0, 0.2);
}

</style>