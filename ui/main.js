/* eslint no-undef: 0 */
/* eslint-disable no-new */
import Vue from './packages/ems/vue/vue.js'
import Vuetify from './packages/ems/vuetify/vuetify.js'
import httpVueLoader from './packages/ems/httpVueLoader.js'
import VueRouter from './packages/ems/vue-router.js'
import './packages/legacy/fontawesome-pro/js/all.js'

// Make sure the dom is loaded.
document.addEventListener('DOMContentLoaded', (event) => {
  Vue.use(Vuetify)
  Vue.use(VueRouter)

  const router = new VueRouter({
    mode: 'history',
    routes: [
      {
        path: '/',
        component: httpVueLoader('./views/timby/index.vue'),
        name: 'dashboard',
        meta: { 
          'title': 'Dashboard',
          'icon': 'dashboard'
        }
      },
      {
        path: '/personal',
        component: httpVueLoader('./views/personal/personal.vue'),
        name: 'personal',
        meta: { 
          'title': 'Personal',
          'icon': 'face'
        }
      },
      {
        path: '/projects',
        component: httpVueLoader('./views/projects/projects.vue'),
        name: 'projects',
        meta: { 
          'title': 'Projects',
          'icon': 'folder'
        }
      }
    ]
  })

  Vue.filter('convertTime', function (time) {
    if (!time) return 'No work time';
    const hours = parseInt(time / 3600)
    const minutes = parseInt((time /60) % 60)
    return `${hours} h ${minutes} min`;
  })

  new Vue({
    el: '#app',
    vuetify: new Vuetify({
      iconfont: 'fa',
      theme: {
        themes: {
          light: {
            primary: '#2d4052',
            secondary: '#57be8e'
          }
        }
      }
    }),
    components: {
      app: httpVueLoader('./App/index.vue')
    },
    router,
    template: '<app></app>'
  })
})