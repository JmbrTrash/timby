module.exports = {
  name: 'projects',
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
        { 
          text: 'User', 
          value: 'user',
          sortable: false 
        },
        { 
          text: 'Hours worked this week', 
          value: 'time' 
        }
      ],
    }
  },

  computed: {
    
  },

  mounted () {
    axios.get(`http://${window.location.hostname}:${window.location.port}/api/projects`)
    .then(response => {this.projects = response.data; 
    })
  },

  methods: {

    getProjectData(project){
        return axios.get(`http://${window.location.hostname}:${window.location.port}/api/getProjectData/${project}`).then(r => {
          this.projectData = r.data;
        }, this);
    },

    getProjectWeeks(project){
      return axios.get(`http://${window.location.hostname}:${window.location.port}/api/getWeeksPerProject/${project}`)
        .then(response => {
          this.weeks = response.data; 
        }, this)
    },
    getProjectDataPerWeek(project, week, year){
      return axios.get(`http://${window.location.hostname}:${window.location.port}/api/getDataWeekPerProject/${project}/${week}/${year}`)
        .then(response => {
          this.ProjectDataWeek = response.data; 
        }, this)
    },
    getTotalTimeUsers(project){
      return axios.get(`http://${window.location.hostname}:${window.location.port}/api/getTotalTimesProject/${project}`).then(r => {
        this.totalTimesUsers = r.data;
      }, this)
  },
    ClickedWeek(week, year){
      this.getProjectDataPerWeek(this.currentProject, week, year)
      
    },

    async setSelected(project) {
      this.panel = []
      this.currentProject = project[0]

      await this.getProjectData(this.currentProject)
      await this.getTotalTimeUsers(this.currentProject)
      await this.getProjectWeeks(this.currentProject)
     
    }
  }
}
