module.exports = {
  name: 'dashboard',
  components: {
  },
  props: [],
  data () {
    return {
      weeks:[],
      items: [],
      dataPerWeek: [],
      panel:[],
      valueYear: new Date().getFullYear().toString(),
      user: "",
      selected:"this",
      dialog: false,
      week: 0,
      expanded: [],
      currentyear: 0,
      show: false,
      headers: [
        {
          text: 'User',
          align: 'left',
          sortable: false,
          value: 'user',
        },
        { 
          text: 'Hours worked this week', 
          value: 'time' 
        },
      ],
      time_entries: []
    }
  },
  computed: {
  },
  mounted () {
    axios.get(`http://${window.location.hostname}:${window.location.port}/api/time_entries`)
      .then(response => { 
        this.items = response.data; 
      })
    this.currentyear = this.valueYear
    axios.get(`http://${window.location.hostname}:${window.location.port}/api/getWeeks/${this.currentyear}`)
      .then(response => {
        this.weeks = response.data; 
      })
  },
  methods: {
    setSelected(year) {
      this.panel = [];
      this.currentyear = year;
      axios.get(`http://${window.location.hostname}:${window.location.port}/api/getWeeks/${year}`)
        .then(response => {
          this.weeks = response.data; 
        })
    },
    customSort(items, index, isDesc) {
      items.sort((a, b) => {
        if (index[0] === 'time') {
          if (isDesc[0]) {
            return parseInt(b[index]) - parseInt(a[index]);
          } else {
            return parseInt(a[index]) - parseInt(b[index]);
          }
        }
      });
      return items;
    },
    handleClick(value){
      this.week = value.week
      this.dialog = true;
    },
    getUserData(user){
      axios.get(`http://${window.location.hostname}:${window.location.port}/api/time_entries_week_user/${user}`)
          .then(response => {this.time_entries = response.data; 
          })
    },
    
    clicked(week){
      axios.get(`http://${window.location.hostname}:${window.location.port}/api/getDataWeek/${week}/${this.currentyear}`)
          .then(response => {
            this.dataPerWeek = response.data; 
          })
    },
    fullscreen(){
      var elem = document.getElementById('fullscreen');

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
  }
}
