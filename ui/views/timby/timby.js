module.exports = {
  name: 'threetransfer',
  components: {
  },
  props: [],
  data () {
    return {
    weeks:[],
    drawer: null,
    items: [],
    dataPerWeek: [],
    panel:[],
    valueYear: new Date().getFullYear().toString(),
    user: "",
    selected:"this",
    dialog: false,
    VPN: 0,
    Manual: 0,
    Local: 0,
    week: 0,
    expanded: [],
    currentyear: 0,
    singleExpand: false,
    show: false,
    headers: [
      {
        text: 'User',
        align: 'left',
        sortable: false,
        value: 'user',
      },
      { text: 'Hours worked this week', value: 'time' },
     
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
    axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries`)
    .then(response => {this.items = response.data; 
    })
    
      this.currentyear = this.valueYear;
      axios.get(`http://${window.location.hostname}:${window.location.port}/getWeeks/${this.currentyear}`)
    .then(response => {this.weeks = response.data; 
    })


  },
  methods: {
    setSelected(year) {
      this.panel=[],
      this.currentyear = year;
      axios.get(`http://${window.location.hostname}:${window.location.port}/getWeeks/${year}`)
    .then(response => {this.weeks = response.data; 

    })
    },
    handleClick(value){
      this.week = value.week
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

    
    clicked(value){
      year = this.currentyear

      axios.get(`http://${window.location.hostname}:${window.location.port}/getDataWeek/${value}/${year}`)
          .then(response => {
            this.dataPerWeek = response.data; 

          })
    },
    fullscreen(){
      var elem = document.getElementById('jipla');

        if(elem.requestFullscreen){
            elem.requestFullscreen();
        }
        else if(elem.mozRequestFullScreen){
            elem.mozRequestFullScreen();
        }
        else if(elem.webkitRequestFullscreen){
            elem.webkitRequestFullscreen();
        }
        else if(elem.msRequestFullscreen){
            elem.msRequestFullscreen();
        }
    }
    // ...window.vuex.mapActions([

    // ]),
  
    
  }
}
