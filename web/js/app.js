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
        commands: {},
        settings: {},
        json_configs: {},
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
                        required: true,
                        desc: 'Requires <a href="https://developer.twitter.com/en/products/twitter-api/academic-research">Twitter for Academic Research</a> access',
                        type: 'settings',
                        arg: 'BEARER_TOKEN',
                        input: {type: 'text', placeholder: 'Leave empty to fill in yourself in settings.py'},
                        value: '',
                    },
                    {
                        name: 'Query',
                        required: true,
                        desc: 'Search queries can be single terms or more intricate queries. See <a href="http://t.co/operators">operators</a> and <a href="https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search">the API ref</a> for reference.',
                        type: 'command',
                        arg: '-q',
                        input: {type: 'text', placeholder: 'Enter a keyword or expression to search for'},
                        value: null,
                    },
                    {
                        name: 'Filename',
                        required: false,
                        desc: 'Only required if you want to resume in a specific file under <code>./results/{filename}.csv</code>. Default: search query + timestamp.',
                        type: 'command',
                        arg: '-f',
                        input: {type: 'text', placeholder: 'Only the name, not the entire path'},
                        value: null,
                    },
                    {
                        name: 'Max results per request/page',
                        required: false,
                        desc: 'Default is 500 which is max for academic accounts',
                        type: 'command',
                        arg: '-m',
                        input: {type: 'number'},
                        value: null,
                    },
                    {
                        name: 'From Datetime',
                        required: false,
                        desc: 'This is in UTC. Can\'t be used with from/to ID.',
                        type: 'command',
                        arg: '-fd',
                        input: {type: 'datetime-local'},
                        value: null,
                    },
                    {
                        name: 'To Datetime',
                        required: false,
                        desc: 'This is in UTC. Can\'t be used with from/to ID.',
                        type: 'command',
                        arg: '-td',
                        input: {type: 'datetime-local'},
                        value: null,
                    },
                    {
                        name: 'From ID',
                        required: false,
                        desc: 'Can\'t be used with from/to dates. From which ID do you want to fetch/resume fetching tweets?',
                        type: 'command',
                        arg: '-fi',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Until ID',
                        required: false,
                        desc: 'Can\'t be used with from/to dates. Until which ID do you want to fetch/resume fetching tweets?',
                        type: 'command',
                        arg: '-ui',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Exclude RTs',
                        required: false,
                        desc: 'Use this to NOT store retweet-related data. ',
                        type: 'command',
                        arg: '--no-keep-rt',
                        input: {type: 'checkbox'},
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
                config: [
                    {
                        name: 'Input Filename',
                        required: true,
                        desc: 'Full or relative path to the csv file. E.g. <code>results/my_data.csv</code>',
                        type: 'command',
                        arg: '-f',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Output Filename',
                        required: false,
                        desc: 'Full or relative path to the output/filtered csv file. Default: <code>output.csv</code>',
                        type: 'command',
                        arg: '-o',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Columns',
                        required: false,
                        desc: 'Columns to keep. Separated with comma. If any are set, only those are saved. Applied after processing. Can be multiple. E.g. <code>created_at,text</code>',
                        type: 'command',
                        arg: '-c',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Date Column',
                        required: false,
                        desc: 'Name of the column with the date to filter with. Required for date filtering/tz conversion. Default: <code>created_at</code>',
                        type: 'command',
                        arg: '--date-col',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Timezone',
                        required: false,
                        desc: 'Timezone to convert time data to. If date column in input csv is not tz-aware, will assume UTC. See <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">here under "TZ Database Name"</a> for reference.',
                        type: 'command',
                        arg: '-tz',
                        input: {type: 'text', placeholder: 'e.g. Asia/Tokyo'},
                        value: null,
                    },
                    {
                        name: 'From Date',
                        required: false,
                        desc: 'Get all rows where date col date >= this date',
                        type: 'command',
                        arg: '--from-date',
                        input: {type: 'date'},
                        value: null,
                    },
                    {
                        name: 'To Date',
                        required: false,
                        desc: 'Get all rows where date col date <= this date',
                        type: 'command',
                        arg: '--to-date',
                        input: {type: 'date'},
                        value: null,
                    },
                    {
                        name: 'Text Column',
                        required: false,
                        desc: 'Name of the column with the text to query. Required for query. Default: <code>text</code>',
                        type: 'command',
                        arg: '--text-col',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Query',
                        required: false,
                        desc: 'Query specified text column with given substrings. Can use boolean operators AND/OR and NOT (caps required). NO NESTED RULES/PARANTHESES. Wrap strings in quotes if separated by space. E.g. <code>keyword1 AND keyword2</code>',
                        type: 'command',
                        arg: '-q',
                        input: {type: 'text', placeholder: 'Do not mix AND/OR operators in the same expression'},
                        value: null,
                    },
                    {
                        name: 'Remove media URLs',
                        required: false,
                        desc: 'Remove t.co URLs from the specified text column',
                        type: 'command',
                        arg: '--remove-media-urls',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Exclude RTs',
                        required: false,
                        desc: 'Get only rows where is_retweet == False',
                        type: 'command',
                        arg: '--no-keep-rt',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                ]
            },
            {
                name: 'categorize',
                desc: 'Categorize data rows based on given keyword map. In other words, given categories and possible keywords that belong in it, it checks for keywords and decides which categories this row/tweet falls into.',
                filename: 'categorize.py',
                src: 'scripts/categorize.py',
                checked: false,
                config: [
                    {
                        name: 'Categories',
                        required: true,
                        desc: 'Enter categories (left) and comma-separated keywords (right) that belong to that category.',
                        type: 'config',
                        arg: 'categories',
                        count: 1,
                        input: [{type: 'text', placeholder: 'Category', width: '15%', margin: '0em'}, {type: 'text', placeholder: 'Comma-separated keywords', width: '75%', margin: '0.5em'}],
                        value: []  // key: value
                    },
                    {
                        name: 'Categories JSON Filepath',
                        required: true,
                        desc: 'Path to JSON file with categories. Default: name of file downloaded by this webpage',
                        type: 'command',
                        arg: '-c',
                        input: {type: 'text', placeholder: 'Don\'t forget the folder path if running script from a different folder'},
                        value: 'categorize.config.json'
                    },
                    {
                        name: 'Input Filename',
                        required: true,
                        desc: 'Full or relative path to the csv file. E.g. <code>results/my_data.csv</code>',
                        type: 'command',
                        arg: '-i',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Output Filename (Categorized)',
                        required: false,
                        desc: 'Full or relative path to the output/categorized csv file. Default: <code>results/categorize_output.csv</code>',
                        type: 'command',
                        arg: '-o',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Output Filename (Word Frequencies)',
                        required: false,
                        desc: 'Full or relative path to the output/categorized csv file. Default: <code>results/keyword_frequencies.csv</code>',
                        type: 'command',
                        arg: '-of',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Text Column',
                        required: false,
                        desc: 'Name of the column with the text to query. Required for query. Default: <code>text</code>',
                        type: 'command',
                        arg: '-t',
                        input: {type: 'text'},
                        value: null,
                    },
                    {
                        name: 'Categorize Entire Conversations',
                        required: false,
                        desc: 'Apply the same categories to entire conversations. Uses the column "conversation_id" for grouping',
                        type: 'command',
                        arg: '--categorize-entire-conversation',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                ]
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
                config: [
                    {
                        name: 'Input Filename',
                        required: true,
                        desc: 'Full or relative path to the csv file. E.g. <code>results/my_data.csv</code>',
                        type: 'command',
                        arg: '-f',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Chunk Size',
                        required: false,
                        desc: 'Size of processing chunk. Default: 100K (rows)',
                        type: 'command',
                        arg: '-c',
                        input: {type: 'number'},
                        value: null,
                    },
                    {
                        name: 'Timezone',
                        required: false,
                        desc: 'Timezone to convert time data to before analysis (does not impact original file). See <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">here under "TZ Database Name"</a> for reference.',
                        type: 'command',
                        arg: '-tz',
                        input: {type: 'text', placeholder: 'e.g. Asia/Tokyo'},
                        value: null,
                    },
                    {
                        name: 'Analyze URLs/media',
                        required: false,
                        desc: 'Use this to process/expand media/URLs. ',
                        type: 'command',
                        arg: '--analyze-urls',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Max Redirect Depth',
                        required: false,
                        desc: 'Max depth to follow redirects when analyzing URLs. Default is the minimum: 1 (get link after t.co). <b>WARNING:</b> exponentially slower with each added layer of depth.',
                        type: 'command',
                        arg: '--max-redirect-depth',
                        input: {type: 'number'},
                        value: null,
                    },
                    {
                        name: 'Exclude Twitter URLs',
                        required: false,
                        desc: 'Use this to exclude any url that expands to <code>https://twitter.com/*</code> ',
                        type: 'command',
                        arg: '--exclude-twitter-urls',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Exclude RTs',
                        required: false,
                        desc: 'Use this to NOT process retweets. ',
                        type: 'command',
                        arg: '--no-keep-rt',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Exclude Hashtag Analysis',
                        required: false,
                        desc: 'Use this to NOT process hashtags. ',
                        type: 'command',
                        arg: '--no-analyze-hashtags',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Exclude Date Analysis',
                        required: false,
                        desc: 'Use this to NOT process dates. ',
                        type: 'command',
                        arg: '--no-analyze-date',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Exclude Time Analysis',
                        required: false,
                        desc: 'Use this to NOT process times within a day. ',
                        type: 'command',
                        arg: '--no-analyze-time',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'Exclude User Analysis',
                        required: false,
                        desc: 'Use this to NOT process users. ',
                        type: 'command',
                        arg: '--no-analyze-users',
                        input: {type: 'checkbox'},
                        value: null,
                    },
                    {
                        name: 'From Date',
                        required: false,
                        desc: 'Use only if you want to limit processing from a certain date (not datetime)',
                        type: 'command',
                        arg: '--from-date',
                        input: {type: 'date'},
                        value: null,
                    },
                    {
                        name: 'To Date',
                        required: false,
                        desc: 'Use only if you want to limit processing to a certain date (not datetime)',
                        type: 'command',
                        arg: '--to-date',
                        input: {type: 'date'},
                        value: null,
                    },
                    {
                        name: 'CSV Separator',
                        required: false,
                        desc: 'Separator for your csv file. Default: <code>comma ","</code>',
                        type: 'command',
                        arg: '--csv-sep',
                        input: {type: 'select', options: [{value: ',', name: 'comma ","'}, {value: ';', name: 'semi-colon ";"'}, {value: '|', name: 'pipe "|"'}, {value: '\t', name: 'tab'}] },
                        value: null,
                    },
                ]
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
        handle_config_value(event) {
            const value = event.target.value;
            const data = event.target.dataset;
            const count = parseInt(data.count);
            const index = parseInt(data.index);
            const exists = this.scripts[data.script].config[data.element].value.length >= count;
            if (!exists) {
                this.scripts[data.script].config[data.element].value[count - 1] = [null, null];
            }
            this.scripts[data.script].config[data.element].value[count - 1][index] = value;
        },
        increment(script_index, config_index) {
            this.scripts[script_index].config[config_index].count += 1;
        },
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
        download_configured(include_scripts) {
            const comp = this;
            const folder_name = include_scripts ? comp.zipped_filename + '_configured' : 'twbunseki_configuration';
            var zip = JSZip();
            var folder = zip.folder(folder_name);
            const to_download = comp.scripts.filter(s => s.checked);
            const to_download_names = to_download.map(s => s.name);

            if (include_scripts) {
                for (const i in to_download) {
                    var fetched = fetch(to_download[i].src).then(response => response.blob());
                    folder.file(to_download[i].filename, fetched);
                }

            }

            const other_download = comp.other_files.filter(f => f.filename !== 'settings.py');
            for (const j in other_download) {
                var fetched = fetch(other_download[j].src).then(response => response.blob());
                folder.file(other_download[j].filename, fetched);
            }

            for (const sn_c in comp.commands) {
                if (to_download_names.includes(sn_c)) {
                    folder.file(sn_c + '.bat', comp.commands[sn_c]);
                }
            }

            for (const sn_j in comp.json_configs) {
                if (to_download_names.includes(sn_j)) {
                    folder.file(sn_j + '.config.json', comp.json_configs[sn_j]);
                }
            }

            const configured_settings = [];

            for (const sn_s in comp.settings) {
                if (to_download_names.includes(sn_s)) {
                    configured_settings.push(comp.settings[sn_s]);
                }
            }

            folder.file('settings.py', configured_settings.join('\n'));

            const blob = zip.generateAsync({type:'blob'}).then((blob) => {
                const url = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = folder_name + '.zip';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
        },
        show_configure() {
            // this.is_configure = !this.is_configure;
            var a = document.createElement('a');
            a.href = '#configure-pipeline';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        show_command(script) {
            var result_html = '';
            var settings = [];
            var commands = [];
            var json_configs = [];
            var json_config_meta = null;
            var configs_to_show = script.config.filter(c => c.value !== null && c.value !== false);
            for (const c in configs_to_show) {
                const config = configs_to_show[c];
                if (config.type === 'settings') {
                    if (settings.length > 0) {
                        settings.push(' ');
                    }
                    settings.push((config.arg + '=' + '\'' + config.value + '\''));
                }
                else if (config.type == 'config') {
                    json_config_meta = config; // assumes 1 config max per script
                    for (const i in config.value) {
                        // assumes key: comma-sep values structure
                        const el = {}
                        if (config.value[i][1] !== null) {
                            el[config.value[i][0]] = config.value[i][1].split(',').map(x => x.trim());
                            json_configs.push(el);
                        } 
                    }
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
            const command = 'python ' + script.filename + ' ' + commands.join(' ');
            this.commands[script.name] = command;
            this.settings[script.name] = settings.join('\n');
            result_html += '<p><b>cmd/Terminal</b></p>';
            result_html += ('<p><pre><span class="unselectable">$ </span><code>' + command + '</code></pre></p>');
            if (settings.length > 0) {
                result_html += '<p><b>settings.py</b></p>';
                result_html += ('<p><pre><code>' + settings.join('<br> ') + '</code></pre></p>');
            }
            if (json_configs.length > 0) {
                var result_json = {};
                result_json[json_config_meta.arg] = json_configs;
                const str_json = JSON.stringify(result_json, null, 2);
                this.json_configs[script.name] = str_json;
                result_html += '<p><b>' + script.name + '.config.json</b></p>';
                result_html += '<p><pre><code>' + str_json + '</code></pre></p>';
            }
            return result_html;
        }
    }
}).mount('#app');
