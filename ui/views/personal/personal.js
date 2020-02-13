module.exports = {
  name: 'threetransfer',
  components: {
  },
  props: [],
  data () {
    return {
      items: [],
      entriesWeek:[],
      user: "",
      dialog: false,
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
      time_entries: undefined
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
    .then(response => { 
      this.items = response.data
    })
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
    },

    openTimeOverview(value){
      this.week = value.week
      this.user = value.user
      this.getEntries();
      this.dialog = true;
    },

    getUserData(user){
      axios.get(`http://${window.location.hostname}:${window.location.port}/time_entries_week_user/${user}`)
          .then(response => {
            this.time_entries = response.data; 
          })
    },

    async deleteEntry(value){
      var r = confirm("Are you sure you want to delete this entry?");
      if (r == true) {
        await axios.delete(`http://${window.location.hostname}:${window.location.port}/deleteEntry/${value}`)
        this.getEntries();
      }
    },

    toTime(timeData) {
      return timeData.hours + 'h ' + timeData.minutes + 'mins' + (timeData.day ? ' (' + timeData.day + ')' : '')
    }
  }
}
