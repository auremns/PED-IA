import { createRouter, createWebHistory } from 'vue-router';
import MotifsListe from '../components/MotifsListe.vue'; 
import MotifsDetails from '../components/MotifsDetails.vue'; 
import ClassDetail from '../components/ClassDetail.vue'; 

const router = createRouter({
  history: createWebHistory("/"),
  routes: [
    {
      path: '/',
      redirect: '/list',
    },
    {
      path: '/list',
      name: 'motivesList',
      component: MotifsListe,
    },
    {
      path: '/detail/:motifs',
      name: 'motivesDetail',
      component: MotifsDetails,
      props: true,
    },
    {
      path: '/detail/:classes',
      name: 'classesDetail',
      component: ClassDetail,
      props: true,
    },
  ],
});

export default router;
