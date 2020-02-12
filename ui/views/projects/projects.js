module.exports = {
  name: 'threetransfer',
  components: {
  },
  props: [],
  data () {
    return {
      drawer: null,
      projects:[],
      panel: [],
      projectData:[],
      ProjectDataWeek:[],
      totalTimesUsers:[],
      timeData: [],
      totalTime: "",
      totalTime2019:"",
      totalTime2020:"",
      currentProject:"",
      weeks: {},
      headers: [ 
        { text: 'User', value: 'user' },
           { text: 'Time worked', value: 'time' }
          
      ],
      
    }
  },


  computed: {
    
  },


  mounted () {
    axios.get(`http://${window.location.hostname}:${window.location.port}/projects`)
    .then(response => {this.projects = response.data; 
    })
  },

  methods: {
    
    goToPersonal(){
      this.$router.push(`personal`)
    },
    goToDash(){
      this.$router.push(`dashboard`)
    },
    goToProject(){
      this.$router.push(`projects`)
    },


    getProjectData(project){
        return axios.get(`http://${window.location.hostname}:${window.location.port}/getProjectData/${project}`).then(r => {
          this.projectData = r.data;
        }, this);
    },

    getProjectWeeks(project){
      return axios.get(`http://${window.location.hostname}:${window.location.port}/getWeeksPerProject/${project}`)
        .then(response => {
          this.weeks = response.data; 
        }, this)
    },
    getProjectDataPerWeek(project, week, year){
      return axios.get(`http://${window.location.hostname}:${window.location.port}/getDataWeekPerProject/${project}/${week}/${year}`)
        .then(response => {
          this.ProjectDataWeek = response.data; 
        }, this)
    },
    getTotalTimeUsers(project){
      return axios.get(`http://${window.location.hostname}:${window.location.port}/getTotalTimesProject/${project}`).then(r => {
        this.totalTimesUsers = r.data;
      }, this)
  },
    ClickedWeek(week, year){
      this.getProjectDataPerWeek(this.currentProject, week, year)
      
    },

    displayTopTimes (){
      for(i=0;i<this.totalTimesUsers.length;i++)
      {
        console.log(this.totalTimesUsers[i])
      }
    },

    async setSelected(project) {
      this.panel = []
      this.currentProject = project[0]

      await this.getProjectData(this.currentProject)
      await this.getTotalTimeUsers(this.currentProject)
      await this.getProjectWeeks(this.currentProject)
     
    },

    getTotalTime() {
      timeData = {}
      return timeData
    }
  }
}
