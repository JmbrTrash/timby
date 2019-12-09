/* eslint no-undef: 0 */
/* eslint-disable no-new */
import Vue from '/packages/ems/vue/vue.js'
import Vuex from '/packages/ems/vuex.js'
import transferStore from './store.js'

window.vuex = Vuex
Vuex.jimber = true

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    transferStore
  }
})
