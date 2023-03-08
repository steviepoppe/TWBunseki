const { createApp } = Vue

createApp({
    data() {
      return {
        is_configure: true, //change
        meta: {
            title: '2channel Bunseki',
            short_desc: 'A collection of scripts for analysis of 2channel data.',
            long_desc: '',
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
        zipped_filename: '2ch_scripts',
        commands: {},
        settings: {},
        json_configs: {},
        scripts: [
            {
                name: 'analyze',
                desc: 'Analyze downloaded csv data.',
                filename: 'analyze_2ch.py',
                src: 'scripts/analyze_2ch.py',
                checked: false,
                config: [
                    {
                        name: 'Input Filepath Pattern',
                        required: true,
                        desc: 'Full or relative path pattern for the csv files. Can use wildcards. Example: <code>C://Downloads/2channel_mythread_*.csv</code>',
                        type: 'command',
                        arg: '-fp',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Save Folder',
                        required: true,
                        desc: 'Folder prefix to store results in. Can be something like <code>results/mythread/</code>',
                        type: 'command',
                        arg: '-s',
                        input: {type: 'text', placeholder: 'Only folders'},
                        value: null,
                    },
                ]
            },
            {
                name: 'extract',
                desc: 'Extract and merge csv data from html files.',
                filename: 'extract_2ch.py',
                src: 'scripts/extract_2ch.py',
                checked: false,
                config: [
                    {
                        name: 'Input Filepath Pattern',
                        required: true,
                        desc: 'Full or relative path pattern for the csv files. Can use wildcards. Example: <code>C://Downloads/2channel_mythread_*.html</code>',
                        type: 'command',
                        arg: '-fp',
                        input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
                        value: null,
                    },
                    {
                        name: 'Save Folder',
                        required: true,
                        desc: 'Folder prefix to store results in. Can be something like <code>results/mythread/</code>',
                        type: 'command',
                        arg: '-s',
                        input: {type: 'text', placeholder: 'Only folders'},
                        value: null,
                    },
                ]
            },
            // {
            //     name: 'categorize',
            //     desc: 'Categorize data rows based on given keyword map. In other words, given categories and possible keywords that belong in it, it checks for keywords and decides which categories this row/tweet falls into.',
            //     filename: 'categorize.py',
            //     src: 'scripts/categorize.py',
            //     checked: false,
            //     config: [
            //         {
            //             name: 'Categories',
            //             required: true,
            //             desc: 'Enter categories (left) and comma-separated keywords (right) that belong to that category.',
            //             type: 'config',
            //             arg: 'categories',
            //             count: 1,
            //             input: [{type: 'text', placeholder: 'Category', width: '15%', margin: '0em'}, {type: 'text', placeholder: 'Comma-separated keywords', width: '75%', margin: '0.5em'}],
            //             value: []  // key: value
            //         },
            //         {
            //             name: 'Categories JSON Filepath',
            //             required: true,
            //             desc: 'Path to JSON file with categories. Default: name of file downloaded by this webpage',
            //             type: 'command',
            //             arg: '-c',
            //             input: {type: 'text', placeholder: 'Don\'t forget the folder path if running script from a different folder'},
            //             value: 'categorize.config.json'
            //         },
            //         {
            //             name: 'Input Filename',
            //             required: true,
            //             desc: 'Full or relative path to the csv file. E.g. <code>results/my_data.csv</code>',
            //             type: 'command',
            //             arg: '-i',
            //             input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
            //             value: null,
            //         },
            //         {
            //             name: 'Output Filename (Categorized)',
            //             required: false,
            //             desc: 'Full or relative path to the output/categorized csv file. Default: <code>results/categorize_output.csv</code>',
            //             type: 'command',
            //             arg: '-o',
            //             input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
            //             value: null,
            //         },
            //         {
            //             name: 'Output Filename (Word Frequencies)',
            //             required: false,
            //             desc: 'Full or relative path to the output/categorized csv file. Default: <code>results/keyword_frequencies.csv</code>',
            //             type: 'command',
            //             arg: '-of',
            //             input: {type: 'text', placeholder: 'Full path including folders from where the script will be running'},
            //             value: null,
            //         },
            //         {
            //             name: 'Text Column',
            //             required: false,
            //             desc: 'Name of the column with the text to query. Required for query. Default: <code>text</code>',
            //             type: 'command',
            //             arg: '-t',
            //             input: {type: 'text'},
            //             value: null,
            //         },
            //         {
            //             name: 'Categorize Entire Conversations',
            //             required: false,
            //             desc: 'Apply the same categories to entire conversations. Uses the column "conversation_id" for grouping',
            //             type: 'command',
            //             arg: '--categorize-entire-conversation',
            //             input: {type: 'checkbox'},
            //             value: null,
            //         },
            //     ]
            // },
        ],
        other_files: [
            {
                filename: 'requirements.txt',
                src: 'scripts/requirements.txt',
            },
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
