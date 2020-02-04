module.exports = {
  name: 'threetransfer',
  components: {
  },
  props: [],
  data () {
    return {
    drawer: null,
    items: [],
    user: "",
    dialog: false,
    VPN: "",
    Manual: "",
    Local: "",
    week: 0,
   headers: [ 
     { text: 'Week', value: 'week' },
        { text: 'Time worked', value: 'totaltime' }
       
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
    axios.get(`http://${window.location.hostname}:${window.location.port}/users`)
    .then(response => {this.items = response.data; 
      console.log(response)
    })

    console.log("router",)
switch(this.$route.query.view){
  case 'all':
    console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
      axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries`)
      .then(response => {this.time_entries = response.data; 
      })
      break;
  case 'week':
    console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
      axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
      .then(response => {this.time_entries = response.data; 
      })
      break;
  case 'week_project_user':
    console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
      user=this.$route.query.user
      axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week_user_project/${user}`)
      .then(response => {this.time_entries = response.data; 
      })
      break;
  case 'week_user':
    console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
          user=this.$route.query.user
          axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week_user/${user}`)
          .then(response => {this.time_entries = response.data; 
          })
          break;
}

  },
  methods: {
    setSelected(jipla) {
      this.getUserData(jipla[0]);
    },
    handleClick(value){
      this.week = value.week
      console.log(value)
      axios.get(`http://${window.location.hostname}:${window.location.port}/getTypes/${value.user}/${value.week}`)
      .then(response => {
        if(response.data.VPN != undefined)
        {
          this.VPN = response.data.VPN + ' uren';
        }
        else{
          this.VPN = "Geen geregistreerde uren!"
        }
        if(response.data.Manual != undefined)
        {
          this.Manual = response.data.Manual + ' uren';
        }
        else{
          this.Manual = "Geen geregistreerde uren!"
        }
        if(response.data.Local != undefined)
        {
          this.Local = response.data.Local + ' uren';
        }
        else{
          this.Local = "Geen geregistreerde uren!"
        }
      })
      this.dialog = true;
    },
    getUserData(user){
      axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week_user/${user}`)
          .then(response => {this.time_entries = response.data; 
          })
    },
    goToPersonal(){
      this.$router.push(`personal`)
    },
    goToDash(){
      this.$router.push(`dashboard`)
    }
    // ...window.vuex.mapActions([

    // ]),
  
    
  }
}
