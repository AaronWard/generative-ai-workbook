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
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

// Map agent action to an animation name from your .glb
const actionToClipName = {
  "StayStill": "SM_idle",
  "MoveForward": "SM_slowSwim",
  "TurnLeft": "SM_fastLeft_swim",
  "TurnRight": "SM_fastRight_swim",
  "MoveUp": "SM_fastUp_swim",
  "MoveDown": "SM_fastDown_swim"
};

export default defineComponent({
  name: "FishBowl",

  data() {
    return {
      seaMonkeyModel: null,
      seaMonkeyAnimations: null,

      // agent_id -> 3D object
      agentMeshMap: {},

      // agent_id -> AnimationMixer
      mixerMap: {},

      // agent_id -> currently playing action name
      actionMap: {},

      // NEW: Track the movement state for each agent so we can do smooth interpolation
      // agentMovementMap[agent_id] = { startPosition, endPosition, currentTime, duration }
      agentMovementMap: {},

      refreshIntervalId: null,
      animationId: null,
      clock: new THREE.Clock(),
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

    // PBR settings
    this.renderer.physicallyCorrectLights = true;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.renderer.outputEncoding = THREE.sRGBEncoding;

    this.initScene();
    this.loadEnvironment();
    this.loadSeaMonkeyModel()
      .then(() => {
        console.log("SeaMonkey .glb loaded. Starting animation loop...");
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
      this.controls = markRaw(
        new OrbitControls(this.camera, this.renderer.domElement)
      );
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.minDistance = 10;
      this.controls.maxDistance = 200;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
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

    loadEnvironment() {
      const pmremGenerator = new THREE.PMREMGenerator(this.renderer);
      pmremGenerator.compileEquirectangularShader();

      const rgbeLoader = new RGBELoader();
      const hdrPath = import.meta.env.BASE_URL + "envmaps/studio_small_08_hd.hdr";

      rgbeLoader.load(hdrPath, (texture) => {
        const envMap = pmremGenerator.fromEquirectangular(texture).texture;
        this.scene.environment = envMap;
        // this.scene.background = envMap; // optional
        texture.dispose();
        pmremGenerator.dispose();
      });
    },

    loadSeaMonkeyModel() {
      return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        const modelPath = import.meta.env.BASE_URL + "models/sea_monkey.glb";

        loader.load(
          modelPath,
          (gltf) => {
            const { scene, animations } = gltf;

            // Fix up materials
            scene.traverse((child) => {
              if (child.isMesh && child.material) {
                if (child.material.map) {
                  child.material.map.encoding = THREE.sRGBEncoding;
                }
                child.material.metalness = 0;
                child.material.roughness = 0.5;
                child.material.needsUpdate = true;
              }
            });

            this.seaMonkeyModel = markRaw(scene);
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
      // Poll the backend every 2 seconds
      this.refreshIntervalId = setInterval(async () => {
        try {
          // Step 1: trigger a simulation step on the backend
          await axios.post("http://localhost:8000/simulate");
          // Step 2: get updated agent states
          const res = await axios.get("http://localhost:8000/agents");
          this.updateAgents(res.data);
        } catch (err) {
          console.error("Error in simulation loop:", err);
        }
      }, 2000);
    },

    updateAgents(agents) {
      // For each agent returned by the backend:
      agents.forEach(({ agent_id, position, action }) => {

        // 1) Create a mesh if none exists yet
        if (!this.agentMeshMap[agent_id]) {
          const clonedMonkey = markRaw(SkeletonUtils.clone(this.seaMonkeyModel));
          clonedMonkey.scale.set(300, 300, 300);
          clonedMonkey.rotation.y = Math.random() * 2 * Math.PI;

          this.scene.add(clonedMonkey);

          // Prep an animation mixer
          const mixer = new THREE.AnimationMixer(clonedMonkey);
          this.mixerMap[agent_id] = mixer;

          this.agentMeshMap[agent_id] = clonedMonkey;
          this.actionMap[agent_id] = null;

          // Initialize the movement map so we don't jump on the first update
          this.agentMovementMap[agent_id] = {
            startPosition: new THREE.Vector3(position.x, position.y, position.z),
            endPosition: new THREE.Vector3(position.x, position.y, position.z),
            currentTime: 0,
            duration: 2.0, // match your backend refresh interval
          };

          // Place the object at the initial position
          clonedMonkey.position.copy(this.agentMovementMap[agent_id].startPosition);
        } else {
          // 2) Update the movement map for smooth interpolation
          const mesh = this.agentMeshMap[agent_id];
          const movement = this.agentMovementMap[agent_id];

          // The new cycle starts from wherever the mesh currently is
          movement.startPosition = mesh.position.clone();

          // The new position from the server
          movement.endPosition.set(position.x, position.y, position.z);

          // Reset the interpolation time
          movement.currentTime = 0;
          movement.duration = 2.0; // 2 seconds in between updates
        }

        // 3) If the agent's action changed, update the animation
        if (this.actionMap[agent_id] !== action) {
          this.playAnimation(agent_id, action);
          this.actionMap[agent_id] = action;
        }
      });
    },

    playAnimation(agent_id, agentAction) {
      const mixer = this.mixerMap[agent_id];
      if (!mixer || !this.seaMonkeyAnimations) return;

      const clipName = actionToClipName[agentAction] || "SM_idle";
      const clip = THREE.AnimationClip.findByName(this.seaMonkeyAnimations, clipName);

      if (!clip) {
        console.warn(`Could not find animation clip for ${clipName}, defaulting to idle`);
        return;
      }

      // Stop all ongoing actions
      mixer.stopAllAction();

      // Play the new clip
      const newAction = mixer.clipAction(clip);
      newAction.reset().play();
    },

    animate() {
      this.animationId = requestAnimationFrame(this.animate);
      const delta = this.clock.getDelta();

      // (A) Update all mixers
      Object.keys(this.mixerMap).forEach((id) => {
        this.mixerMap[id].update(delta);
      });

      // (B) Smoothly interpolate positions for each agent
      Object.keys(this.agentMeshMap).forEach((agent_id) => {
        const mesh = this.agentMeshMap[agent_id];
        const movement = this.agentMovementMap[agent_id];
        if (!movement) return;

        // Increase the elapsed time
        movement.currentTime += delta;

        // Calculate interpolation factor
        const t = Math.min(movement.currentTime / movement.duration, 1.0);

        // Lerp from start to end
        mesh.position.lerpVectors(movement.startPosition, movement.endPosition, t);
      });

      // (C) Update controls and render
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
