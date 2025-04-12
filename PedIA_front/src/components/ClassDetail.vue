<template>
  <li>
    <button @click="toggleExpand">{{ classDetail.name }}</button>
    <div v-if="classDetail.isExpanded" class="expanded-content">
      <ul>
        <li v-if="classDetail.subclasses.length > 0">
          <h3>Sous-catégories:</h3>
          <ul>
            <class-detail
              v-for="subclass in classDetail.subclasses"
              :key="subclass.name"
              :class-detail="subclass"
              :expanded-classes="expandedClasses"
              @updateDecision="handleUpdateDecision"
            />
          </ul>
        </li>
        <li v-if="classDetail.relatedClasses.length > 0">
          <h3>Il faut rechercher:</h3>
          <ul>
            <class-detail
              v-for="related in classDetail.relatedClasses"
              :key="related.name"
              :class-detail="related"
              :expanded-classes="expandedClasses"
              @updateDecision="handleUpdateDecision"
            />
          </ul>
        </li>
        <li v-if="classDetail.contextClasses.length > 0">
          <h3>Ces éléments peuvent mener à une décision:</h3>
          <ul>
            <class-detail
              v-for="context in classDetail.contextClasses"
              :key="context.name"
              :class-detail="context"
              :expanded-classes="expandedClasses"
              @updateDecision="handleUpdateDecision"
            />
          </ul>
        </li>
      </ul>
    </div>
  </li>
</template>

<script>
import { ref, inject, computed } from 'vue';
import axios from 'axios';
import { useMainStore } from '@/stores/store';
const BACK_URL = "https://ped-ia-back-384d733bb8ae.herokuapp.com";

export default {
  props: ['classDetail'],
  emits: ['updateDecision'],
  setup(props, { emit }) {
    const mainStore = useMainStore();
    const expandedClasses = inject('expandedClasses');
    const classDetail = ref(props.classDetail);


    const toggleExpand = () => {
      classDetail.value.isExpanded = !classDetail.value.isExpanded;
      if (classDetail.value.isExpanded) {
        expandedClasses.add(classDetail.value.name);
        addClassToSession(classDetail.value.name).then(() => {
          mainStore.fetchClickedClasses();
        });
        fetchDetails();
        fetchDecision(); 

      } else {
        removeDisplayedClass(classDetail.value.name);

      }
    };

    const addClassToSession = async (className) => {
      try {
        const currentEncounterId = mainStore.getEncounterId();
        await axios.post(BACK_URL + `/push_class_to_session?class_name=${className}`, currentEncounterId);
      } catch (error) {
        console.error('Error adding class to session:', error);
      }
    };

    const removeDisplayedClass = async (className) => {
      try {
        const currentEncounterId = mainStore.getEncounterId();
        await axios.post(BACK_URL + '/remove_displayed_class', {
          class_name: className, 
          encounter_id: currentEncounterId.encounter_id
        });
      } catch (error) {
        console.error('Error removing class from session:', error);
      }
    };

    const fetchDetails = () => {
      const { name } = classDetail.value;
      const currentEncounterId = mainStore.getEncounterId();
      const fetchSubclasses = axios.post(BACK_URL + `/get_subclasses?class_name=${name}`, currentEncounterId);
      const fetchRelatedClasses = axios.post(BACK_URL + `/get_classes_after_faitRechercher?class_name=${name}`, currentEncounterId);
      const fetchContextClasses = axios.post(BACK_URL + `/get_classes_after_aPourContexte?class_name=${name}`, currentEncounterId);
      Promise.all([fetchSubclasses, fetchRelatedClasses, fetchContextClasses])
        .then(([subclassesRes, relatedClassesRes, contextClassesRes]) => {
          processDetails(subclassesRes, relatedClassesRes, contextClassesRes);
        })
        .catch(error => {
          console.error('Error fetching details:', error);
        });
    };

    const processDetails = (subclassesRes, relatedClassesRes, contextClassesRes) => {
      classDetail.value.subclasses = subclassesRes.data.map(item => ({
        name: item.name,
        subclasses: [],
        relatedClasses: [],
        contextClasses: [],
        isExpanded: false
      }));
      classDetail.value.relatedClasses = relatedClassesRes.data.map(item => ({
        name: item.name,
        subclasses: [],
        relatedClasses: [],
        contextClasses: [],
        isExpanded: false
      }));
      classDetail.value.contextClasses = contextClassesRes.data.map(item => ({
        name: item.name,
        relation: item.relation,
        subclasses: [],
        relatedClasses: [],
        contextClasses: [],
        isExpanded: false
      }));
      
      fetchDecision();
    };


    const flattenContextClasses = computed(() => {
      return classDetail.value.contextClasses.reduce((acc, group) => [...acc, ...group], []);
    });

    const fetchDecision = () => {
      mainStore.fetchAndSetDecision(classDetail.value.name);
    };

    async function handleUpdateDecision(decision) {
      mainStore.setCurrentDecision(decision);
      await mainStore.fetchAndSetDecision(); 
    }


    return {
      classDetail,
      mainStore,
      toggleExpand,
      flattenContextClasses,
      expandedClasses,
      handleUpdateDecision,
    };
  }
};
</script>

<style scoped>
li {
  list-style: none;
}

.button-container {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
}

button {
  padding: 5px 10px;
  margin-right: 5px;
  background-color: #6a0505;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 5px;
}

button:hover {
  background-color: #040404;
}

.expanded-content {
  padding-left: 20px; 
}

.decision-box {
  position: fixed; 
  bottom: 20px;
  right: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border: 1px solid #ccc;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}


</style>
