// store.ts
import { defineStore } from 'pinia';
import axios from 'axios';
const BACK_URL = "https://ped-ia-back-384d733bb8ae.herokuapp.com";

export const useMainStore = defineStore('main', {
  state: () => ({
    encounterId: null as string | null,
    currentDecision: null as string | null,
    clickedClasses: [] as string[]
  }),
  actions: {
    setEncounterId(id: string) {
      this.encounterId = id;
    },
    setCurrentDecision(decision: string) {
      this.currentDecision = decision;
    },
    getEncounterId() {
      return {"encounter_id": this.encounterId}
    },
    async fetchClickedClasses() {
      try {
        console.log('Fetching clicked classes...');
        const currentEncounterId = this.getEncounterId();
        const response = await axios.post(BACK_URL + '/get_clicked_classes', currentEncounterId);
        console.log('Raw fetched data:', response.data);
        this.clickedClasses = response.data.clicked_classes;
        console.log('Clicked classes fetched:', this.clickedClasses);
        
      } catch (error) {
        console.error('Error fetching clicked classes:', error);
      }
    },
    async removeClickedClass(className: string) {
      try {
        console.log(`Removing clicked class: ${className}`);
        const response = await axios.post(BACK_URL + '/remove_clicked_class', { class_name: className, encounter_id: this.encounterId });
        if (response.status === 200) {
          this.clickedClasses = response.data.clicked_classes;
          this.setCurrentDecision(response.data.worst_decision);
          console.log(`Clicked class removed: ${className}`);
          console.log('Updated clicked classes:', this.clickedClasses);
          console.log('Updated worst decision:', this.currentDecision);
          
        } else {
          console.error('Error removing clicked class:', response.data.error);
        }
      } catch (error) {
        console.error('Error removing clicked class:', error);
      }
    },
    async fetchAndSetDecision(className: string) {
      try {
        console.log('Fetching decisions...');
        const response = await axios.post(BACK_URL + '/get_decision', {
          class_name: className,
          encounter_id: this.encounterId
        });
        this.setCurrentDecision(response.data.worst_decision);
        console.log('Decisions fetched:', response.data);
      } catch (error) {
        console.error('Error fetching decisions:', error);
      }
    },
    clearEncounterId() {
      this.encounterId = null;
      this.clickedClasses = [];
      this.currentDecision = null;
      console.log('Encounter ID and clicked classes cleared');
    },
  }
});
