module.exports = {
  name: 'threetransfer',
  components: {
  },
  props: [],
  data () {
    return {
    drawer: null,
    items: [],
    entriesWeek:[],
    user: "",
    dialog: false,
    VPN: "",
    Manual: "",
    Local: "",
    week: 0,
   headers: [ 
    { text: 'Year', value: 'year'},
     { text: 'Week', value: 'week'},
        { text: 'Time worked', value: 'totaltime'}
       
   ],
   headersEntries: [ 
    { text: 'Project', value: 'project'},
     { text: 'Start', value: 'start'},
        { text: 'Time worked', value: 'totaltime'}
       
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

//     console.log("router",)
// switch(this.$route.query.view){
//   case 'all':
//     console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
//       axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries`)
//       .then(response => {this.time_entries = response.data; 
//       })
//       break;
//   case 'week':
//     console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
//       axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
//       .then(response => {this.time_entries = response.data; 
//       })
//       break;
//   case 'week_project_user':
//     console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
//       user=this.$route.query.user
//       axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week_user_project/${user}`)
//       .then(response => {this.time_entries = response.data; 
//       })
//       break;
//   case 'week_user':
//     console.log(`http://${window.location.hostname}:${window.location.port}/time_entries_week`)
//           user=this.$route.query.user
//           axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week_user/${user}`)
//           .then(response => {this.time_entries = response.data; 
//           })
//           break;
//}eeee





  },
  methods: {

    getEntries(){
      axios.get(`http://${window.location.hostname}:${window.location.port}/allEntriesWeekUser/${this.week}/${this.user}`)
      .then(response => {
        this.entriesWeek = response.data;
      })
    },

    setSelected(jipla) {
      this.getUserData(jipla[0]);
      table = document.getElementById('table')
      table.classList.remove("d-none");
    },
    handleClick(value){
      this.week = value.week
      console.log(value)
      this.user = value.user
      // axios.get(`http://${window.location.hostname}:${window.location.port}/getTypes/${value.user}/${value.week}`)
      // .then(response => {
      //   if(response.data.VPN != undefined)
      //   {
      //     this.VPN = response.data.VPN + ' uren';
      //   }
      //   else{
      //     this.VPN = "Geen geregistreerde uren!"
      //   }
      //   if(response.data.Manual != undefined)
      //   {
      //     this.Manual = response.data.Manual + ' uren';
      //   }
      //   else{
      //     this.Manual = "Geen geregistreerde uren!"
      //   }
      //   if(response.data.Local != undefined)
      //   {
      //     this.Local = response.data.Local + ' uren';
      //   }
      //   else{
      //     this.Local = "Geen geregistreerde uren!"
      //   }
      // })
      this.getEntries();

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
    },
    goToProject(){
      this.$router.push(`projects`)
    },
    // ...window.vuex.mapActions([

    // ]),
    async deleteEntry(value){
      var r = confirm("Are you sure you want to delete this entry?");
      if (r == true) {
        await axios.delete(`http://${window.location.hostname}:${window.location.port}/deleteEntry/${value}`)
        this.getEntries();
      } else {
       alert('Cancelled deletion!')
      }
    },

    toTime(timeData) {
      return timeData.hours + 'h ' + timeData.minutes + 'mins' + (timeData.day ? ' (' + timeData.day + ')' : '')
    }
  }
}
