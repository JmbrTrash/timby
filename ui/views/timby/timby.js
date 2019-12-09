module.exports = {
  name: 'threetransfer',
  components: {
  },
  props: [],
  data () {
    return {
   headers: [
        {
          text: 'User',
          align: 'left',
          sortable: false,
          value: 'user',
        },
        { text: 'Project', value: 'project' },
        { text: 'Start', value: 'start' },
        { text: 'Time worked', value: 'totaltime' },
        { text: 'Week', value: 'week' }
   ],
   time_entries: []
    }
  },
  computed: {
    ...window.vuex.mapGetters([
      'uploadMessages',
      'uploadMessage',
      'uploading'
    ]),
    showUploadButton () {
      if (this.file === '' || this.uploadMessage.code === 'UPLOADING'){
        return false
      }
      return true
    }
  },
  mounted () {
    console.log("router",)
switch(this.$route.query.view){
  case 'all':
      axios.get("http://192.168.2.10:5000/time_entries")
      .then(response => {this.time_entries = response.data; 
      })
      break;
  case 'week':
      axios.get("http://192.168.2.10:5000/time_entries_week")
      .then(response => {this.time_entries = response.data; 
      })
      break;
  case 'week_project_user':
      user=this.$route.query.user
      axios.get(`http://192.168.2.10:5000/time_entries_week_user_project/${user}`)
      .then(response => {this.time_entries = response.data; 
      })
      break;
  case 'week_user':
          user=this.$route.query.user
          axios.get(`http://192.168.2.10:5000/time_entries_week_user/${user}`)
          .then(response => {this.time_entries = response.data; 
          })
          break;
}

  },
  methods: {
    ...window.vuex.mapActions([

    ]),
    
  }
}
