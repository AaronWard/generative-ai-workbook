<template>
  <div class="book-reader">
    <div class="controls">
      <button @click="playCurrentChunk" :disabled="isPlaying">Play</button>
      <button @click="pauseTTS" :disabled="!isPlaying">Pause</button>
      <!-- If you want next chunk manually, uncomment below
        <button @click="goToNextChunk" :disabled="chunkId >= maxChunkId">Next Chunk</button>
        -->
    </div>

    <div class="chunk-container" ref="chunkContainer">
      <p :class="{ highlight: isPlaying }">
        {{ currentChunkText }}
      </p>
    </div>

    <div class="query-box">
      <input
        v-model="question"
        placeholder="Ask about the current chunk..."
        @keyup.enter="askQuestion"
      />
      <button @click="askQuestion">Ask</button>
      <div v-if="answer"><strong>Answer:</strong> {{ answer }}</div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "BookReader",
  data() {
    return {
      chunkId: 0,
      maxChunkId: 2, // Adjust as needed based on how many total chunks you have

      currentChunkText: "",
      currentAudio: null, // Audio object for the current chunk
      preloadedAudio: null, // Audio object for the next chunk

      isPlaying: false,
      question: "",
      answer: "",

      preloadTriggered: false, // To avoid multiple calls during a single chunk
    };
  },
  mounted() {
    // Load initial chunk text and TTS
    this.loadChunk(this.chunkId).then(() => {
      // this.generateTTSForCurrentChunk();
      // Preload the next chunk’s audio as well
      // this.preloadNextChunk();
    });
  },
  methods: {
    /**
     *  Fetch text for a given chunkId from the backend.
     */
    async loadChunk(id) {
      try {
        const res = await axios.get(`http://localhost:8003/chunks/${id}`);
        if (res.data.error) {
          console.error(res.data.error);
        } else {
          this.currentChunkText = res.data.text;
        }
      } catch (err) {
        console.error("Failed to load chunk:", err);
      }
    },

    /**
     *  Generate TTS for the *current* chunk and store in `currentAudio`.
     */
    async generateTTSForCurrentChunk() {
      try {
        const body = {
          text: this.currentChunkText,
          voice_id: "JBFqnCBsd6RMkjVDRZzb", // Must match a valid voice ID
          model_id: "eleven_multilingual_v2",
        };
        const response = await axios.post(`http://localhost:8003/tts`, body, {
          responseType: "arraybuffer",
        });
        // Convert to a Blob
        const audioBlob = new Blob([response.data], { type: "audio/mpeg" });
        const audioUrl = URL.createObjectURL(audioBlob);
        this.currentAudio = new Audio(audioUrl);

        this.setupAudioListeners(); // If you have timeupdate/ended, etc.
      } catch (err) {
        console.error("Error generating TTS for current chunk:", err);
      }
    },

    /**
     *  Preload the *next* chunk’s text/audio, storing it in `preloadedAudio`.
     */
    async preloadNextChunk() {
      const nextChunkId = this.chunkId + 1;
      if (nextChunkId > this.maxChunkId) {
        this.preloadedAudio = null;
        return;
      }

      try {
        // 1) Get the text
        const chunkRes = await axios.get(`http://localhost:8003/chunks/${nextChunkId}`);
        if (chunkRes.data.error) {
          console.warn("No chunk to preload:", chunkRes.data.error);
          return;
        }
        const nextChunkText = chunkRes.data.text;

        // 2) Request TTS audio
        const body = {
          text: nextChunkText,
          voice: "Brian", // use "Brian" consistently
          model: "eleven_multilingual_v2",
        };
        const audioRes = await axios.post("http://localhost:8003/tts", body, {
          responseType: "arraybuffer",
        });

        // 3) Convert audio to Blob and then to URL
        const audioBlob = new Blob([audioRes.data], { type: "audio/mpeg" });
        const audioUrl = URL.createObjectURL(audioBlob);

        // 4) Create an Audio object
        this.preloadedAudio = new Audio(audioUrl);
      } catch (err) {
        console.error("Failed to preload next chunk audio:", err);
      }
    },

    /**
     *  Setup event listeners (timeupdate, ended) on the *currentAudio*.
     */
    setupAudioListeners() {
      if (!this.currentAudio) return;

      // Remove existing listeners to avoid duplication if re-generating TTS
      this.currentAudio.removeEventListener("timeupdate", this.handleTimeUpdate);
      this.currentAudio.removeEventListener("ended", this.handleChunkEnded);

      this.currentAudio.addEventListener("timeupdate", this.handleTimeUpdate);
      this.currentAudio.addEventListener("ended", this.handleChunkEnded);
    },

    /**
     *  Called on each `timeupdate` event. If the user is near the end
     *  of the current chunk (e.g. 10s left) and we haven't preloaded
     *  the next chunk yet, do so now.
     */
    handleTimeUpdate() {
      if (!this.currentAudio || this.preloadTriggered) return;

      const duration = this.currentAudio.duration;
      const currentTime = this.currentAudio.currentTime;

      if (duration - currentTime <= 10) {
        this.preloadNextChunk();
        this.preloadTriggered = true; // Only do it once per chunk
      }
    },

    /**
     *  Called when the current chunk's audio finishes playing.
     *  We automatically proceed to the next chunk (if available).
     */
    handleChunkEnded() {
      this.isPlaying = false;
      // Reset preload trigger for next chunk
      this.preloadTriggered = false;

      // Auto-advance to next chunk if we can
      if (this.chunkId < this.maxChunkId) {
        this.goToNextChunk();
      } else {
        console.warn("No more chunks left!");
      }
    },

    /**
     *  Play the current chunk’s audio from the start.
     */
    async playCurrentChunk() {
      if (!this.currentChunkText) {
        console.warn("No chunk text loaded yet");
        return;
      }
      if (!this.currentAudio) {
        // If no TTS is generated yet, generate it now
        await this.generateTTSForCurrentChunk();
      }
      if (!this.currentAudio) {
        console.error("No currentAudio to play.");
        return;
      }

      try {
        this.isPlaying = true;
        await this.currentAudio.play();
        this.scrollText();
      } catch (err) {
        console.error("Error playing current chunk audio:", err);
        this.isPlaying = false;
      }
    },

    /**
     *  Pause the current audio.
     */
    pauseTTS() {
      if (this.isPlaying && this.currentAudio) {
        this.currentAudio.pause();
        this.isPlaying = false;
      }
    },

    /**
     *  Manually skip to the next chunk. If preloaded, we use that audio.
     */
    async goToNextChunk() {
      // Stop listening to old chunk's events
      if (this.currentAudio) {
        this.currentAudio.removeEventListener("timeupdate", this.handleTimeUpdate);
        this.currentAudio.removeEventListener("ended", this.handleChunkEnded);
        this.currentAudio.pause();
      }

      this.chunkId++;
      if (this.chunkId > this.maxChunkId) {
        console.warn("No more chunks left!");
        return;
      }

      // If we have preloaded audio, use it
      if (this.preloadedAudio) {
        this.currentAudio = this.preloadedAudio;
        this.preloadedAudio = null;

        // Also update chunk text
        const res = await axios.get(`http://localhost:8003/chunks/${this.chunkId}`);
        this.currentChunkText = res.data.text;
      } else {
        // fallback: load chunk & generate TTS
        await this.loadChunk(this.chunkId);
        await this.generateTTSForCurrentChunk();
      }

      this.preloadTriggered = false;
      // Preload the chunk after this one
      this.preloadNextChunk();
      // Start playing newly loaded chunk
      this.playCurrentChunk();
    },

    /**
     *  User can ask a question about the current chunk
     */
    async askQuestion() {
      if (!this.question.trim()) return;
      try {
        const body = {
          question: this.question,
          current_chunk: this.currentChunkText,
        };
        const res = await axios.post("http://localhost:8003/query", body);
        this.answer = res.data.answer;
      } catch (err) {
        console.error("Failed to query context:", err);
      }
    },

    /**
     *  Simple “Star Wars crawl” style auto-scrolling for dramatic effect.
     */
    scrollText() {
      const container = this.$refs.chunkContainer;
      if (!container) return;

      let step = 0;
      const scrollInterval = setInterval(() => {
        if (!this.isPlaying) {
          clearInterval(scrollInterval);
          return;
        }
        step += 1;
        container.scrollTop = step;

        if (step > container.scrollHeight - container.clientHeight) {
          clearInterval(scrollInterval);
        }
      }, 100);
    },
  },
};
</script>

<style scoped>
.book-reader {
  max-width: 600px;
  margin: 0 auto;
}

.controls {
  margin-bottom: 1em;
}

.chunk-container {
  background: #333;
  color: #fff;
  height: 200px;
  overflow-y: hidden; /* “movie intro” style hidden scrollbar */
  position: relative;
  border: 1px solid #aaa;
  padding: 1rem;
}

.highlight {
  font-weight: bold;
  color: #ffe900;
}

.query-box {
  margin-top: 1em;
}
</style>
