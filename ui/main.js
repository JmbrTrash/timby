/* eslint no-undef: 0 */
/* eslint-disable no-new */
import Vue from './packages/ems/vue/vue.js'
import Vuetify from './packages/ems/vuetify/vuetify.js'
import httpVueLoader from './packages/ems/httpVueLoader.js'
import VueRouter from './packages/ems/vue-router.js'
import './packages/legacy/fontawesome-pro/js/all.js'
import config from './config/index.js'
import store from './store/index.js'


// Make sure the dom is loaded.
document.addEventListener('DOMContentLoaded', (event) => {
  Vue.use(Vuetify)
  Vue.use(VueRouter)
  window.config = config

  const router = new VueRouter({
    routes: [{
      path: '/',
      component: httpVueLoader('./views/timby/index.vue'),
      name: 'timby',
    },
    {
      path: '/personal',
      component: httpVueLoader('./views/personal/personal.vue'),
      name: 'personal',
    },{
      path: '/dashboard',
      component: httpVueLoader('./views/timby/index.vue'),
      name: 'dashboard',
    }
  ]
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
    store,
    template: '<app></app>'
  })
})