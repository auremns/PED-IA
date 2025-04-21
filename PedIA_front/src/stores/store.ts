// store.ts
import { defineStore } from 'pinia';
//import axios from 'axios';
//axios.defaults.withCredentials = true;
const BACK_URL = "https://d5ptpgq7oh.execute-api.eu-west-3.amazonaws.com/prod";

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

        console.log('Fetching clicked classes...');
        const currentEncounterId = this.getEncounterId();
        await fetch(BACK_URL + '/get_clicked_classes', {
          method:"POST", credentials: 'include', body:JSON.stringify(currentEncounterId)}).then(async (response) => {
            const res = await response.json();
            console.log('Raw fetched data:', res);
            this.clickedClasses = res.clicked_classes;
            console.log('Clicked classes fetched:', this.clickedClasses);
          }
          ).catch((error) => {
            console.error('Error fetching clicked classes:', error); 
          }
          );
        
    },
    async removeClickedClass(className: string) {

        console.log(`Removing clicked class: ${className}`);
        await fetch(BACK_URL + '/remove_clicked_class', {
          method:"POST", credentials: 'include', body: JSON.stringify({ class_name: className, encounter_id: this.encounterId }), headers: {
            "Accept":"application/json", 
            "Content-Type":"application/json"
        }}).then(async (response) => {
            const res = await response.json();
            this.clickedClasses = res.clicked_classes;
            this.setCurrentDecision(res.worst_decision);
            console.log(`Clicked class removed: ${className}`);
            console.log('Updated clicked classes:', this.clickedClasses);
            console.log('Updated worst decision:', this.currentDecision);
          }
          ).catch((error) => {
            console.error('Error removing clicked class:', error); 
          }
          );
    },
    async fetchAndSetDecision(className: string) {

        console.log('Fetching decisions...');
        await fetch(BACK_URL + '/get_decision', {
          method:"POST", credentials: 'include', body: JSON.stringify({
          class_name: className,
          encounter_id: this.encounterId
        })},).then(async (response) => {
          const res = await response.json();
          this.setCurrentDecision(res.worst_decision);
          console.log('Decisions fetched:', res);
        }
        ).catch((error) => {
          console.error('Error fetching decisions:', error);
        }
        );


    },
    clearEncounterId() {
      this.encounterId = null;
      this.clickedClasses = [];
      this.currentDecision = null;
      console.log('Encounter ID and clicked classes cleared');
    },
  }
});
