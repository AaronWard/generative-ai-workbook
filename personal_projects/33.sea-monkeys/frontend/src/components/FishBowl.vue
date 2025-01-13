<template>
  <!-- We only have a single <canvas> for the Three.js scene. -->
  <canvas ref="canvas"></canvas>
</template>

<script>
import { defineComponent, markRaw } from "vue";
import axios from "axios";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import * as SkeletonUtils from "three/examples/jsm/utils/SkeletonUtils.js";

export default defineComponent({
  name: "FishBowl",

  data() {
    return {
      // We'll store a reference to the loaded .glb (non-reactively).
      seaMonkeyModel: null,

      // agent_id -> cloned mesh
      agentMeshMap: {},

      // Interval & animation
      refreshIntervalId: null,
      animationId: null,
    };
  },

  mounted() {
    // 1) Create non-reactive references for scene, camera, renderer
    this.scene = markRaw(new THREE.Scene());
    this.camera = markRaw(
      new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      )
    );
    this.renderer = markRaw(
      new THREE.WebGLRenderer({
        canvas: this.$refs.canvas,
        antialias: true,
      })
    );
    this.controls = null; // define later

    // 2) Initialize the Three.js environment
    this.initScene();

    // 3) Load the .glb model, then start animate() + poll the API
    this.loadSeaMonkeyModel()
      .then(() => {
        console.log("SeaMonkey .glb loaded. Starting animation...");
        this.animate();
        console.log("Starting simulation loop (every 2s)...");
        this.startSimulationLoop();
      })
      .catch((err) => {
        console.error("Failed to load sea monkey .glb:", err);
      });
  },

  beforeUnmount() {
    // Cleanup intervals / event listeners
    if (this.animationId) cancelAnimationFrame(this.animationId);
    if (this.refreshIntervalId) clearInterval(this.refreshIntervalId);
    window.removeEventListener("resize", this.onWindowResize);
  },

  methods: {
    initScene() {
      // Position camera
      this.camera.position.set(0, 50, 100);
      this.camera.lookAt(this.scene.position);

      // Renderer
      this.renderer.setSize(window.innerWidth, window.innerHeight);

      // OrbitControls
      this.controls = markRaw(new OrbitControls(this.camera, this.renderer.domElement));
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.minDistance = 10;
      this.controls.maxDistance = 200;

      // Ambient + directional lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
      this.scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
      directionalLight.position.set(10, 10, 10);
      this.scene.add(directionalLight);

      // Fishbowl geometry (wireframe sphere of radius 50)
      const bowlGeometry = new THREE.SphereGeometry(50, 32, 32);
      const bowlMaterial = new THREE.MeshBasicMaterial({
        color: 0xadd8e6,
        wireframe: true,
        transparent: true,
        opacity: 0.25,
      });
      const fishBowl = new THREE.Mesh(bowlGeometry, bowlMaterial);
      this.scene.add(fishBowl);

      window.addEventListener("resize", this.onWindowResize);
    },

    /**
     * Loads the .glb sea monkey model from /public/models/sea_monkey.glb
     * Mark as non-reactive so Vue won't proxy it.
     */
    loadSeaMonkeyModel() {
      return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        const modelPath = import.meta.env.BASE_URL + "models/sea_monkey.glb";
        console.log("Loading sea_monkey from:", modelPath);

        loader.load(
          modelPath,
          (gltf) => {
            this.seaMonkeyModel = markRaw(gltf.scene);
            console.log("3D model loaded:", gltf);
            resolve();
          },
          (xhr) => {
            const progress = (xhr.loaded / xhr.total) * 100;
            console.log(`sea_monkey.glb loading: ${progress.toFixed(2)}%`);
          },
          (error) => {
            reject(error);
          }
        );
      });
    },

    /**
     * Calls /simulate then /agents every 2 seconds, updating agent positions in 3D.
     */
    startSimulationLoop() {
      this.refreshIntervalId = setInterval(async () => {
        try {
          console.log("[FishBowl] POST /simulate");
          await axios.post("http://localhost:8000/simulate");
          
          console.log("[FishBowl] GET /agents");
          const res = await axios.get("http://localhost:8000/agents");
          this.updateAgents(res.data);
        } catch (err) {
          console.error("Error in simulation loop:", err);
        }
      }, 2000);
    },

    /**
     * For each agent, clone or update a 3D sea monkey.
     */
    updateAgents(agents) {
      agents.forEach(({ agent_id, position }) => {
        // If we don't have a mesh for this agent yet, clone the .glb
        if (!this.agentMeshMap[agent_id]) {
          if (!this.seaMonkeyModel) {
            console.warn("seaMonkeyModel not loaded yet.");
            return;
          }
          // Clone
          const clonedMonkey = markRaw(SkeletonUtils.clone(this.seaMonkeyModel));

          // Scale the glb so we can see it in radius=50 bowl
          // If the bounding box is super small, try 50 or 100
          clonedMonkey.scale.set(50, 50, 50);

          // Optional: ensure pivot is at center if needed
          // e.g. if the model is offset

          // Add to the scene
          this.scene.add(clonedMonkey);

          // Save reference
          this.agentMeshMap[agent_id] = clonedMonkey;
        }

        // Update the position for this agent
        const mesh = this.agentMeshMap[agent_id];
        mesh.position.set(position.x, position.y, position.z);
      });

      // (Optional) remove meshes for agents that no longer exist
    },

    /**
     * The main Three.js rendering loop
     */
    animate() {
      this.animationId = requestAnimationFrame(this.animate);
      if (this.controls) {
        this.controls.update();
      }
      this.renderer.render(this.scene, this.camera);
    },

    onWindowResize() {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    },
  },
});
</script>

<style scoped>
canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
