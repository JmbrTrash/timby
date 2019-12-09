export default ({
    uploadFile (file) {
        return axios.post(`${window.config.fileTransferApiUrl}/fileserver/api/threetransfer/${file.name}`, 
        file,
        {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }
        )
    },
    generateLink (url) {
        return axios.post(`${window.config.jsApiUrl}/threetransfer/link`, {
            args: {
                shortlink:{
                    url
                }
            }
        })
    },
    downloadFile (identifier) {
        // return axios.get(`${window.config.fileTransferApiUrl}/fileserver/api/threetransferdownload/${identifier}`)

        return axios.request(
            {
                url: `${window.config.fileTransferApiUrl}/fileserver/api/threetransferdownload/${identifier}`, 
                method: 'GET', 
                responseType: 'blob'
            })
    },
})