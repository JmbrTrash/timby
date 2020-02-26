module.exports = {
  name: 'personal',
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
        { text: 'Time worked', value: 'time'}
      ],
      headersEntries: [ 
        { text: 'Project', value: 'project'},
        { text: 'Start', value: 'start'},
        { text: 'Time worked', value: 'time'}
      ],
      time_entries: undefined
    }
  },

  computed: {
  },

  mounted () {
    console.log(axios)
    axios.get(`http://${window.location.hostname}:${window.location.port}/api/users`)
    .then(response => { 
      this.items = response.data
    })
  },

  methods: {
    getEntries(){
      axios.get(`http://${window.location.hostname}:${window.location.port}/api/allEntriesWeekUser/${this.week}/${this.user}`)
      .then(response => {
        this.entriesWeek = response.data;
      })
    },

    setSelected(user) {
      this.getUserData(user[0]);
    },

    openTimeOverview(value){
      this.week = value.week
      this.user = value.user
      this.getEntries();
      this.dialog = true;
    },

    getUserData(user){
      axios.get(`http://${window.location.hostname}:${window.location.port}/api/time_entries_week_user/${user}`)
          .then(response => {
            this.time_entries = response.data; 
          })
    },

    async deleteEntry(value){
      var r = confirm("Are you sure you want to delete this entry?");
      if (r == true) {
        await axios.delete(`http://${window.location.hostname}:${window.location.port}/api/deleteEntry/${value}`)
        this.getEntries();
      }
    },

    toTime(timeData) {
      return timeData.hours + 'h ' + timeData.minutes + 'mins' + (timeData.day ? ' (' + timeData.day + ')' : '')
    },
  }
}
