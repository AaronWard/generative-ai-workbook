<template>
    <div>
      <!-- YouTuber Filter Section -->
      <div class="filter-section">
        <label class="filter-header">
          <input
            type="checkbox"
            :checked="allYoutubersSelected"
            @change="toggleAllYoutubers"
          />
          <span class="filter-title">All</span>
        </label>
        <label
          v-for="youtuber in youtubers"
          :key="youtuber.name"
          class="youtuber-filter"
        >
          <input
            type="checkbox"
            :value="youtuber.name"
            v-model="selectedYoutubers"
          />
          <!-- Display YouTuber icon as a circular image -->
          <img
            v-if="youtuber.icon"
            :src="youtuber.icon"
            :alt="youtuber.name"
            class="youtuber-icon"
          />
          <span class="youtuber-name">{{ youtuber.name }}</span>
        </label>
      </div>
  
      <div class="filter-section-divider"></div>

      <!-- Category Filter Section -->
      <div class="filter-section">
        <label class="filter-header">
          <input
            type="checkbox"
            :checked="allCategoriesSelected"
            @change="toggleAllCategories"
          />
          <span class="filter-title">All Categories</span>
        </label>
        <label
          v-for="category in specifiedCategories"
          :key="category"
          class="category-filter"
        >
          <input
            type="checkbox"
            :value="category"
            v-model="selectedCategories"
          />
          <span class="category-name">{{ category }}</span>
        </label>
      </div>
  
      <!-- Chart -->
      <div ref="chartRef" style="width: 100%; height: 600px;"></div>
    </div>
  </template>
  
  <script>
  import { defineComponent, onMounted, ref, watch, computed } from 'vue'
  import * as echarts from 'echarts'
  import dayjs from 'dayjs'
  
  export default defineComponent({
    setup() {
      const chartRef = ref(null)
      let chart = null
  
      // Reactive variables for filters
      const selectedYoutubers = ref([])
      const youtubers = ref([])
      const selectedCategories = ref([])
  
      // List of specified categories
      const specifiedCategories = [
        "In context learning",
        "Multimodal models",
        "Agents",
        "Vector Databases",
        "Prompting",
        "Chain of thought reasoning",
        "Image",
        "Search",
        "Classification",
        "Topic Modelling",
        "Clustering",
        "Data, Text and Code generation",
        "Summarization",
        "Rewriting",
        "Extractions",
        "Proof reading",
        "Swarms",
        "Querying Data",
        "Fine tuning",
        "Executing code",
        "Sentiment Analysis",
        "Planning and Complex Reasoning",
        "Image classification and generation (If multi-modal)",
        "Philosophical reasoning and ethics",
        "Reinforcement learning",
        "Model security and privacy",
        "APIs",
        "Infrastructure"
      ]
  
      // Load and store all data entries
      const dataList = ref([])
  
      // Default icon in case channelIcon is missing
      const defaultIcon = '/assets/icons/default_icon.png' // Ensure this path is correct
  
      // Computed properties for "Select All" checkboxes
      const allYoutubersSelected = computed(() => {
        return selectedYoutubers.value.length === youtubers.value.length
      })
  
      const allCategoriesSelected = computed(() => {
        return selectedCategories.value.length === specifiedCategories.length
      })
  
      // Toggle all YouTubers
      const toggleAllYoutubers = (event) => {
        if (event.target.checked) {
          selectedYoutubers.value = youtubers.value.map(y => y.name)
        } else {
          selectedYoutubers.value = []
        }
      }
  
      // Toggle all Categories
      const toggleAllCategories = (event) => {
        if (event.target.checked) {
          selectedCategories.value = [...specifiedCategories]
        } else {
          selectedCategories.value = []
        }
      }
  
      onMounted(() => {
        chart = echarts.init(chartRef.value)
  
        // Dynamically import all JSON files from src/data
        const modules = import.meta.glob('../data/*.json', { eager: true, import: 'default' })
  
        // Load and process all data
        const tempDataList = []
  
        for (const path in modules) {
          const data = modules[path]
          if (Array.isArray(data)) {
            tempDataList.push(...data)
          } else {
            console.warn(`Data in ${path} is not an array.`)
          }
        }
  
        dataList.value = tempDataList
  
        // Extract the list of YouTubers
        const youtuberMap = new Map()
        dataList.value.forEach(entry => {
          if (entry.channel) {
            if (!youtuberMap.has(entry.channel)) {
              youtuberMap.set(entry.channel, {
                name: entry.channel,
                icon: entry.channelIcon || defaultIcon // Use default icon if not provided
              })
            }
          }
        })
        youtubers.value = Array.from(youtuberMap.values())
        selectedYoutubers.value = youtubers.value.map(y => y.name) // Select all by default
  
        // Initialize category selection
        selectedCategories.value = [...specifiedCategories] // Select all by default
  
        // Initialize the chart
        updateChart()
      })
  
      // Watch for changes in filters
      watch(
        [selectedYoutubers, selectedCategories],
        () => {
          updateChart()
        }
      )
  
      function updateChart() {
        if (!chart) return
  
        // Clear the chart
        chart.clear()
  
        // Prepare dictionaries to hold counts and video details
        const categoryCounts = {}
        const videoDetails = {}
  
        // Filter dataList based on selectedYoutubers and selectedCategories
        const filteredDataList = dataList.value.filter(entry =>
          selectedYoutubers.value.includes(entry.channel) &&
          entry.categories.some(category => selectedCategories.value.includes(category))
        )
  
        // Process the data
        filteredDataList.forEach(entry => {
          const date = dayjs(entry['published_at']).startOf('week').format('YYYY-MM-DD')
          entry['categories'].forEach(category => {
            if (selectedCategories.value.includes(category)) {
              // Update category counts
              if (!categoryCounts[category]) {
                categoryCounts[category] = {}
              }
              if (!categoryCounts[category][date]) {
                categoryCounts[category][date] = 0
              }
              categoryCounts[category][date] += 1
  
              // Store video details for tooltips using Maps to avoid duplicates
              const key = `${category}-${date}`
              if (!videoDetails[key]) {
                videoDetails[key] = new Map()
              }
              videoDetails[key].set(entry['url'], {
                title: entry['title'],
                url: entry['url'],
                channel: entry['channel'],
                description: entry['description'],
              })
            }
          })
        })
  
        // Prepare data for ECharts
        // Get all unique dates
        const datesSet = new Set()
        for (const category in categoryCounts) {
          for (const date in categoryCounts[category]) {
            datesSet.add(date)
          }
        }
        const dates = Array.from(datesSet).sort()
  
        // Prepare series data
        const series = specifiedCategories
          .filter(category => selectedCategories.value.includes(category))
          .map(category => {
            const dataPoints = dates.map(date => categoryCounts[category]?.[date] || 0)
            return {
              name: category,
              type: 'line',
              stack: 'Total',
              areaStyle: {},
              emphasis: {
                focus: 'series'
              },
              data: dataPoints
            }
          })
  
        // Function to extract YouTube video ID from URL
        function getYouTubeVideoID(url) {
          const regExp = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?(?:.*&)?v=|v\/|embed\/)|youtu\.be\/)([^#&?]*).*/
          const match = url.match(regExp)
          return match && match[1].length === 11 ? match[1] : null
        }
  
        // Prepare the option for ECharts
        const option = {
          title: {
            text: 'Topic Trends in the Past 12 Months'
          },
          tooltip: {
            trigger: 'item',
            enterable: true,
            hideDelay: 3000,
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#6a7985'
              }
            },
            formatter: params => {
              const date = dates[params.dataIndex]
              const category = params.seriesName
              const value = params.value
  
              let tooltipContent = `<strong>${date}</strong><br/>`
              tooltipContent += `<span style="color:${params.color};">${category}: ${value}</span><br/>`
  
              const key = `${category}-${date}`
              const videosMap = videoDetails[key] || new Map()
              const videos = Array.from(videosMap.values())
  
              // Build the video list
              let videoList = videos.map(video => {
                const videoId = getYouTubeVideoID(video.url)
                const thumbnailUrl = videoId
                  ? `https://img.youtube.com/vi/${videoId}/default.jpg`
                  : defaultIcon // Use default icon if video ID not found
                return `<div style="display: flex; align-items: center; margin-bottom: 5px;">
                          <img src="${thumbnailUrl}" alt="Thumbnail" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover; margin-right: 5px;">
                          <div style="line-height: 1.2;">
                            <div style="font-size: 0.85em; color: #666;">${video.channel}</div>
                            <a href="${video.url}" target="_blank" style="display: block; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.9em; color: #1a73e8;">${video.title}</a>
                          </div>
                        </div>`
              }).join('')
  
              tooltipContent += videoList
  
              return `<div style="max-height:300px;overflow-y:auto;">${tooltipContent}</div>`
            }
          },
          legend: {
            data: series.map(s => s.name),
            type: 'scroll',
            orient: 'horizontal',
            top: '7%',   // Position legend at the top
            left: 'center',
            textStyle: {
              fontFamily: 'sans-serif',
              fontSize: 12,
              color: '#333'
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '15%',  // Adjust grid top to accommodate the legend
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: dates,
            axisLabel: {
              fontFamily: 'sans-serif',
              fontSize: 12,
              color: '#333'
            }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              fontFamily: 'sans-serif',
              fontSize: 12,
              color: '#333'
            }
          },
          series: series
        }
  
        chart.setOption(option)
      }
  
      return {
        chartRef,
        youtubers,
        selectedYoutubers,
        specifiedCategories,
        selectedCategories,
        toggleAllYoutubers,
        toggleAllCategories,
        allYoutubersSelected,
        allCategoriesSelected
      }
    }
  })
  </script>
  
  <style scoped>
  .filter-section {

    display: flex;
    flex-wrap: wrap;
    margin-bottom: 15px;
    align-items: center;
    font-family: sans-serif; /* Match ECharts font */
    font-size: 14px;
    color: #333; /* Match ECharts default text color */
  }
  
  .filter-section  {
    margin-top: 30px;
  }


  /* Header for each filter section */
  .filter-header {
    
    display: flex;
    align-items: center;
    margin-right: 15px;
    font-weight: bold;
  }
  
  /* Title for each filter */
  .filter-title {
    margin-left: 5px;
    
  }
  
  /* YouTuber filter styles */
  .youtuber-filter {
    display: flex;
    align-items: center;
    margin-right: 15px;

  }
  
  .youtuber-filter input[type="checkbox"] {
    margin-right: 5px;
  }
  
  .youtuber-icon {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 5px;
  }
  
  .youtuber-name {
    font-family: inherit;
    font-size: inherit;
    color: inherit;
  }
  
  /* Category filter styles */
  .category-filter {
    display: flex;
    align-items: center;
    margin-right: 15px;
  }
  
  .category-filter input[type="checkbox"] {
    margin-right: 5px;
  }
  
  .category-name {
    font-family: inherit;
    font-size: inherit;
    color: inherit;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .filter-section {
      flex-direction: column;
      align-items: flex-start;
    }
  
    .filter-header {
      margin-bottom: 10px;
    }
  }


  .filter-section-divider {
    border-top: solid 1px #333;
    margin-top: 20px;
    margin-bottom: 20px;
  }
  </style>
  
