const { createApp } = Vue

createApp({
    data() {
      return {
        is_configure: true, //change
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
                src: 'scripts/twitter_search.py',
                checked: false,
                config: [
                    {
                        name: 'Twitter API Bearer Token',
                        desc: 'Requires <a href="https://developer.twitter.com/en/products/twitter-api/academic-research">Twitter for Academic Research</a> access',
                        type: 'settings',
                        arg: 'BEARER_TOKEN',
                        input: {type: 'text', placeholder: 'Leave empty to fill in yourself in settings.py'},
                        value: null,
                    },
                    {
                        name: 'Query',
                        desc: '<b>Required</b>. Search queries can be single terms or more intricate queries. See <a href="http://t.co/operators">operators</a> and <a href="https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search">the API ref</a> for reference.',
                        type: 'command',
                        arg: '-q',
                        input: {type: 'text', placeholder: 'Enter a keyword or expression to search for'},
                        value: null,
                    },
                    {
                        name: 'Filename',
                        desc: 'Only required if you want to resume in a specific file under <code>./results/{filename}.csv</code>. Default: search query + timestamp.',
                        type: 'command',
                        arg: '-f',
                        input: {type: 'text', placeholder: 'Only the name, not the entire path'},
                        value: null,
                    },
                    {
                        name: 'Max results per request/page',
                        desc: 'Default is 500 which is max for academic accounts',
                        type: 'command',
                        arg: '-m',
                        input: {type: 'number'},
                        value: null,
                    },
                    {
                        name: 'From Datetime',
                        desc: 'This is in UTC. Can\'t be used with from/to ID.',
                        type: 'command',
                        arg: '-fd',
                        input: {type: 'datetime-local'},
                        value: null,
                    },
                    {
                        name: 'To Datetime',
                        desc: 'This is in UTC. Can\'t be used with from/to ID.',
                        type: 'command',
                        arg: '-td',
                        input: {type: 'datetime-local'},
                        value: null,
                    },
                    {
                        name: 'From ID',
                        desc: 'Can\'t be used with from/to dates. From which ID do you want to fetch/resume fetching tweets?',
                        type: 'command',
                        arg: '-fi',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Until ID',
                        desc: 'Can\'t be used with from/to dates. Until which ID do you want to fetch/resume fetching tweets?',
                        type: 'command',
                        arg: '-ui',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Exclude RTs',
                        desc: 'Use this to NOT store retweet-related data',
                        type: 'command',
                        arg: '--no-keep-rt',
                        input: {type: 'checkbox', label: 'Exclude'},
                        value: null,
                    },
                ]
            },
            {
                name: 'filter',
                desc: 'Filter csv by a number of configurable variables. Takes any csv but config values default to format of the output from the <code>search</code> script.',
                filename: 'filter.py',
                src: 'scripts/filter.py',
                checked: false,
                config: []
            },
            {
                name: 'categorize',
                desc: 'Categorize data rows based on given keyword map. In other words, given categories and possible keywords that belong in it, it checks for keywords and decides which categories this row/tweet falls into.',
                filename: 'categorize.py',
                src: 'scripts/categorize.py',
                checked: false,
                config: []
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
                src: 'scripts/get_metrics.py',
                checked: false,
                config: []
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
            this.is_configure = !this.is_configure;
        },
        show_command(script) {
            var result_html = '';
            var settings = [];
            var commands = [];
            var configs_to_show = script.config.filter(c => c.value !== null && c.value !== false);
            for (const c in configs_to_show) {
                const config = configs_to_show[c];
                if (config.type === 'settings') {
                    if (settings.length > 0) {
                        settings.push(' ');
                    }
                    settings.push((config.arg + '=' + '\'' + config.value + '\''));
                }
                else if (config.value === true) {
                    commands.push(config.arg);
                }
                else if (config.input.type === 'datetime-local') {
                    const replaced = config.value + ':00Z';
                    commands.push((config.arg + ' "' + replaced + '"'));
                }
                else if (config.value.length > 0) { // command with text
                    const replaced = config.value.replaceAll('"', '\'');
                    commands.push((config.arg + ' "' +  replaced + '"'));
                }
                else if (config.input.type === 'number') {
                    commands.push((config.arg + ' ' + config.value));
                }
            }

            result_html += '<p><b>cmd/Terminal</b></p>';
            result_html += ('<p><pre><span class="unselectable">$ </span><code>python ' + script.filename + ' ' + commands.join(' ') + '</code></pre></p>');
            if (settings.length > 0) {
                result_html += '<p><b>settings.py</b></p>';
                result_html += ('<p><pre><code>' + settings.join('<br> ') + '</code></pre></p>');
            }
            return result_html;
        }
    }
}).mount('#app');
