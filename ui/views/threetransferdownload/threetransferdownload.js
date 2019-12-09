module.exports = {
  name: 'threetransferdownload',
  components: {
  },
  props: ['identifier'],
  data() {
    return {
      
    }
  },
  computed: {
    ...window.vuex.mapGetters([
      'downloadMessage'
    ])

  },
  mounted() {
    this.downloadFile()
  },
  methods: {
    ...window.vuex.mapActions([
      'downloadfile'
    ]),
    downloadFile() {
      let file = this.downloadfile(this.identifier)
      this.downloadToSystem(file)
    },
    downloadToSystem(file) {
      console.log(file)
    },
    reloadPage(){
      window.location.reload()
    }
  }
}
