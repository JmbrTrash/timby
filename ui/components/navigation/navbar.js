module.exports = {
    props: [],
    name: 'navbar',
    data () {
        return {
            drawer: null,
            routes: []
        }
    },

    created() {
        this.$router.options.routes.forEach(route => {
            if (route.meta) {
                this.routes.push(route)
            }
        })
    }
};