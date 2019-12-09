import threetransferService from '../service.js'

export default ({
    state : {
        uploadMessages: [],
        uploadMessage: "",
        downloadMessage: ""
    },
    actions: {
        uploadfile: (context, file) => {
            context.commit('addMessage', {message: 'Uploading file', code:'UPLOADING', color:'green'})
            console.log('in service uploadfile' , file)
            threetransferService.uploadFile(file).then(response => {
                context.commit('addMessage', {message: 'File has been succesfully uploaded', color:'green'})
                context.dispatch('generateLink',file.name)
            }).catch(error => {
                context.commit('addMessage', {message: 'An error occured during the uploading of the file', code:'ERROR', color:'red'})
                console.log(`Request failed: `, error)
            })
        },
        generateLink: (context, url) => {
            // context.commit('addMessage', {message: 'Generating link', color:'green'})
            threetransferService.generateLink(url).then(response => {
                let url = `${window.location.origin}/fileserver/threetransfer/#/download/${response.data.identifier}`
                let message = `The file is available for download on the following url: `
                context.commit('addMessage', {message: message, code:'SUCCESS', color:'green', url:url})
            }).catch(error => {
                context.commit('addMessage', {message: 'Link generation failed', code:'ERROR', color:'red'})
                this.uploading = false
                console.log(error)
            })
        },
        downloadfile: (context, identifier) => {
            console.log(`downloadfile`, identifier)
            context.commit('setDownloadMessage', {message: 'Downloading file', code:'DOWNLOADING'})
            console.log(`downloadmessage` , context.downloadMessage)
            threetransferService.downloadFile(identifier).then(response => {
                console.log(response)
                const a = document.createElement("a");
                a.style.display = "none";
                document.body.appendChild(a);
                console.log(response.data)
                // Set the HREF to a Blob representation of the data to be downloaded
                a.href = window.URL.createObjectURL(
                    new Blob([response.data]/*, {type: response.data.type}*/)
                );
                
                // Use download attribute to set set desired file name
                
                a.setAttribute("download", response.headers.filename);
                
                // Trigger the download by simulating click
                a.click();
                
                // Cleanup
                window.URL.revokeObjectURL(a.href);
                document.body.removeChild(a);
                context.commit('setDownloadMessage', {message: 'File successfully downloaded!', code:'SUCCESS'})

            }).catch(error => {
                console.log(error)
                context.commit('setDownloadMessage', {message: 'Downloading failed, please try again', code:'ERROR', color:'red'})
            })
        },
        clearMessages: (context) => {
            context.commit('clearMessages')
        } 
    },
    mutations: {
        addMessage: (state, message) => { 
            state.uploadMessages.push(message);
            state.uploadMessage = message
        },
        clearMessages: (state) => { 
            state.uploadMessages = []
            state.uploadMessage = ""
        },
        setDownloadMessage: (state, message) => {
            state.downloadMessage = message;
        }
    },
    getters: {
        uploadMessage: (state) => state.uploadMessage,
        uploadMessages: (state) => state.uploadMessages,
        downloadMessage: (state) => state.downloadMessage
    }
})