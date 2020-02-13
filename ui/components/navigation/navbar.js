module.exports = {
    props: [],
    name: 'navbar',
    data () {
        return {
            drawer: null,
        }
    },
    
    methods: {
        goToPersonal() {
            this.$router.push(`personal`)
        },

        goToDash() {
            this.$router.push(`dashboard`)
        },

        goToProject() {
            this.$router.push(`projects`)
        }
    },
};