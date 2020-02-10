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
      hidden1 = document.getElementById('total1')
      hidden1.classList.remove("d-none");
      hidden2 = document.getElementById('total2')
      hidden2.classList.remove("d-none");
      await this.getProjectData(this.currentProject)
      await this.getTotalTimeUsers(this.currentProject)
      console.log(this.totalTimesUsers)
      await this.getProjectWeeks(this.currentProject)
      this.displayTopTimes()
      hoursglobal= 0;
      minutesglobal=0;
      hours2019=0;
      hours2020=0;
      minutes2019=0;
      minutes2020=0;
      for(i=0;i<this.projectData.length;i++)
      {
        project = this.projectData[i]
        total = project.totaltime;
        hoursglobal +=  parseInt(total.split(',')[0])
        minutesglobal += parseInt(total.split(',')[1])
        if(project.year== '2019')
        {
          total2019= project.totaltime;
          hours2019 +=  parseInt(total2019.split(',')[0])
          minutes2019 += parseInt(total2019.split(',')[1])
        } 
        if(project.year== '2020')
        {
          total2020= project.totaltime;
          hours2020 +=  parseInt(total2020.split(',')[0])
          minutes2020 += parseInt(total2020.split(',')[1])
        }        
      }

      hoursglobal += Math.floor(minutesglobal/60)
      minutesglobal =minutesglobal%60
      this.totalTime = hoursglobal + 'u '+ minutesglobal+'min'

      hours2019 += Math.floor(minutes2019/60)
      minutes2019 =minutes2019%60
      this.totalTime2019 = hours2019 + 'u '+ minutes2019+'min'

      hours2020 += Math.floor(minutes2020/60)
      minutes2020 =minutes2020%60
      this.totalTime2020 = hours2020 + 'u '+ minutes2020+'min'
    },
  }
}
