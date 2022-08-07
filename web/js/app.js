const { createApp } = Vue

createApp({
    data() {
      return {
        is_diy: false,
        is_configure: false,
        meta: {
            title: 'Twitter Bunseki',
            short_desc: 'A collection of python scripts to fetch, process, and analyze Twitter data.',
            long_desc: 'The purpose of this project is to make it easier to collect and analyze Twitter data. This page offers a short introduction into the usage of the scripts and a way to customize your own pipeline so to speak. Nothing you enter here is stored on any servers or collected in any way.',
        },
        tutorial: {
            desc: 'In order to use the scripts, you have to prepare by:',
            steps: [
                {
                    text: 'Installing <code>python3.9</code> (any version >= 3.7 will work but this was tested on 3.9)',
                    links: [
                        {text: 'official docs', href: 'https://www.python.org/downloads/release/python-3913/'},
                        {text: 'instructions for different operating systems', href: 'https://montessorimuddle.org/2021/10/03/python-setup-on-different-operating-systems-2021/'}
                    ]
                },
                {
                    text: '(Optional) Creating and activating a virtual environment to isolate dependencies',
                    links: [
                        {text: 'official docs', href: 'https://docs.python.org/3.9/library/venv.html'}
                    ]
                },
                {
                    text: 'Installing dependencies',
                    links: [
                        {text: 'required dependencies', href: 'scripts/requirements.txt', download: 'requirements.txt'},
                        {text: 'how to install packages', href: 'https://packaging.python.org/en/latest/tutorials/installing-packages/'}
                    ]
                },
                {
                    text: '(If this is your first time running python scripts) Learn how to run a simple python script',
                    links: [
                        {text: 'tutorial', href: 'https://realpython.com/run-python-scripts/#how-to-run-python-scripts-using-the-command-line'}
                    ]
                }
            ]
        },
        zipped_filename: 'twbunseki_scripts',
        scripts: [
            {
                name: 'search',
                desc: 'Fetch data from Twitter API. '
                + 'Requires <a href="https://developer.twitter.com/en/products/twitter-api/academic-research">Twitter for Academic Research</a> access. '
                + 'Downloads data locally under <code>results/{filename}.csv</code>.',
                filename: 'twitter_search.py',
                src: 'scripts/twitter_search.py'
            },
            {
                name: 'filter',
                desc: 'Filter csv by a number of configurable variables. Takes any csv but config values default to format of the output from the <code>search</code> script.',
                filename: 'filter.py',
                src: 'scripts/filter.py'
            },
            {
                name: 'categorize',
                desc: 'Categorize data rows based on given keyword map. In other words, given categories and possible keywords that belong in it, it checks for keywords and decides which categories this row/tweet falls into.',
                filename: 'categorize.py',
                src: 'scripts/categorize.py'
            },
            {
                name: 'analyze',
                desc: 'Analyze data using an number of configurable methods. Expects a csv formatted by <code>search</code> but will accept fewer columns depending on configuration (e.g. output from <code>filter</code>).<br><br>'
                +'<b>Possible outputs:</b>'
                + '<ul>'
                +'<li>hashtag frequencies (also on certain months)</li>'
                +'<li>date frequencies</li>'
                +'<li>time frequencies</li>'
                +'<li>user-related metrics</li>'
                +'<li>media/URL frequencies (with possible nested tracing of redirected URLs)</li>',
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
        },
        show_configure() {
            this.is_configure = true;
        }
    }
}).mount('#app');
