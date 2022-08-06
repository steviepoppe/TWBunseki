const { createApp } = Vue

createApp({
    data() {
      return {
        zipped_filename: 'twbunseki_scripts',
        scripts: [
            {
                name: 'search',
                desc: 'Fetch data from Twitter API',
                filename: 'twitter_search.py',
                src: 'scripts/twitter_search.py'
            },
            {
                name: 'filter',
                desc: 'Filter csv by a number of configurable variables',
                filename: 'filter.py',
                src: 'scripts/filter.py'
            },
            {
                name: 'categorize',
                desc: 'Categorize data rows based on given keyword map',
                filename: 'categorize.py',
                src: 'scripts/categorize.py'
            },
            {
                name: 'analyze',
                desc: 'Analyze data using an number of configurable methods',
                filename: 'get_metrics.py',
                src: 'scripts/get_metrics.py'
            }
        ],
        other_files: [
            {
                filename: 'requirements.txt',
                src: 'scripts/requirements.txt',
            },
            {
                filename: 'settings.py',
                src: 'scripts/settings.py.example'
            }
        ]
      }
    },
    methods: {
        download_all() {
            const comp = this;
            var zip = JSZip();
            var folder = zip.folder(comp.zipped_filename);

            for (const i in comp.scripts) {
                var fetched = fetch(comp.scripts[i].src).then(response => response.blob());
                folder.file(comp.scripts[i].filename, fetched);
            }

            for (const j in comp.other_files) {
                var fetched = fetch(comp.other_files[j].src).then(response => response.blob());
                folder.file(comp.other_files[j].filename, fetched);
            }

            const blob = zip.generateAsync({type:'blob'}).then((blob) => {
                const url = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = comp.zipped_filename + '.zip';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
        }
    }
}).mount('#app');
