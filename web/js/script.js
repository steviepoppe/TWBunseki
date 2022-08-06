const { createApp } = Vue

createApp({
    data() {
      return {
        scripts: [
            {
                name: 'search',
                desc: 'Fetch data from Twitter API',
                src: 'scripts/twitter_search.py'
            },
            {
                name: 'filter',
                desc: 'Filter csv by a number of configurable variables',
                src: 'scripts/filter.py'
            },
            {
                name: 'categorize',
                desc: 'Categorize data rows based on given keyword map',
                src: 'scripts/categorize.py'
            },
            {
                name: 'analyze',
                desc: 'Analyze data using an number of configurable methods',
                src: 'scripts/get_metrics.py'
            }
        ]
      }
    }
}).mount('#app');
