<template>
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
      seaMonkeyModel: null,
      agentMeshMap: {},
      refreshIntervalId: null,
      animationId: null,

      // NEW: We'll store one or more mixers for animation:
      mixerMap: {}, // agent_id -> AnimationMixer

      clock: new THREE.Clock(), // needed for animation updates
    };
  },

  mounted() {
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

    this.initScene();
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
    if (this.animationId) cancelAnimationFrame(this.animationId);
    if (this.refreshIntervalId) clearInterval(this.refreshIntervalId);
    window.removeEventListener("resize", this.onWindowResize);
  },

  methods: {
    initScene() {
      // Camera
      this.camera.position.set(0, 50, 100);
      this.camera.lookAt(this.scene.position);

      // Renderer
      this.renderer.setSize(window.innerWidth, window.innerHeight);

      // Controls
      this.controls = markRaw(new OrbitControls(this.camera, this.renderer.domElement));
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.minDistance = 10;
      this.controls.maxDistance = 200;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
      this.scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
      directionalLight.position.set(10, 10, 10);
      this.scene.add(directionalLight);

      // Fishbowl geometry
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
     * and ensures it has materials/animations.
     */
    loadSeaMonkeyModel() {
      return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        const modelPath = import.meta.env.BASE_URL + "models/sea_monkey.glb";

        loader.load(
          modelPath,
          (gltf) => {
            // 1) Access the scene and animations
            const { scene, animations } = gltf;
            console.log("3D model loaded:", gltf);

            // 2) This ensures the materials are kept
            scene.traverse((child) => {
              if (child.isMesh) {
                // If you see a dull gray, you might need to tweak material settings:
                // e.g. child.material = new THREE.MeshStandardMaterial({ map: yourTexture });
                // But usually the glTF loader sets child.material automatically if textures are embedded.
                child.castShadow = true;
                child.receiveShadow = true;
              }
            });

            // 3) Save them as non-reactive
            this.seaMonkeyModel = markRaw(scene);
            // We'll also store the animations in case you need them:
            this.seaMonkeyAnimations = animations;

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

    startSimulationLoop() {
      // Poll the backend every 2s
      this.refreshIntervalId = setInterval(async () => {
        try {
          await axios.post("http://localhost:8000/simulate");
          const res = await axios.get("http://localhost:8000/agents");
          this.updateAgents(res.data);
        } catch (err) {
          console.error("Error in simulation loop:", err);
        }
      }, 2000);
    },

    /**
     * For each agent, clone or update a 3D sea monkey with materials & animations
     */
    updateAgents(agents) {
      agents.forEach(({ agent_id, position }) => {
        // If no mesh for this agent yet, clone from the seaMonkeyModel
        if (!this.agentMeshMap[agent_id]) {
          if (!this.seaMonkeyModel) {
            console.warn("seaMonkeyModel not loaded yet.");
            return;
          }

          const clonedMonkey = markRaw(SkeletonUtils.clone(this.seaMonkeyModel));
          // Scale up if needed
          clonedMonkey.scale.set(300, 300, 300);

          // Add to scene
          this.scene.add(clonedMonkey);

          // Create a new AnimationMixer *if* we have animations
          if (this.seaMonkeyAnimations && this.seaMonkeyAnimations.length > 0) {
            const mixer = new THREE.AnimationMixer(clonedMonkey);

            // Start playing the *first* animation
            // (If your model has multiple animations, you might pick which to play)
            const clip = this.seaMonkeyAnimations[0];
            const action = mixer.clipAction(clip);
            action.play();

            this.mixerMap[agent_id] = mixer;
          }

          // Save reference
          this.agentMeshMap[agent_id] = clonedMonkey;
        }

        // Update position
        const mesh = this.agentMeshMap[agent_id];
        mesh.position.set(position.x, position.y, position.z);
      });
    },

    /**
     * The main Three.js render loop
     */
    animate() {
      this.animationId = requestAnimationFrame(this.animate);

      // 1) Update all mixers
      const delta = this.clock.getDelta();
      Object.keys(this.mixerMap).forEach((id) => {
        this.mixerMap[id].update(delta);
      });

      // 2) Update controls
      if (this.controls) {
        this.controls.update();
      }

      // 3) Render scene
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
