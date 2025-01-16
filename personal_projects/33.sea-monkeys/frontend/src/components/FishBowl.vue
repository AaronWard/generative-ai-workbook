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

// 1) Import RGBELoader for environment
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

export default defineComponent({
  name: "FishBowl",

  data() {
    return {
      seaMonkeyModel: null,
      seaMonkeyAnimations: null,
      agentMeshMap: {},
      mixerMap: {}, 
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

    // 2) For PBR materials, enable physically correct lighting, tone mapping, etc.
    this.renderer.physicallyCorrectLights = true;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;

    // 3) sRGB output encoding so texture colors look correct
    this.renderer.outputEncoding = THREE.sRGBEncoding; 

    this.initScene();
    this.loadEnvironment(); // <-- Load an HDR environment
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
      this.controls = markRaw(
        new OrbitControls(this.camera, this.renderer.domElement)
      );
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.minDistance = 10;
      this.controls.maxDistance = 200;

      // Basic lights (still helpful along with environment)
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

    // 4) Create a function to load an HDR environment
    loadEnvironment() {
      const pmremGenerator = new THREE.PMREMGenerator(this.renderer);
      pmremGenerator.compileEquirectangularShader();

      const rgbeLoader = new RGBELoader();
      // Provide your own .hdr file in public/envmaps/:
      const hdrPath = import.meta.env.BASE_URL + "envmaps/studio_small_08_hd.hdr";

      rgbeLoader.load(hdrPath, (texture) => {
        const envMap = pmremGenerator.fromEquirectangular(texture).texture;
        this.scene.environment = envMap;
        // Optional: scene.background = envMap;
        texture.dispose();
        pmremGenerator.dispose();
      });
    },

    loadSeaMonkeyModel() {
      return new Promise((resolve, reject) => {
        const loader = new GLTFLoader();
        const modelPath = import.meta.env.BASE_URL + "models/shadow_leviathan.glb";

        loader.load(
          modelPath,
          (gltf) => {
            const { scene, animations } = gltf;
            console.log("3D model loaded:", gltf);

            // If your model is authored with high metalness, you can clamp it down:
            scene.traverse((child) => {
              if (child.isMesh && child.material) {
                // Ensure map is in sRGB:
                if (child.material.map) {
                  child.material.map.encoding = THREE.sRGBEncoding;
                }

                // If still dark, override metalness or roughness:
                // child.material.metalness = 0;
                // child.material.roughness = 0.5;

                child.material.needsUpdate = true;
              }
            });

            this.seaMonkeyModel = markRaw(scene);
            this.seaMonkeyAnimations = animations;
            resolve();
          },
          (xhr) => {
            const progress = (xhr.loaded / xhr.total) * 100;
            console.log(`shadow_leviathan.glb loading: ${progress.toFixed(2)}%`);
          },
          (error) => {
            reject(error);
          }
        );
      });
    },

    startSimulationLoop() {
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

    updateAgents(agents) {
      agents.forEach(({ agent_id, position }) => {
        if (!this.agentMeshMap[agent_id]) {
          const clonedMonkey = markRaw(SkeletonUtils.clone(this.seaMonkeyModel));

          // Random initial rotation
          clonedMonkey.rotation.y = Math.random() * 2 * Math.PI;

          // Scale up
          clonedMonkey.scale.set(50, 50, 50);

          // Add to the scene
          this.scene.add(clonedMonkey);

          // If there are animations, create a mixer:
          if (this.seaMonkeyAnimations?.length) {
            const mixer = new THREE.AnimationMixer(clonedMonkey);
            const clip = this.seaMonkeyAnimations[0];
            const action = mixer.clipAction(clip);
            action.play();
            this.mixerMap[agent_id] = mixer;
          }

          this.agentMeshMap[agent_id] = clonedMonkey;
        }

        // Smooth movement with userData.targetPosition
        const mesh = this.agentMeshMap[agent_id];
        if (!mesh.userData.targetPosition) {
          mesh.userData.targetPosition = new THREE.Vector3(
            position.x,
            position.y,
            position.z
          );
        } else {
          mesh.userData.targetPosition.set(position.x, position.y, position.z);
        }
      });
    },

    animate() {
      this.animationId = requestAnimationFrame(this.animate);

      const delta = this.clock.getDelta();
      Object.keys(this.mixerMap).forEach((id) => {
        this.mixerMap[id].update(delta);
      });

      // Lerp toward target
      Object.values(this.agentMeshMap).forEach((mesh) => {
        if (mesh.userData.targetPosition) {
          mesh.position.lerp(mesh.userData.targetPosition, 0.1);
        }
      });

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
